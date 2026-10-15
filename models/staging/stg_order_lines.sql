select
    order_id,
    line_id,
    product_id,
    quantity,
    unit_price,
    unit_cost,
    quantity * unit_price as line_revenue,
    quantity * unit_cost as line_cost,
    quantity * (unit_price - unit_cost) as line_margin,
    updated_at
from {{ source('raw', 'order_lines') }}

