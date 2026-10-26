{{
    config(
        materialized='incremental',
        unique_key='order_item_id',
        incremental_strategy='merge'
    )
}}

-- One row per US order line (latest version).
-- Incremental: each run only re-processes lines updated in the last 3 days
-- and merges them in, because Amazon keeps changing the status (Pending -> Shipped).
-- Returns are not here: they arrive weeks later and live in fct_returns.

with order_items as (

    select * from {{ ref('int_order_items_latest') }}

    {% if is_incremental() %}
    where last_updated_at >= (
        select dateadd(day, -3, max(last_updated_at)) from {{ this }}
    )
    {% endif %}

)

select
    -- ids
    amazon_order_id,
    order_item_id,
    sku,
    asin,

    -- dates (UTC)
    purchased_at,
    purchased_at::date                              as purchase_date,
    last_updated_at,

    -- status
    order_status,
    item_status,
    order_status = 'Cancelled'                      as is_cancelled,
    fulfillment_channel,
    is_business_order,

    -- amounts
    quantity,
    currency,
    item_price,
    item_tax,
    shipping_price,
    item_promotion_discount,
    ship_promotion_discount,

    -- ship to
    ship_state,
    ship_country

from order_items
