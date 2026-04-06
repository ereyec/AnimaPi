with ordered as (
  select
    plant_id,
    created_at,
    lag(created_at) over (
      partition by plant_id
      order by created_at
    ) as prev_time
  from public."Sensor_readings"
  where plant_id = 'c3c0d6aa-1234-5678-9abc-123456789abc'
    and created_at >= now() - interval '24 hours'
),
deltas as (
  select
    plant_id,
    created_at,
    extract(epoch from (created_at - prev_time)) as delta_seconds
  from ordered
  where prev_time is not null
)
select
  count(*) as intervals_checked,
  round(avg(delta_seconds)::numeric, 2) as avg_interval_s,
  round(min(delta_seconds)::numeric, 2) as min_interval_s,
  round(max(delta_seconds)::numeric, 2) as max_interval_s,
  round(stddev(delta_seconds)::numeric, 2) as stddev_interval_s,
  round(
    100.0 * avg(case when delta_seconds between 55 and 65 then 1 else 0 end),
    2
  ) as pct_within_55_65,
  sum(case when delta_seconds > 65 then 1 else 0 end) as late_intervals,
  sum(case when delta_seconds > 120 then 1 else 0 end) as likely_missed_uploads
from deltas;
