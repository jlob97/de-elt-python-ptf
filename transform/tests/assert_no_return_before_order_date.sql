-- A unit cannot be returned before it was ordered.
-- Only checks returns where the order date is known.

select
    return_id,
    amazon_order_id,
    order_date,
    return_date

from {{ ref('fct_returns') }}
where order_date is not null
  and return_date < order_date
