-- models/marts/negative_price_events.sql
--   
-- Grain: one row per hour where the price went negative.

with hourly as (

    select * from {{ ref('int_energy_hourly') }}

),

negative_events as (

    select
        timestamp_local,
        day_ahead_price_eur_mwh,
        total_load_mw,
        total_generation_mw,
        renewable_share,
        residual_load_mw

    from hourly
    where is_negative_price

)

select * from negative_events
order by timestamp_local

