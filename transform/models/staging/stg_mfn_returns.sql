with source as (

    select * from {{ source('raw', 'mfn_returns') }}

),

renamed as (

    select
        -- ids
        payload:"Amazon RMA ID"::string                                 as amazon_rma_id,
        payload:"Order ID"::string                                      as amazon_order_id,
        payload:"Order Item ID"::string                                 as order_item_id,
        nullif(trim(payload:"Tracking ID"::string), '')                 as return_tracking_id,

        -- dates (report gives dates like 02-Oct-2026, no time)
        try_to_date(payload:"Order date"::string, 'DD-MON-YYYY')        as order_date,
        try_to_date(payload:"Return request date"::string, 'DD-MON-YYYY')  as return_request_date,
        try_to_date(payload:"Return delivery date"::string, 'DD-MON-YYYY') as return_delivery_date,

        -- product
        payload:"Merchant SKU"::string                                  as sku,
        payload:"ASIN"::string                                          as asin,
        payload:"Item Name"::string                                     as product_name,

        -- return details
        try_to_number(payload:"Order quantity"::string)                 as order_quantity,
        try_to_number(payload:"Return quantity"::string)                as return_quantity,
        payload:"Return Reason"::string                                 as return_reason,
        payload:"Return request status"::string                         as return_status,
        payload:"Return type"::string                                   as return_type,
        payload:"Resolution"::string                                    as resolution,
        try_to_boolean(payload:"In policy"::string)                     as is_in_policy,
        try_to_boolean(payload:"A-to-Z Claim"::string)                  as is_a_to_z_claim,
        try_to_boolean(payload:"Is prime"::string)                      as is_prime,

        -- money
        payload:"Currency code"::string                                 as currency,
        try_to_number(payload:"Order Amount"::string, 12, 2)            as order_amount,
        try_to_number(payload:"Refunded Amount"::string, 12, 2)         as refunded_amount,

        -- return label
        nullif(trim(payload:"Return carrier"::string), '')              as return_carrier,
        nullif(trim(payload:"Label type"::string), '')                  as label_type,
        nullif(trim(payload:"Label to be paid by"::string), '')         as label_paid_by,
        try_to_number(payload:"Label cost"::string, 12, 2)              as label_cost,

        -- load metadata
        _source_file,
        _file_row_number,
        _dt,
        _loaded_at

    from source

)

select * from renamed