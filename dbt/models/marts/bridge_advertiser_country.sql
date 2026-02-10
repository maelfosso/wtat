with base as (
  select distinct advertiser_id, unnest(country_of_residence) as country, unnest(continent_of_residence) as continent,
  'residence' as link_type
  from {{ ref('int_data__advertiser') }}
  union
  select distinct advertiser_id,  unnest(country_of_origin) as country, unnest(continent_of_origin) as continent,
    'origin' as link_type
  from {{ ref('int_data__advertiser') }}
)
select
  advertiser_id,
  {{ dbt_utils.generate_surrogate_key(['country', 'continent']) }} AS country_id,
  link_type
from base
