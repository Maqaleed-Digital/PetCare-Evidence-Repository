PETCARE PHASE 2
DF-01 Security Baseline
Status: LOCKED

Security controls:
- Cloud KMS project enabled
- Secret Manager enabled
- audit logs baseline enforced
- default networks removed
- org IAM baseline applied
- firewall logs enabled
- VPC flow logs enabled
- keyring per region
- keys for storage, database, secrets, artifacts
- no shared secret material between sandbox and prod

Keys:
- kr-petcare-mec2
- key-petcare-storage
- key-petcare-db
- key-petcare-secrets
- key-petcare-artifacts
