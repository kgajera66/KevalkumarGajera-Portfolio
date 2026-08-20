-- models/staging/stg_price.sql

with source as (

    select * from {{ source('raw', 'raw_price') }}

),

renamed as (

    select
        timestamp_utc,
        convert_timezone('UTC', 'Europe/Berlin', timestamp_utc) as timestamp_local,
        day_ahead_price_eur_mwh,

        -- Flagging negative prices HERE, not in the mart, because this is
        -- a property of the raw fact itself (did this hour have negative
        -- pricing or not), not something derived from combining sources.
        case when day_ahead_price_eur_mwh < 0 then true else false end as is_negative_price

    from source

)

select * from renamed

