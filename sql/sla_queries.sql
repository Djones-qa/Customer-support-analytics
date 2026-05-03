-- SLA compliance by priority
SELECT s.priority, COUNT(*) AS total,
    SUM(s.sla_met) AS met, SUM(1 - s.sla_met) AS breached,
    ROUND(AVG(s.sla_met) * 100, 1) AS compliance_pct,
    ROUND(AVG(s.breach_hours), 2) AS avg_breach_hours
FROM sla_tracking s GROUP BY s.priority
ORDER BY CASE s.priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END;

-- SLA trend by month
SELECT strftime('%Y-%m', t.created_at) AS month,
    ROUND(AVG(s.sla_met) * 100, 1) AS sla_pct,
    COUNT(*) AS tickets
FROM tickets t JOIN sla_tracking s ON t.ticket_id = s.ticket_id
GROUP BY month ORDER BY month;

-- Worst SLA breaches
SELECT t.ticket_id, t.category, t.priority, t.agent_name,
    s.sla_target_hours, ROUND(s.actual_hours, 1) AS actual_hours,
    ROUND(s.breach_hours, 1) AS breach_hours
FROM sla_tracking s JOIN tickets t ON s.ticket_id = t.ticket_id
WHERE s.sla_met = 0 ORDER BY s.breach_hours DESC LIMIT 30;

-- First response SLA
SELECT strftime('%Y-%m', created_at) AS month,
    ROUND(AVG(CASE WHEN first_response_at IS NOT NULL
        THEN (julianday(first_response_at) - julianday(created_at)) * 24 END), 2) AS avg_first_response_hrs,
    ROUND(SUM(CASE WHEN first_response_at IS NOT NULL
        AND (julianday(first_response_at) - julianday(created_at)) * 24 <= 1
        THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS first_response_sla_pct
FROM tickets GROUP BY month ORDER BY month;
