-- One row per SKU: the latest listing details plus the latest FBA inventory.

with listings as (

    select * from {{ ref('stg_listings') }}
    qualify row_number() over (
        partition by sku
        order by snapshot_date desc, _loaded_at desc, _source_file desc
    ) = 1

),

inventory as (

    select * from {{ ref('stg_inventory') }}
    qualify row_number() over (
        partition by sku
        order by snapshot_date desc, _loaded_at desc, _source_file desc
    ) = 1

),

-- A SKU can be in listings only (FBM), in inventory only (old FBA SKUs), or in both
final as (

    select
        -- ids
        coalesce(listings.sku, inventory.sku)                       as sku,
        coalesce(listings.asin, inventory.asin)                     as asin,
        inventory.fnsku,
        listings.listing_id,

        -- product
        coalesce(listings.item_name, inventory.product_name)        as product_name,
        listings.listing_status,
        listings.fulfillment_channel,
        listings.price,
        listings.opened_at_utc,

        -- stock
        listings.quantity                                           as fbm_quantity,
        inventory.fulfillable_quantity                              as fba_fulfillable_quantity,
        inventory.inbound_working_quantity
            + inventory.inbound_shipped_quantity
            + inventory.inbound_receiving_quantity                  as fba_inbound_quantity,
        inventory.total_quantity                                    as fba_total_quantity,

        -- where each side came from
        listings.sku is not null                                    as is_in_listings,
        inventory.sku is not null                                   as is_in_fba_inventory,
        listings.snapshot_date                                      as listing_snapshot_date,
        inventory.snapshot_date                                     as inventory_snapshot_date

    from listings
    full outer join inventory
        on listings.sku = inventory.sku

)

select * from final
