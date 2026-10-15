select
    customer_id,
    trim(company_name) as company_name,
    lower(segment) as segment,
    upper(region) as region,
    created_at,
    updated_at
from {{ source('raw', 'customers') }}

