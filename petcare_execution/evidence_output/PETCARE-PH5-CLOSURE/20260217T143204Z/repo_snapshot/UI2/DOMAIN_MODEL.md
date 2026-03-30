# UI-2 Domain Model

## Tenant (top boundary)
- tenant_id: string

## Owner
- owner_id: string
- tenant_id: string
- fields: name, phone, email (optional)

## Pet
- pet_id: string
- tenant_id: string
- owner_id: string
- fields: name, species, breed (optional)

## Visit
- visit_id: string
- tenant_id: string
- pet_id: string
- fields: visit_date, notes (optional)

## Pharmacy Item
- item_id: string
- tenant_id: string
- fields: sku, name, qty

## Invariants
- All records are tenant-scoped
- owner_id must exist for pet
- pet_id must exist for visit
- Deterministic list ordering by id (lexical)
