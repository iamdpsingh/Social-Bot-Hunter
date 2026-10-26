-- Query: Top Risk Accounts for a given Scan
-- Parameters: :scan_id, :limit
SELECT
    pa.platform_account_id,
    pa.username,
    pa.display_name,
    ra.score,
    ra.band,
    ra.evidence_coverage,
    ra.features_available,
    ra.features_total,
    ra.contributions,
    ra.assessed_at
FROM risk_assessments ra
JOIN platform_accounts pa
    ON pa.id = ra.platform_account_id
WHERE ra.scan_id = :scan_id
    AND ra.status = 'scored'
ORDER BY ra.score DESC, ra.evidence_coverage DESC
LIMIT :limit;
