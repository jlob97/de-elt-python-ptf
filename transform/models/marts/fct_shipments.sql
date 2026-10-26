-- One row per item shipped by Amazon (FBA), US only.

with shipments as (

    select * from {{ ref('stg_shipments') }}
    qualify row_number() over (
        partition by shipment_item_id
        order by _loaded_at desc, _source_file desc
    ) = 1

)

select
    -- ids
    shipment_item_id,
    shipment_id,
    amazon_order_id,
    order_item_id,
    sku,
    buyer_email_hash,

    -- dates (UTC)
    purchased_at,
    shipped_at,
    shipped_at::date                                as ship_date,
    estimated_arrival_at,
    datediff('hour', purchased_at, shipped_at)      as hours_to_ship,

    -- fulfillment
    fulfillment_center_id,
    ship_service_level,
    carrier,

    -- amounts (discounts are negative in this report)
    quantity_shipped,
    currency,
    item_price,
    item_tax,
    shipping_price,
    shipping_tax,
    item_promotion_discount,
    ship_promotion_discount,

    -- ship to (no street or postal code in marts)
    ship_city,
    ship_state,
    ship_country

from shipments
