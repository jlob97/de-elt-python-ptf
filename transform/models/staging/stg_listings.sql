with source as (

    select * from {{ source('raw', 'listings') }}

),

renamed as (

    select
        -- ids
        payload:"seller-sku"::string                                as sku,
        payload:"listing-id"::string                                as listing_id,
        payload:"asin1"::string                                     as asin,

        -- snapshot date (one full copy of the listings per day)
        _dt                                                         as snapshot_date,

        -- listing details
        payload:"item-name"::string                                 as item_name,
        payload:"status"::string                                    as listing_status,
        payload:"fulfillment-channel"::string                       as fulfillment_channel,
        payload:"item-condition"::string                            as item_condition_code,
        try_to_number(payload:"price"::string, 12, 2)               as price,
        try_to_number(payload:"quantity"::string)                   as quantity,
        try_to_number(payload:"pending-quantity"::string)           as pending_quantity,

        -- open-date looks like '2019-08-23 12:24:07 PDT': read it as Pacific time, store as UTC
        convert_timezone(
            'America/Los_Angeles',
            'UTC',
            try_to_timestamp_ntz(left(payload:"open-date"::string, 19))
        )                                                           as opened_at_utc,

        -- load metadata
        _source_file,
        _file_row_number,
        _dt,
        _loaded_at

    from source

)

select * from renamed
