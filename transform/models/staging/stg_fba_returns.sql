with source as (

    select * from {{ source('raw', 'fba_returns') }}

),

renamed as (

    select
        -- ids
        payload:"license-plate-number"::string                  as license_plate_number,
        payload:"order-id"::string                              as amazon_order_id,

        -- dates (UTC)
        try_to_timestamp_tz(payload:"return-date"::string)      as returned_at,

        -- product
        payload:"sku"::string                                   as sku,
        payload:"asin"::string                                  as asin,
        payload:"fnsku"::string                                 as fnsku,
        payload:"product-name"::string                          as product_name,

        -- return details
        try_to_number(payload:"quantity"::string)               as quantity,
        payload:"fulfillment-center-id"::string                 as fulfillment_center_id,
        payload:"detailed-disposition"::string                  as detailed_disposition,
        payload:"reason"::string                                as return_reason,
        payload:"status"::string                                as return_status,

        -- load metadata
        _source_file,
        _file_row_number,
        _dt,
        _loaded_at

    from source

)

select * from renamed