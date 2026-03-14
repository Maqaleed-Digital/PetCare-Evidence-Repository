# Shared Pagination and Filtering Contract

## Version

`petcare-pagination-v1` · Phase PH-FND-3

## Pagination Style

All list endpoints use **cursor-based pagination** (keyset pagination). Offset-based
pagination is not supported — it is unsafe for append-only collections (e.g., audit_ledger).

## Request Parameters

| Parameter  | Type    | Default | Description                                              |
|------------|---------|---------|----------------------------------------------------------|
| `limit`    | integer | 50      | Number of items to return. Maximum: 200.                 |
| `cursor`   | string  | (none)  | Opaque cursor from previous response. Omit for first page. |
| `order`    | string  | `asc`   | Sort direction: `asc` or `desc` by primary sort key.     |

Cursors are opaque base64-encoded strings. Clients must not construct or decode them.

## Response Envelope

Every paginated list response wraps results in:

```json
{
  "items": [ ...resource objects... ],
  "pagination": {
    "limit":       50,
    "count":       50,
    "has_more":    true,
    "next_cursor": "<opaque>",
    "prev_cursor": "<opaque>"
  }
}
```

| Field         | Description                                                    |
|---------------|----------------------------------------------------------------|
| `count`       | Number of items in this page (≤ limit)                        |
| `has_more`    | `true` if another page exists after this one                  |
| `next_cursor` | Pass as `cursor` to fetch the next page. Absent if `has_more == false` |
| `prev_cursor` | Pass as `cursor` to fetch the previous page. Absent on first page |

## Filtering

Filters are passed as query parameters using the pattern `filter[field]=value`.

### Supported Operators

| Syntax                         | Meaning                        | Example                              |
|--------------------------------|--------------------------------|--------------------------------------|
| `filter[field]=value`          | Exact match                    | `filter[status]=pending`             |
| `filter[field][gte]=value`     | Greater than or equal          | `filter[ts_utc][gte]=2026-01-01T00:00:00Z` |
| `filter[field][lte]=value`     | Less than or equal             | `filter[ts_utc][lte]=2026-03-15T23:59:59Z` |
| `filter[field][in]=a,b,c`      | Value in set                   | `filter[event_type][in]=consent_granted,consent_revoked` |

Unknown filter fields return `422 VALIDATION_INVALID_FIELD`.

## Sorting

```
sort=field_name        # ascending
sort=-field_name       # descending (prefix -)
```

If `sort` and `order` conflict, `sort` takes precedence.

## Example — Audit log page 1

```
GET /v1/audit/events?limit=20&filter[ts_utc][gte]=2026-03-01T00:00:00Z&sort=-ts_utc
```

Response:

```json
{
  "items": [ { "event_id": "...", "ts_utc": "2026-03-15T10:42:00Z", ... }, ... ],
  "pagination": {
    "limit": 20, "count": 20, "has_more": true,
    "next_cursor": "eyJzZXEiOiAyMDB9",
    "prev_cursor": null
  }
}
```
