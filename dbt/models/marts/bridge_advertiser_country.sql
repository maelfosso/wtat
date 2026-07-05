with base as (
  select distinct seeker_id, unnest(country_of_residence) as country, unnest(continent_of_residence) as continent,
  'residence' as link_type
  from {{ ref('int_data__seeker') }}
  union
  select distinct seeker_id,  unnest(country_of_origin) as country, unnest(continent_of_origin) as continent,
    'origin' as link_type
  from {{ ref('int_data__seeker') }}
)
select
  seeker_id,
  {{ dbt_utils.generate_surrogate_key(['country', 'continent']) }} AS country_id,
  link_type
from base
