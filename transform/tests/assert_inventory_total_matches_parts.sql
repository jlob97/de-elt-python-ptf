-- FBA total quantity should equal the sum of its parts.
-- Amazon's total does not include units under research, so they are left out.
-- The test fails (here: warns) for every SKU where it does not add up.

{{ config(severity='warn') }}

select
    sku,
    snapshot_date,
    total_quantity,
    fulfillable_quantity
        + inbound_working_quantity
        + inbound_shipped_quantity
        + inbound_receiving_quantity
        + reserved_quantity
        + unfulfillable_quantity    as sum_of_parts

from {{ ref('stg_inventory') }}
where total_quantity != sum_of_parts
