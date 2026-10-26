with source as (

    select * from {{ source('raw', 'shipments') }}

),

renamed as (

    select
        -- ids
        payload:"shipment-item-id"::string                              as shipment_item_id,
        payload:"shipment-id"::string                                   as shipment_id,
        payload:"amazon-order-id"::string                               as amazon_order_id,
        payload:"amazon-order-item-id"::string                          as order_item_id,

        -- buyer (email is hashed here; the plain value stays in RAW)
        sha2(lower(trim(nullif(payload:"buyer-email"::string, ''))))    as buyer_email_hash,

        -- dates (UTC)
        try_to_timestamp_tz(payload:"purchase-date"::string)            as purchased_at,
        try_to_timestamp_tz(payload:"payments-date"::string)            as paid_at,
        try_to_timestamp_tz(payload:"shipment-date"::string)            as shipped_at,
        try_to_timestamp_tz(payload:"reporting-date"::string)           as reported_at,
        try_to_timestamp_tz(payload:"estimated-arrival-date"::string)   as estimated_arrival_at,

        -- channel and fulfillment
        payload:"sales-channel"::string                                 as sales_channel,
        payload:"fulfillment-channel"::string                           as fulfillment_channel,
        payload:"fulfillment-center-id"::string                         as fulfillment_center_id,
        payload:"ship-service-level"::string                            as ship_service_level,
        payload:"carrier"::string                                       as carrier,
        payload:"tracking-number"::string                               as tracking_number,

        -- product
        payload:"sku"::string                                           as sku,
        payload:"product-name"::string                                  as product_name,
        try_to_number(payload:"quantity-shipped"::string)               as quantity_shipped,

        -- amounts (discounts come as negative numbers in this report)
        payload:"currency"::string                                      as currency,
        try_to_number(payload:"item-price"::string, 12, 2)              as item_price,
        try_to_number(payload:"item-tax"::string, 12, 2)                as item_tax,
        try_to_number(payload:"shipping-price"::string, 12, 2)          as shipping_price,
        try_to_number(payload:"shipping-tax"::string, 12, 2)            as shipping_tax,
        try_to_number(payload:"gift-wrap-price"::string, 12, 2)         as gift_wrap_price,
        try_to_number(payload:"gift-wrap-tax"::string, 12, 2)           as gift_wrap_tax,
        try_to_number(payload:"item-promotion-discount"::string, 12, 2) as item_promotion_discount,
        try_to_number(payload:"ship-promotion-discount"::string, 12, 2) as ship_promotion_discount,

        -- ship to
        payload:"ship-city"::string                                     as ship_city,
        payload:"ship-state"::string                                    as ship_state,
        payload:"ship-postal-code"::string                              as ship_postal_code,
        payload:"ship-country"::string                                  as ship_country,

        -- load metadata
        _source_file,
        _file_row_number,
        _dt,
        _loaded_at

    from source

)

select * from renamed
where sales_channel = 'amazon.com'