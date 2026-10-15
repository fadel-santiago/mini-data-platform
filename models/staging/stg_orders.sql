select
    order_id,
    customer_id,
    order_date,
    lower(status) as status,
    lower(channel) as channel,
    updated_at
from {{ source('raw', 'orders') }}

