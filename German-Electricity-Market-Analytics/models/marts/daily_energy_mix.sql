-- models/marts/daily_energy_mix.sql
--
-- Grain of this table: one row per calendar day.

with hourly as (

    select * from {{ ref('int_energy_hourly') }}

),

daily as (

    select
        date(timestamp_local) as report_date,

        avg(wind_onshore_mw)   as avg_wind_onshore_mw,
        avg(photovoltaik_mw)   as avg_photovoltaik_mw,
        avg(erdgas_mw)         as avg_erdgas_mw,
        avg(kernenergie_mw)    as avg_kernenergie_mw,
        avg(steinkohle_mw)     as avg_steinkohle_mw,
        avg(braunkohle_mw)     as avg_braunkohle_mw,
        avg(biomasse_mw)       as avg_biomasse_mw,
        avg(wasserkraft_mw)    as avg_wasserkraft_mw,

        avg(total_generation_mw) as avg_total_generation_mw,
        avg(total_load_mw)       as avg_total_load_mw,
        avg(residual_load_mw)    as avg_residual_load_mw,
  
        sum(coalesce(wind_onshore_mw, 0)
            + coalesce(photovoltaik_mw, 0)
            + coalesce(biomasse_mw, 0)
            + coalesce(wasserkraft_mw, 0))
        / nullif(sum(total_generation_mw), 0) as renewable_share,

        avg(day_ahead_price_eur_mwh) as avg_price_eur_mwh,
        min(day_ahead_price_eur_mwh) as min_price_eur_mwh,
        max(day_ahead_price_eur_mwh) as max_price_eur_mwh,

        count_if(is_negative_price) as negative_price_hours,

        avg_braunkohle_mw + avg_steinkohle_mw as avg_coal_mw,

        CASE 
            WHEN EXTRACT(MONTH FROM report_date) IN (12,1,2) THEN 'Winter'
            WHEN EXTRACT(MONTH FROM report_date) IN (3,4,5) THEN 'Spring'
            WHEN EXTRACT(MONTH FROM report_date) IN (6,7,8) THEN 'Summer'
            WHEN EXTRACT(MONTH FROM report_date) IN (9,10,11) THEN 'Autumn'
        END AS season

    from hourly
    group by 1

)

select * from daily
order by report_date

