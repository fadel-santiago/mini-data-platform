select *
from {{ ref('stg_order_lines') }}
where quantity <= 0

