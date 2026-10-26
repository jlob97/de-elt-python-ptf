with source as (

    select * from {{ source('raw', 'inventory') }}

),

-- The loader stored each inventory summary as JSON text; turn it back into JSON
parsed as (

    select
        parse_json(payload:summary::string)     as summary,
        _source_file,
        _file_row_number,
        _dt,
        _loaded_at

    from source

),

renamed as (

    select
        -- ids
        summary:sellerSku::string                                               as sku,
        summary:fnSku::string                                                   as fnsku,
        summary:asin::string                                                    as asin,

        -- snapshot date (one full copy of FBA inventory per day)
        _dt                                                                     as snapshot_date,

        -- product
        summary:productName::string                                             as product_name,
        summary:condition::string                                               as item_condition,
        try_to_timestamp_tz(summary:lastUpdatedTime::string)                    as last_updated_at,

        -- quantities
        summary:totalQuantity::number                                           as total_quantity,
        summary:inventoryDetails:fulfillableQuantity::number                    as fulfillable_quantity,
        summary:inventoryDetails:inboundWorkingQuantity::number                 as inbound_working_quantity,
        summary:inventoryDetails:inboundShippedQuantity::number                 as inbound_shipped_quantity,
        summary:inventoryDetails:inboundReceivingQuantity::number               as inbound_receiving_quantity,
        summary:inventoryDetails:reservedQuantity:totalReservedQuantity::number as reserved_quantity,
        summary:inventoryDetails:unfulfillableQuantity:totalUnfulfillableQuantity::number as unfulfillable_quantity,
        summary:inventoryDetails:researchingQuantity:totalResearchingQuantity::number     as researching_quantity,

        -- load metadata
        _source_file,
        _file_row_number,
        _dt,
        _loaded_at

    from parsed

)

select * from renamed
