-- Average wait time by service for last 7 days
SELECT s.name, AVG(ar.avg_wait_minutes) AS avg_wait
FROM apps_analytics_analyticsrecord ar
JOIN apps_queues_service s ON s.id = ar.service_id
WHERE ar.period_start >= NOW() - INTERVAL '7 days'
GROUP BY s.name
ORDER BY avg_wait DESC;

-- Throughput per hour
SELECT date_trunc('hour', period_start) AS hour_bucket, SUM(throughput) AS total_served
FROM apps_analytics_analyticsrecord
GROUP BY hour_bucket
ORDER BY hour_bucket DESC;

-- Queue abandonment rate by service
SELECT s.code, AVG(ar.abandonment_rate) AS avg_abandonment
FROM apps_analytics_analyticsrecord ar
JOIN apps_queues_service s ON s.id = ar.service_id
GROUP BY s.code;
