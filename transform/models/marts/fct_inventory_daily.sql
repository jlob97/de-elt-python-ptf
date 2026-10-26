-- One row per SKU per day of FBA inventory (one snapshot per day).

with inventory as (

    select * from {{ ref('stg_inventory') }}
    qualify row_number() over (
        partition by sku, snapshot_date
        order by _loaded_at desc, _source_file desc
    ) = 1

)

select
    snapshot_date,
    sku,
    fnsku,
    asin,

    -- quantities
    fulfillable_quantity,
    inbound_working_quantity
        + inbound_shipped_quantity
        + inbound_receiving_quantity                as inbound_quantity,
    reserved_quantity,
    unfulfillable_quantity,
    researching_quantity,
    total_quantity,
    fulfillable_quantity > 0                        as is_in_stock

from inventory
