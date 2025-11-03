select
  id as ad_id,
  ad,
  post_id,
  post_type as ad_type,
  extraction_status,
  extraction_time as extraction_duration
from {{ source('data', 'ads') }}
