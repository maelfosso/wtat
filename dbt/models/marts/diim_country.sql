with all_country as (
  select distinct unnest(country_of_residence) as country, unnest(continent_of_residence) as continent
  from {{ ref('stg_data__profiles') }}
  union
  select distinct unnest(country_of_origin) as country, unnest(continent_of_origin) as continent
  from {{ ref('stg_data__profiles') }}
)
select 
  {{ dbt_utils.generate_surrogate_key(['country', 'continent']) }} AS country_id,
  *,
from all_country