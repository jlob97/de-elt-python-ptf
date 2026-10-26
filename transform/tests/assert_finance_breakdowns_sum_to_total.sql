-- The sales side plus the expenses side must add up to the transaction total.

select
    transaction_id,
    sales_amount,
    expenses_amount,
    total_amount

from {{ ref('fct_financial_transactions') }}
where abs(sales_amount + expenses_amount - total_amount) > 0.01
