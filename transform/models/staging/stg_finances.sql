with source as (

    select * from {{ source('raw', 'finances') }}

),

-- The loader stored each transaction as JSON text; turn it back into JSON
parsed as (

    select
        parse_json(payload:transaction::string)     as txn,
        _source_file,
        _file_row_number,
        _dt,
        _loaded_at

    from source

),

-- relatedIdentifiers is a list of {name, value} pairs; unpack it and keep the ids we need
identifiers as (

    select
        parsed.txn:transactionId::string as transaction_id,
        max(case when ids.value:relatedIdentifierName::string = 'ORDER_ID'
                 then ids.value:relatedIdentifierValue::string end)                 as amazon_order_id,
        max(case when ids.value:relatedIdentifierName::string = 'SETTLEMENT_ID'
                 then ids.value:relatedIdentifierValue::string end)                 as settlement_id,
        max(case when ids.value:relatedIdentifierName::string = 'FINANCIAL_EVENT_GROUP_ID'
                 then ids.value:relatedIdentifierValue::string end)                 as financial_event_group_id

    from parsed,
        lateral flatten(input => parsed.txn:relatedIdentifiers) as ids

    group by 1

),

renamed as (

    select
        -- ids
        parsed.txn:transactionId::string                        as transaction_id,
        identifiers.amazon_order_id,
        identifiers.settlement_id,
        identifiers.financial_event_group_id,

        -- transaction
        parsed.txn:transactionType::string                      as transaction_type,
        parsed.txn:transactionStatus::string                    as transaction_status,
        parsed.txn:description::string                          as description,
        try_to_timestamp_tz(parsed.txn:postedDate::string)      as posted_at,
        parsed.txn:marketplaceDetails:marketplaceId::string     as marketplace_id,

        -- money
        parsed.txn:totalAmount:currencyCode::string             as currency,
        parsed.txn:totalAmount:currencyAmount::number(12, 2)    as total_amount,

        -- nested detail kept as JSON for later models (fees per item)
        parsed.txn:breakdowns                                   as breakdowns,
        parsed.txn:items                                        as items,

        -- load metadata
        parsed._source_file,
        parsed._file_row_number,
        parsed._dt,
        parsed._loaded_at

    from parsed
    left join identifiers
        on parsed.txn:transactionId::string = identifiers.transaction_id

)

select * from renamed
