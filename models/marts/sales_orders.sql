with order_amounts as (
    select
        order_id,
        sum(line_revenue) as revenue,
        sum(line_cost) as cost_of_goods,
        sum(line_margin) as gross_margin,
        sum(quantity) as units_sold
    from {{ ref('stg_order_lines') }}
    group by order_id
)

select
    o.order_id,
    o.order_date,
    o.status,
    o.channel,
    c.customer_id,
    c.company_name,
    c.segment,
    c.region,
    a.revenue,
    a.cost_of_goods,
    a.gross_margin,
    case when a.revenue = 0 then 0 else round(a.gross_margin / a.revenue * 100, 2) end as margin_rate,
    a.units_sold
from {{ ref('stg_orders') }} o
join {{ ref('stg_customers') }} c using (customer_id)
join order_amounts a using (order_id)
where o.status <> 'cancelled'

