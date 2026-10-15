select
    order_date,
    region,
    channel,
    count(distinct order_id) as orders,
    count(distinct customer_id) as customers,
    sum(units_sold) as units_sold,
    sum(revenue) as revenue,
    sum(cost_of_goods) as cost_of_goods,
    sum(gross_margin) as gross_margin,
    case when sum(revenue) = 0 then 0 else round(sum(gross_margin) / sum(revenue) * 100, 2) end as margin_rate
from {{ ref('sales_orders') }}
group by order_date, region, channel

