with base as (
  select distinct desired_id, unnest(country_of_residence) as country, unnest(continent_of_residence) as continent,
  'residence' as link_type
  from {{ ref('int_data__desired') }}
  union
  select distinct desired_id,  unnest(country_of_residence) as country, unnest(continent_of_residence) as continent,
    'origin' as link_type
  from {{ ref('int_data__desired') }}
)
select
  desired_id,
  {{ dbt_utils.generate_surrogate_key(['country', 'continent']) }} AS country_id,
  link_type
from base