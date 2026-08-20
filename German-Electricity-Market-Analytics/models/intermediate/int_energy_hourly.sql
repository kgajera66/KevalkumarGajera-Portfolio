-- models/intermediate/int_energy_hourly.sql

with generation as (

    select * from {{ ref('stg_generation') }}

),

consumption as (

    select * from {{ ref('stg_consumption') }}

),

price as (

    select * from {{ ref('stg_price') }}

),

joined as (

    select
        generation.timestamp_utc,
        generation.timestamp_local,

        generation.wind_onshore_mw,
        generation.photovoltaik_mw,
        generation.erdgas_mw,
        generation.kernenergie_mw,
        generation.steinkohle_mw,
        generation.braunkohle_mw,
        generation.biomasse_mw,
        generation.wasserkraft_mw,
        generation.total_generation_mw,
        generation.renewable_share,

        consumption.total_load_mw,

        price.day_ahead_price_eur_mwh,
        price.is_negative_price,

        consumption.total_load_mw
            - (coalesce(generation.wind_onshore_mw, 0)
                + coalesce(generation.photovoltaik_mw, 0)
                + coalesce(generation.biomasse_mw, 0)
                + coalesce(generation.wasserkraft_mw, 0)) as residual_load_mw

    from generation
    inner join consumption
        on generation.timestamp_utc = consumption.timestamp_utc
    inner join price
        on generation.timestamp_utc = price.timestamp_utc

)

select * from joined

