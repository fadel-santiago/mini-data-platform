select
    invoice_id,
    order_id,
    issued_date,
    due_date,
    paid_date,
    amount,
    lower(status) as status,
    updated_at
from {{ source('raw', 'invoices') }}

