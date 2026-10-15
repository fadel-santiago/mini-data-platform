select
    product_id,
    trim(product_name) as product_name,
    lower(category) as category,
    stock_quantity,
    reorder_point,
    unit_cost,
    updated_at
from {{ source('raw', 'inventory') }}

