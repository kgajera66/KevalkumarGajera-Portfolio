-- models/staging/stg_consumption.sql
-- Same 1:1 cleanup pattern as stg_generation -- just renaming and timezone conversion.

with source as (

    select * from {{ source('raw', 'raw_consumption') }}

),

renamed as (

    select
        timestamp_utc,
        convert_timezone('UTC', 'Europe/Berlin', timestamp_utc) as timestamp_local,
        netzlast_mw as total_load_mw

    from source

)

select * from renamed

