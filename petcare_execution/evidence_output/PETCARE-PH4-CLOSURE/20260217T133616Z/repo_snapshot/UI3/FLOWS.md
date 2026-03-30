# UI-3 Flow Definitions

## Common Rules
- Header x-tenant-id is required
- Keys are normalized (no absolute, no ..)
- Deterministic listing: lexical sort

## Flow: Write Record
Request: POST /api/platform-admin/storage/put
Body: {\"key\":\"<path>\",\"value\":{...}}
Response: {\"ok\":true}

## Flow: Read Record
Request: POST /api/platform-admin/storage/get
Body: {\"key\":\"<path>\"}
Response: {\"ok\":true,\"value\":{...}|null}

## Flow: Delete Record
Request: POST /api/platform-admin/storage/delete
Body: {\"key\":\"<path>\"}
Response: {\"ok\":true,\"deleted\":true|false}

## Flow: List Keys
Request: POST /api/platform-admin/storage/list
Body: {\"prefix\":\"owners/\"}
Response: {\"ok\":true,\"keys\":[...sorted...]}

## Flow: Export Bundle
Request: POST /api/platform-admin/export/bundle
Body: {\"actor_id\":\"<id>\",\"out_dir\":\"EVIDENCE/exports/<tenant>_<ts>\"}
Response: {\"ok\":true,\"manifest\":{...}}
