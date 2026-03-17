PETCARE-PRODUCTION-ENVIRONMENT-READINESS-AND-DEPLOYMENT-CONTROLS
PRODUCTION_ENVIRONMENT_VARIABLE_CONTRACT

Purpose
Define the governed production environment variable contract required for deployable production readiness.

State Transition
- Current: production_infrastructure_activation
- Target: petcare_production_environment_ready

Rules
- real secret values must never be committed
- only variable names, scopes, ownership, rotation class, and validation rules are documented
- production variables are resolved at runtime from approved secret storage
- environment separation across dev, test, prod is mandatory
- no production deployment without contract completeness

Variable Classes
1. Core Runtime
- APP_ENV
- APP_REGION
- APP_BASE_URL
- API_BASE_URL
- WORKER_CONCURRENCY
- LOG_LEVEL

2. Data Layer
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_SSL_MODE
- DB_POOL_SIZE

3. Object Storage
- STORAGE_BUCKET_PRIMARY
- STORAGE_BUCKET_AUDIT_EXPORT
- STORAGE_REGION
- STORAGE_ENDPOINT_MODE

4. Security and Identity
- AUTH_ISSUER_URL
- AUTH_AUDIENCE
- SESSION_SIGNING_KEY_REF
- KMS_KEY_REF
- BREAK_GLASS_AUDIT_CHANNEL

5. AI Governance Runtime
- MODEL_GATEWAY_URL
- AI_PROVIDER_KEY_REF
- AI_PROMPT_LOG_STREAM
- AI_OUTPUT_LOG_STREAM
- AI_OVERRIDE_AUDIT_STREAM

6. Observability
- OTEL_EXPORTER_ENDPOINT
- LOG_SINK
- METRICS_NAMESPACE
- ALERT_ROUTING_KEY_REF

7. Deployment Controls
- RELEASE_VERSION
- RELEASE_APPROVER
- DEPLOYMENT_ENV
- CHANGE_WINDOW_ID

Per Variable Metadata Required
- variable name
- purpose
- environment scope
- owner
- secret or non-secret classification
- source system
- validation rule
- rotation class where applicable

Minimum Validation Rules
- all production secret variables use *_REF pattern when sourced from secrets manager
- no secret values present in tracked files
- prod-only variables are not required in dev unless explicitly marked optional
- required variables must be listed before go-live validation can pass

Approval Requirement
No production deployment approval unless:
- contract file exists
- required variables are enumerated
- secret handling rule preserved
- release approver field exists in deployment record
