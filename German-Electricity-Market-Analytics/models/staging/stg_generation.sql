-- models/staging/stg_generation.sql
--

with source as (

    select * from {{ source('raw', 'raw_generation') }}

),

renamed as (

    select
        timestamp_utc,
  
        convert_timezone('UTC', 'Europe/Berlin', timestamp_utc) as timestamp_local,

        wind_onshore_mw,
        photovoltaik_mw,
        erdgas_mw,
        kernenergie_mw,
        steinkohle_mw,
        braunkohle_mw,
        biomasse_mw,
        wasserkraft_mw,
  
        coalesce(wind_onshore_mw, 0)
            + coalesce(photovoltaik_mw, 0)
            + coalesce(erdgas_mw, 0)
            + coalesce(kernenergie_mw, 0)
            + coalesce(steinkohle_mw, 0)
            + coalesce(braunkohle_mw, 0)
            + coalesce(biomasse_mw, 0)
            + coalesce(wasserkraft_mw, 0) as total_generation_mw,

        (coalesce(wind_onshore_mw, 0)
            + coalesce(photovoltaik_mw, 0)
            + coalesce(biomasse_mw, 0)
            + coalesce(wasserkraft_mw, 0))
        / nullif(
            coalesce(wind_onshore_mw, 0)
                + coalesce(photovoltaik_mw, 0)
                + coalesce(erdgas_mw, 0)
                + coalesce(kernenergie_mw, 0)
                + coalesce(steinkohle_mw, 0)
                + coalesce(braunkohle_mw, 0)
                + coalesce(biomasse_mw, 0)
                + coalesce(wasserkraft_mw, 0),
            0
        ) as renewable_share

    from source

)

select * from renamed

