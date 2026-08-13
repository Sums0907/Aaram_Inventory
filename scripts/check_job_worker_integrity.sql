WITH movements AS (
    SELECT 
        reference_id as job_worker_id,
        sku_id as item_id,
        SUM(CASE WHEN movement_type = 'JOB_WORK_ISSUE' THEN ABS(quantity) ELSE 0 END) as total_issued,
        SUM(CASE WHEN movement_type = 'JOB_WORK_RETURN' THEN quantity ELSE 0 END) as total_returned,
        SUM(CASE WHEN movement_type = 'RAW_MATERIAL_CONSUMPTION' THEN ABS(quantity) ELSE 0 END) as total_consumed
    FROM inventory_movements
    WHERE movement_type IN ('JOB_WORK_ISSUE', 'JOB_WORK_RETURN', 'RAW_MATERIAL_CONSUMPTION')
    GROUP BY reference_id, sku_id
)
SELECT 
    j.job_worker_id,
    j.item_id,
    j.pending_quantity as stored_pending,
    ROUND((COALESCE(m.total_issued, 0) - COALESCE(m.total_returned, 0) - COALESCE(m.total_consumed, 0)), 4) as derived_pending,
    CASE 
        WHEN ROUND(j.pending_quantity, 4) != ROUND((COALESCE(m.total_issued, 0) - COALESCE(m.total_returned, 0) - COALESCE(m.total_consumed, 0)), 4) 
        THEN 'FAIL' 
        ELSE 'PASS' 
    END as status
FROM inventory_job_worker_stock j
LEFT JOIN movements m ON j.job_worker_id = m.job_worker_id AND j.item_id = m.item_id;
