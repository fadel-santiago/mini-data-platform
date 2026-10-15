select
    i.invoice_id,
    i.order_id,
    o.customer_id,
    o.company_name,
    o.region,
    i.issued_date,
    i.due_date,
    i.paid_date,
    i.amount,
    i.status,
    case
        when i.status = 'paid' then greatest(i.paid_date - i.due_date, 0)
        else greatest(current_date - i.due_date, 0)
    end as days_late,
    case
        when i.status <> 'paid' and current_date > i.due_date then i.amount
        else 0
    end as overdue_amount
from {{ ref('stg_invoices') }} i
join {{ ref('sales_orders') }} o using (order_id)

