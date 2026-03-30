# UI-2 API Surface

All endpoints are tenant-scoped via header:
- x-tenant-id: required

## Platform Admin (baseline)
- POST /api/platform-admin/storage/put
- POST /api/platform-admin/storage/get
- POST /api/platform-admin/storage/delete
- POST /api/platform-admin/storage/list
- POST /api/platform-admin/export/bundle

## Entity Keys (Phase-1)
Keys are stored in the tenant store using normalized paths:
- owners/{owner_id}
- pets/{pet_id}
- visits/{visit_id}
- pharmacy/{item_id}

## Determinism
- list returns lexical key ordering
- export bundle sorts paths lexically
