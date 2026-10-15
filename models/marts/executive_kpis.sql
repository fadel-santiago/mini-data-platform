select
    (select coalesce(sum(revenue), 0) from {{ ref('sales_orders') }}) as total_revenue,
    (select coalesce(sum(gross_margin), 0) from {{ ref('sales_orders') }}) as gross_margin,
    (select coalesce(round(sum(gross_margin) / nullif(sum(revenue), 0) * 100, 2), 0) from {{ ref('sales_orders') }}) as margin_rate,
    (select count(distinct customer_id) from {{ ref('sales_orders') }}) as active_customers,
    (select coalesce(sum(amount), 0) from {{ ref('accounts_receivable') }} where status <> 'paid') as open_receivables,
    (select coalesce(sum(overdue_amount), 0) from {{ ref('accounts_receivable') }}) as overdue_receivables,
    (select count(*) from {{ ref('accounts_receivable') }} where overdue_amount > 0) as overdue_invoices,
    (select count(*) from {{ ref('inventory_status') }} where stock_status = 'rupture') as stockouts,
    (select count(*) from {{ ref('inventory_status') }} where stock_status = 'a_reapprovisionner') as low_stock_products,
    (select coalesce(sum(inventory_value), 0) from {{ ref('inventory_status') }}) as inventory_value,
    current_timestamp as refreshed_at

