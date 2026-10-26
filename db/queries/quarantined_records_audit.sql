-- Query: Quarantined Records Audit by Scan
-- Parameter: :scan_id
SELECT
    qr.record_type,
    qr.rejection_reason,
    COUNT(*) AS total_rejected,
    MIN(qr.created_at) AS first_occurrence,
    MAX(qr.created_at) AS last_occurrence
FROM quarantined_records qr
WHERE qr.scan_id = :scan_id
GROUP BY qr.record_type, qr.rejection_reason
ORDER BY total_rejected DESC;
