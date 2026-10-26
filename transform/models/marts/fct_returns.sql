-- One row per return line: FBA returns (sent back to an Amazon warehouse)
-- and MFN returns (orders we shipped ourselves) in one table.

with fba_returns as (

    select * from {{ ref('stg_fba_returns') }}
    qualify row_number() over (
        partition by license_plate_number
        order by _loaded_at desc, _source_file desc
    ) = 1

),

mfn_returns as (

    select * from {{ ref('stg_mfn_returns') }}
    qualify row_number() over (
        partition by amazon_rma_id, order_item_id
        order by _loaded_at desc, _source_file desc
    ) = 1

),

-- The FBA report has no order date, so take it from the orders we have loaded
order_dates as (

    select
        amazon_order_id,
        min(purchased_at)::date             as order_date

    from {{ ref('int_order_items_latest') }}
    group by amazon_order_id

),

returns_unioned as (

    select
        'FBA-' || license_plate_number      as return_id,
        'FBA'                               as return_channel,
        amazon_order_id,
        null::string                        as order_item_id,
        sku,
        asin,
        product_name,
        returned_at::date                   as return_date,
        null::date                          as order_date,
        quantity                            as return_quantity,
        return_reason,
        return_status,
        detailed_disposition,
        fulfillment_center_id,
        null::number(12, 2)                 as refunded_amount,
        null::number(12, 2)                 as label_cost

    from fba_returns

    union all

    select
        'MFN-' || amazon_rma_id || '-' || order_item_id as return_id,
        'MFN'                               as return_channel,
        amazon_order_id,
        order_item_id,
        sku,
        asin,
        product_name,
        return_request_date                 as return_date,
        order_date,
        return_quantity,
        return_reason,
        return_status,
        null::string                        as detailed_disposition,
        null::string                        as fulfillment_center_id,
        refunded_amount,
        label_cost

    from mfn_returns

),

final as (

    select
        returns_unioned.return_id,
        returns_unioned.return_channel,
        returns_unioned.amazon_order_id,
        returns_unioned.order_item_id,
        returns_unioned.sku,
        returns_unioned.asin,
        returns_unioned.product_name,
        returns_unioned.return_date,
        coalesce(returns_unioned.order_date, order_dates.order_date)   as order_date,
        returns_unioned.return_quantity,
        returns_unioned.return_reason,
        returns_unioned.return_status,
        returns_unioned.detailed_disposition,
        returns_unioned.fulfillment_center_id,
        returns_unioned.refunded_amount,
        returns_unioned.label_cost

    from returns_unioned
    left join order_dates
        on returns_unioned.amazon_order_id = order_dates.amazon_order_id

    -- Amazon.com.mx order ids start with 70 (US ones with 11); the FBA report mixes a few in
    where returns_unioned.amazon_order_id not like '70%'

)

select * from final
