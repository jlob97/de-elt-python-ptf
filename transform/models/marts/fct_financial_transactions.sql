{{
    config(
        materialized='incremental',
        unique_key='transaction_id',
        incremental_strategy='merge'
    )
}}

-- One row per financial transaction (order payment, refund, fee),
-- with the sales side and Amazon's expenses side split out.
-- Incremental: each run re-processes the last 30 days (the extractor's lookback),
-- so a held transaction that Amazon later releases gets its new status merged in.

with transactions as (

    select * from {{ ref('stg_finances') }}

    {% if is_incremental() %}
    where posted_at >= (
        select dateadd(day, -30, max(posted_at)) from {{ this }}
    )
    {% endif %}

    qualify row_number() over (
        partition by transaction_id
        order by _loaded_at desc, _source_file desc
    ) = 1

),

-- breakdowns is a list like [{Sales: 56.99}, {Expenses: -12.40}]; add up each side
breakdowns as (

    select
        transactions.transaction_id,
        sum(iff(parts.value:breakdownType::string in ('Sales', 'Refunded Sales'),
                parts.value:breakdownAmount:currencyAmount::number(12, 2), 0))     as sales_amount,
        sum(iff(parts.value:breakdownType::string in ('Expenses', 'Refunded Expenses'),
                parts.value:breakdownAmount:currencyAmount::number(12, 2), 0))     as expenses_amount

    from transactions,
        lateral flatten(input => transactions.breakdowns) as parts

    group by transactions.transaction_id

)

select
    -- ids
    transactions.transaction_id,
    transactions.amazon_order_id,
    transactions.settlement_id,
    transactions.financial_event_group_id,

    -- transaction
    transactions.transaction_type,
    transactions.transaction_status,
    transactions.description,
    transactions.posted_at,
    transactions.posted_at::date                    as posted_date,
    transactions.marketplace_id,

    -- money
    transactions.currency,
    coalesce(breakdowns.sales_amount, 0)            as sales_amount,
    coalesce(breakdowns.expenses_amount, 0)         as expenses_amount,
    transactions.total_amount

from transactions
left join breakdowns
    on transactions.transaction_id = breakdowns.transaction_id
