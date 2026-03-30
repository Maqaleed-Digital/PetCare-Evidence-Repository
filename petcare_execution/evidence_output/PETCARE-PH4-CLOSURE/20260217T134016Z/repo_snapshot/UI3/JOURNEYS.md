# UI-3 Journeys (Phase-1)

All journeys are tenant-scoped.

## J-1 Owner Onboarding
1) Collect owner fields
2) Persist under key: owners/{owner_id}
3) Confirm read-back

## J-2 Pet Registration
1) Select owner_id
2) Persist pet under key: pets/{pet_id} with owner_id
3) Confirm read-back

## J-3 Visit Capture
1) Select pet_id
2) Persist visit under key: visits/{visit_id} with pet_id
3) Confirm read-back

## J-4 Pharmacy Item Add
1) Enter sku/name/qty
2) Persist under key: pharmacy/{item_id}
3) List keys prefix pharmacy/

## J-5 Evidence Export (Admin)
1) Call export bundle endpoint
2) Bundle created under EVIDENCE/exports/{tenant_id}_{timestamp}
3) Manifest returned
