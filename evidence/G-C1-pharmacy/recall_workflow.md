# G-C1 Pharmacy — SFDA Recall Workflow

## Lifecycle

```
ACTIVE → RECALLED → (manual) RESOLVED
```

| Status | Meaning |
|--------|---------|
| `active` | Batch is safe for dispensing |
| `recalled` | SFDA recall issued — dispense blocked |
| `resolved` | Recall resolved — manual admin update required |

## Recall issuance

`POST /api/admin/recalls` (platform_admin only):
1. Creates `RecallEvent` record with: batch_number, reason, severity, issued_at
2. Updates ALL `InventoryItem` rows with matching `sfda_batch_number` → `recall_status='recalled'`
3. Emits `sfda.recall_issued` audit event
4. Sends `RECALL_ALERT` WhatsApp notification to pharmacy operators (stub mode if no key)

## Dispense blocking

In `POST /api/pharmacy/dispense`, before any safety check:
For each `batch_number` in request:
- Query `InventoryItem` by batch_number
- If `recall_status != 'active'` → HTTP 403 `BATCH_RECALLED`
- Emits `pharmacy.recalled_batch_block` audit event

## Model: RecallEvent (models.py → `recall_events` table)

| Field | Type |
|-------|------|
| id | Integer PK |
| sfda_batch_number | String (indexed) |
| recall_reason | Text |
| severity | String |
| issued_at | DateTime(UTC) |
| resolution_status | String default='open' |

## SFDA batch fields on InventoryItem

| Field | Type | Notes |
|-------|------|-------|
| sfda_batch_number | String | Indexed for fast recall lookup |
| sfda_expiry_date | Date | |
| sfda_approval_no | String | |
| recall_status | String | active \| recalled \| quarantined |
