-- models/marts/price_by_hour_of_day.sql
--
-- Grain: one row per hour-of-day (0-23), averaged across the whole 2-year window.

with hourly as (

    select * from {{ ref('int_energy_hourly') }}

),

by_hour as (

    select
        extract(hour from timestamp_local) as hour_of_day,

        avg(day_ahead_price_eur_mwh) as avg_price_eur_mwh,
        stddev(day_ahead_price_eur_mwh) as price_stddev,

        avg(renewable_share) as avg_renewable_share,
        avg(total_load_mw) as avg_load_mw,

        count_if(is_negative_price) as negative_price_hour_count

    from hourly
    group by 1

)

select * from by_hour
order by hour_of_day

