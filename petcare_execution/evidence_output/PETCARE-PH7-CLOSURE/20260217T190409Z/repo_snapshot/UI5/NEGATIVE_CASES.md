# UI-5 Negative Cases

## NC-1 Missing tenant header
Expected: 400

## NC-2 Attempt export without tenant header
Expected: 400

## NC-3 Invalid key: absolute path
Expected: 400

## NC-4 Invalid key: traversal ..
Expected: 400

## NC-5 Determinism
- Re-run export with same dataset -> stable ordering rules must hold
