# Data Directory

## Structure

| Folder | Purpose |
|---|---|
| `raw/` | Original ticket exports, CRM dumps |
| `processed/` | Cleaned, feature-engineered ticket data |
| `external/` | Holiday calendars, product catalogs |

## Expected Schema

| Column | Type | Description |
|---|---|---|
| `ticket_id` | string | Unique ticket identifier |
| `created_at` | datetime | Ticket creation timestamp |
| `resolved_at` | datetime | Resolution timestamp (null if open) |
| `first_response_at` | datetime | First agent response timestamp |
| `category` | string | Issue category |
| `subcategory` | string | Issue subcategory |
| `priority` | string | Critical, High, Medium, Low |
| `status` | string | Current ticket status |
| `channel` | string | Email, Chat, Phone, Web Form, Social Media |
| `agent_id` | string | Assigned agent identifier |
| `agent_name` | string | Agent display name |
| `team` | string | Support team/department |
| `customer_id` | string | Customer identifier |
| `customer_tier` | string | Free, Basic, Premium, Enterprise |
| `subject` | string | Ticket subject line |
| `description` | string | Ticket body text |
| `tags` | string | Comma-separated labels |
| `csat_score` | int | Customer satisfaction (1-5) |
| `resolution_notes` | string | Agent resolution summary |
| `is_escalated` | bool | Escalation flag |
| `reopen_count` | int | Times ticket was reopened |
| `num_interactions` | int | Total messages exchanged |

> Raw data files are excluded from version control via `.gitignore`.
