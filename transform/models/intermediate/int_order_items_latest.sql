with order_items as (

    select * from {{ ref('stg_order_items') }}

)

select *
from order_items
qualify row_number() over (
    partition by amazon_order_id, order_item_id
    order by last_updated_at desc, _loaded_at desc, _source_file desc
) = 1

--Window function to get an "order_items_mst" of the most recent status of each item in an orderd.