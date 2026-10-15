select
    i.invoice_id,
    i.amount as invoice_amount,
    o.revenue as order_revenue
from {{ ref('stg_invoices') }} i
join {{ ref('sales_orders') }} o using (order_id)
where abs(i.amount - o.revenue) > 0.01

