-- The listings as of the most recent daily snapshot: one row per SKU.
-- Feeds the listings snapshot (SCD2), which needs exactly one row per SKU.

with listings as (

    select * from {{ ref('stg_listings') }}

)

select *
from listings
where snapshot_date = (select max(snapshot_date) from listings)
qualify row_number() over (
    partition by sku
    order by _loaded_at desc, _source_file desc
) = 1
