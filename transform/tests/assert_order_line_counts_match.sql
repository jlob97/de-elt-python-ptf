-- Reconciliation: every order line in staging must come out of the dedupe exactly once,
-- and the mart must not gain or lose rows in its joins.
-- Returns a row (= fails) when the three counts are not all equal.

with staging as (

    select count(distinct amazon_order_id, order_item_id) as order_lines
    from {{ ref('stg_order_items') }}

),

intermediate as (

    select count(*) as order_lines
    from {{ ref('int_order_items_latest') }}

),

mart as (

    select count(*) as order_lines
    from {{ ref('fct_order_items') }}

)

select
    staging.order_lines         as staging_order_lines,
    intermediate.order_lines    as intermediate_order_lines,
    mart.order_lines            as mart_order_lines

from staging
cross join intermediate
cross join mart
where staging.order_lines != intermediate.order_lines
   or intermediate.order_lines != mart.order_lines
