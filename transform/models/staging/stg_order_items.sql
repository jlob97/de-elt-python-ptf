with source as (

    select * from {{ source('raw', 'order_items') }}

),

renamed as (

    select
        -- ids
        payload:"amazon-order-id"::string                           as amazon_order_id,
        payload:"order-item-id"::string                             as order_item_id,
        nullif(payload:"merchant-order-id"::string, '')             as merchant_order_id,

        -- dates (UTC)
        try_to_timestamp_tz(payload:"purchase-date"::string)        as purchased_at,
        try_to_timestamp_tz(payload:"last-updated-date"::string)    as last_updated_at,

        -- status and channel
        payload:"order-status"::string                              as order_status,
        nullif(payload:"item-status"::string, '')                   as item_status,
        payload:"fulfillment-channel"::string                       as fulfillment_channel,
        payload:"sales-channel"::string                             as sales_channel,
        nullif(payload:"ship-service-level"::string, '')            as ship_service_level,

        -- product
        payload:"sku"::string                                       as sku,
        payload:"asin"::string                                      as asin,
        payload:"product-name"::string                              as product_name,

        -- amounts
        try_to_number(payload:"quantity"::string)                   as quantity,
        nullif(payload:"currency"::string, '')                      as currency,
        try_to_number(payload:"item-price"::string, 12, 2)          as item_price,
        try_to_number(payload:"item-tax"::string, 12, 2)            as item_tax,
        try_to_number(payload:"shipping-price"::string, 12, 2)      as shipping_price,
        try_to_number(payload:"shipping-tax"::string, 12, 2)        as shipping_tax,
        try_to_number(payload:"gift-wrap-price"::string, 12, 2)     as gift_wrap_price,
        try_to_number(payload:"gift-wrap-tax"::string, 12, 2)       as gift_wrap_tax,
        try_to_number(payload:"item-promotion-discount"::string, 12, 2) as item_promotion_discount,
        try_to_number(payload:"ship-promotion-discount"::string, 12, 2) as ship_promotion_discount,

        -- flags
        try_to_boolean(payload:"is-business-order"::string)         as is_business_order,
        try_to_boolean(payload:"is-prime"::string)                  as is_prime,
        try_to_boolean(payload:"is-replacement-order"::string)      as is_replacement_order,

        -- ship to
        nullif(payload:"ship-city"::string, '')                     as ship_city,
        nullif(payload:"ship-state"::string, '')                    as ship_state,
        nullif(payload:"ship-postal-code"::string, '')              as ship_postal_code,
        nullif(payload:"ship-country"::string, '')                  as ship_country,

        -- load metadata
        _source_file,
        _file_row_number,
        _dt,
        _loaded_at

    from source

)

select * from renamed
where sales_channel = 'Amazon.com'