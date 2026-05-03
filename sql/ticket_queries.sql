-- Ticket volume by month
SELECT strftime('%Y-%m', created_at) AS month, COUNT(*) AS tickets,
    SUM(CASE WHEN status IN ('Resolved','Closed') THEN 1 ELSE 0 END) AS resolved,
    ROUND(AVG(CASE WHEN resolved_at IS NOT NULL
        THEN (julianday(resolved_at) - julianday(created_at)) * 24 END), 2) AS avg_resolution_hrs
FROM tickets GROUP BY month ORDER BY month;

-- Category breakdown with SLA
SELECT category, COUNT(*) AS tickets,
    ROUND(AVG(CASE WHEN resolved_at IS NOT NULL
        THEN (julianday(resolved_at) - julianday(created_at)) * 24 END), 2) AS avg_hrs,
    ROUND(AVG(csat_score), 2) AS avg_csat
FROM tickets GROUP BY category ORDER BY tickets DESC;

-- Priority distribution
SELECT priority, COUNT(*) AS tickets,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tickets), 1) AS pct
FROM tickets GROUP BY priority ORDER BY
    CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END;

-- Channel performance
SELECT channel, COUNT(*) AS tickets,
    ROUND(AVG(CASE WHEN resolved_at IS NOT NULL
        THEN (julianday(resolved_at) - julianday(created_at)) * 24 END), 2) AS avg_resolution_hrs,
    ROUND(AVG(csat_score), 2) AS avg_csat
FROM tickets GROUP BY channel ORDER BY tickets DESC;

-- Open tickets aging
SELECT ticket_id, category, priority, agent_name,
    ROUND((julianday('now') - julianday(created_at)) * 24, 1) AS hours_open
FROM tickets WHERE status NOT IN ('Resolved','Closed')
ORDER BY hours_open DESC LIMIT 50;
