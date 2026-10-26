-- Query: Candidate Coordinated Clusters Summary for a Scan
-- Parameter: :scan_id
SELECT
    nc.id AS cluster_id,
    nc.signal_strength,
    nc.confidence,
    nc.member_count,
    nc.method,
    nc.signals,
    nc.metrics,
    nc.alternative_explanations,
    nc.review_status
FROM network_clusters nc
WHERE nc.scan_id = :scan_id
ORDER BY
    CASE nc.signal_strength
        WHEN 'high' THEN 1
        WHEN 'moderate' THEN 2
        WHEN 'low' THEN 3
        ELSE 4
    END,
    nc.member_count DESC;
