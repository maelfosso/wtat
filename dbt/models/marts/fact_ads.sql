with ads_country as (
  select 
    a.seeker_id,
    c.country
  from {{ ref('dim_seeker') }} a
  inner join {{ ref('bridge_seeker_country') }} c on c.seeker_id = a.seeker_id
  where c.link_type = 'residence'
)
select 
  a.ad_id,
  p.date as publication_date,
  w.seeker_id,
  s.sought_id,

  case
    when 'Cameroun' = ac.country and a.post_type = 'Sunday' then 1000
    when 'Cameroun' != ac.country and a.post_type = 'Sunday' then 16500
    when a.post_type = 'Special' then 33000
    else 0
  end as price,

  case
    when trim(a.ad) = '' then 0
    else length(trim(a.ad)) - length(replace(trim(a.ad), ' ', '')) + 1
  end as number_of_ad_words,

from {{ ref('dim_ads') }} a
-- inner join posts p on a.post_id = p.id
inner join {{ ref('dim_seeker') }} w on w.ad_id = a.ad_id
inner join {{ ref('dim_sought') }} s on s.ad_id = a.ad_id
inner join ads_country ac on ac.seeker_id = w.seeker_id
