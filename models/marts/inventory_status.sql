select
    product_id,
    product_name,
    category,
    stock_quantity,
    reorder_point,
    unit_cost,
    stock_quantity * unit_cost as inventory_value,
    case
        when stock_quantity = 0 then 'rupture'
        when stock_quantity <= reorder_point then 'a_reapprovisionner'
        else 'sain'
    end as stock_status,
    greatest(reorder_point * 2 - stock_quantity, 0) as suggested_reorder_quantity,
    updated_at
from {{ ref('stg_inventory') }}

