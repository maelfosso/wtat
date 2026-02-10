with date_spine as (
  {{
    dbt_utils.date_spine(
      datepart="day",
      start_date="cast('2021-01-01' as date)",
      end_date="cast('2026-12-31' as date)"
    )
  }}
),

date_features as (
  select 
    -- cast(cast(date_day as varchar) as integer) as date_id,
    CAST(strftime(date_day, '%Y%m%d') AS INTEGER) AS date_id,
    date_day as date,

    extract(year from date_day) as year,
    extract(quarter from date_day) as quarter,
    extract(month from date_day) as month,
    extract(day from date_day) as day,
    extract(doy from date_day) as day_of_year,
    extract(week from date_day) as week_of_year,

    case extract(month from date_day)
      when 1 then 'January'
      when 2 then 'February'
      when 3 then 'March'
      when 4 then 'April'
      when 5 then 'May'
      when 6 then 'June'
      when 7 then 'July'
      when 8 then 'August'
      when 9 then 'September'
      when 10 then 'October'
      when 11 then 'November'
      when 12 then 'December'
    end as month_name,

    case extract(month from date_day)
      when 1 then 'Jan'
      when 2 then 'Feb'
      when 3 then 'Mar'
      when 4 then 'Apr'
      when 5 then 'May'
      when 6 then 'Jun'
      when 7 then 'Jul'
      when 8 then 'Aug'
      when 9 then 'Sep'
      when 10 then 'Oct'
      when 11 then 'Nov'
      when 12 then 'Dec'
    end as month_name_short,

    extract(dow from date_day) as day_of_week,

    case extract(dow from date_day)
      when 0 then 'Sunday'
      when 1 then 'Monday'
      when 2 then 'Tuesday'
      when 3 then 'Wednesday'
      when 4 then 'Thursday'
      when 5 then 'Friday'
      when 6 then 'Saturday'
    end as day_name,

    case extract(dow from date_day)
      when 0 then 'Sun'
      when 1 then 'Mon'
      when 2 then 'Tue'
      when 3 then 'Wed'
      when 4 then 'Thu'
      when 5 then 'Fri'
      when 6 then 'Sat'
    end as day_name_short,

    case when extract(month from date_day) = 1 and extract(day from date_day) = 1
      then true
      else false
      end as is_new_year,
    
    case when extract(month from date_day) = 12 and extract(day from date_day) = 25
      then true
      else false
      end as is_christmas,
    
    case when extract(dow from date_day) in (0, 6)
      then true
      else false
      end as is_weekend,

    'T' || cast(extract(quarter from date_day) as varchar) as quarter_name,

    case
      when extract(month from date_day) between 1 and 3 then 'Q1'
      when extract(month from date_day) between 4 and 6 then 'Q2'
      when extract(month from date_day) between 7 and 9 then 'Q3'
      when extract(month from date_day) between 10 and 12 then 'Q4'
    end as fiscal_quarter

    -- date_format(date_day, 'DD/MM/YYYY') as date_fr,
    -- date_format(date_day, 'YYYY-MM-DD') as date_iso

  from date_spine
)

select * from date_features
order by date_id
