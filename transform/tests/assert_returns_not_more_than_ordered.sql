-- An order cannot have more units of a SKU returned than were ordered.
-- Checked per order + sku, because FBA returns have no order_item_id.
-- Only returns whose order is loaded are checked.

{{ config(severity='warn') }}

with ordered as (

    select
        amazon_order_id,
        sku,
        sum(quantity)           as ordered_quantity

    from {{ ref('fct_order_items') }}
    group by amazon_order_id, sku

),

returned as (

    select
        amazon_order_id,
        sku,
        sum(return_quantity)    as returned_quantity

    from {{ ref('fct_returns') }}
    group by amazon_order_id, sku

)

select
    returned.amazon_order_id,
    returned.sku,
    ordered.ordered_quantity,
    returned.returned_quantity

from returned
inner join ordered
    on  returned.amazon_order_id = ordered.amazon_order_id
    and returned.sku = ordered.sku
where returned.returned_quantity > ordered.ordered_quantity
