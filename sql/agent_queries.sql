-- Agent leaderboard
SELECT a.agent_id, t.agent_name, a.tickets_handled,
    a.avg_resolution_hrs, ROUND(a.sla_rate * 100, 1) AS sla_pct,
    a.avg_csat, ROUND(a.escalation_rate * 100, 1) AS escalation_pct
FROM agent_metrics a
LEFT JOIN (SELECT DISTINCT agent_id, agent_name FROM tickets) t ON a.agent_id = t.agent_id
ORDER BY a.avg_csat DESC, a.sla_rate DESC;

-- Agent trend over time
SELECT agent_id, period, tickets_handled,
    ROUND(avg_resolution_hrs, 1) AS avg_hrs,
    ROUND(sla_rate * 100, 1) AS sla_pct
FROM agent_metrics ORDER BY agent_id, period;

-- CSAT by agent
SELECT agent_id, agent_name, COUNT(*) AS reviews,
    ROUND(AVG(csat_score), 2) AS avg_csat,
    ROUND(SUM(CASE WHEN csat_score >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS satisfied_pct
FROM tickets WHERE csat_score IS NOT NULL
GROUP BY agent_id HAVING reviews >= 10
ORDER BY avg_csat DESC;

-- Escalation by agent
SELECT agent_id, agent_name, COUNT(*) AS total,
    SUM(is_escalated) AS escalated,
    ROUND(AVG(is_escalated) * 100, 1) AS escalation_pct
FROM tickets GROUP BY agent_id
HAVING total >= 10
ORDER BY escalation_pct DESC;
