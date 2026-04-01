# PETCARE EP-13 Stage 1
# API Contract Specification
# Status: LOCKED
# Scope: External platform exposure with controlled integration only

## 1. Objective

Define the governed external API contract for PetCare platform externalization while preserving all EP-08 through EP-12 invariants.

This specification authorizes:
- safe read exposure
- controlled write request intake
- event subscription and webhook delivery
- partner-scoped integration access
- auditable traceable deterministic external behavior

This specification does not authorize:
- autonomous external execution
- payment execution by external parties
- approval bypass
- treasury bypass
- hidden or unregistered integrations
- AI-mediated external execution

## 2. Governance Boundary

All external write operations are request-creating interfaces only.

External request flow:

1. partner submits request
2. gateway validates identity and schema
3. platform converts request into internal governed action
4. internal approval gates are enforced
5. execution occurs only inside PetCare controlled runtime
6. outcome becomes externally visible according to access scope

Non-bypassable rule:

External API call does not equal execution.

## 3. API Surface Classification

### 3.1 Allowed Read APIs

Allowed read APIs expose only partner-scoped, tenant-scoped, least-privilege information.

Authorized read surface:

- partner profile and integration status
- order status
- referral status
- availability sync status
- catalog ingestion job status
- webhook subscription status
- event delivery status
- partner scorecard summary when explicitly enabled
- audit receipt metadata for that partner

### 3.2 Allowed Controlled Write APIs

Allowed controlled write APIs accept requests that enter internal governance.

Authorized controlled write surface:

- create referral request
- create order request
- submit catalog batch
- update availability
- create webhook subscription
- disable webhook subscription
- rotate webhook secret through governed process
- request partner credential rotation
- request partner sandbox certification

### 3.3 Explicitly Forbidden API Capabilities

Forbidden surface:

- payment initiation
- payout release
- treasury movement
- prescription approval
- prescription authorization
- clinical diagnosis submission as final decision
- consultation sign-off
- emergency override closure
- AI instruction execution against core runtime
- hidden asynchronous mutation without audit trail

## 4. Versioning Strategy

### 4.1 Version Pattern

Base path versioning is mandatory.

Version pattern:
- /v1/...

Minor additive changes are allowed without path change when backward compatible.

Breaking changes require:
- new major version path
- migration note
- deprecation window
- partner communication plan
- updated evidence artifacts

### 4.2 Compatibility Rules

Backward-compatible changes:
- adding optional fields
- adding new enum values only when consumers are documented to ignore unknown values
- adding new endpoints
- adding new event types after subscription model update

Breaking changes:
- removing fields
- changing field types
- changing required fields
- changing approval semantics
- changing authentication model
- changing error contract

## 5. Authentication and Authorization Model

### 5.1 Supported Authentication Methods

Primary:
- OAuth 2.0 client credentials for partner systems

Secondary:
- API key for constrained low-risk integrations
- mutual TLS for high-trust regulated partners when approved

### 5.2 Authorization Model

Authorization decision inputs:
- partner_id
- tenant_id
- integration_status
- granted_scopes
- endpoint capability
- environment
- gateway policy version

Required scope categories:
- orders.read
- orders.write_request
- referrals.read
- referrals.write_request
- availability.write
- catalog.write
- webhooks.manage
- events.read
- partner.read
- audit.read_receipts

### 5.3 Tenant Isolation

All access is constrained by:
- partner scope
- tenant scope
- object ownership
- environment boundary

No cross-tenant reads.
No cross-partner reads.
No production data access from sandbox credentials.

## 6. Common Contract Rules

### 6.1 Headers

Required headers for all requests:

- Authorization
- X-PetCare-Partner-Id
- X-PetCare-Request-Id
- X-PetCare-Timestamp

Required for idempotent controlled writes:

- Idempotency-Key

Optional diagnostic header:
- X-PetCare-Correlation-Id

### 6.2 Content Type

JSON only for synchronous API requests and responses.

Media type:
- application/json

Webhook media type:
- application/json

### 6.3 Time Format

All timestamps must be RFC 3339 UTC.

Example:
- 2026-04-01T11:30:00Z

### 6.4 Identifier Format

Identifiers are opaque strings.
Consumers must not infer meaning from identifier structure.

## 7. Resource Contracts

### 7.1 Partner Profile

Resource:
- PartnerProfile

Fields:
- partner_id
- tenant_id
- legal_name
- display_name
- integration_status
- allowed_scopes
- webhook_capable
- sandbox_certification_status
- created_at
- updated_at

### 7.2 Order Summary

Resource:
- OrderSummary

Fields:
- order_id
- partner_id
- tenant_id
- external_reference
- order_type
- status
- governance_state
- approval_state
- amount_currency
- amount_value
- created_at
- updated_at

Status values:
- REQUEST_RECEIVED
- PENDING_INTERNAL_REVIEW
- PENDING_APPROVAL
- APPROVED_FOR_EXECUTION
- IN_EXECUTION
- COMPLETED
- REJECTED
- CANCELLED

### 7.3 Referral Summary

Resource:
- ReferralSummary

Fields:
- referral_id
- partner_id
- tenant_id
- pet_id_reference
- referral_type
- status
- internal_case_id
- governance_state
- created_at
- updated_at

Status values:
- REQUEST_RECEIVED
- TRIAGE_PENDING
- UNDER_REVIEW
- ACCEPTED
- REJECTED
- CLOSED

### 7.4 Availability Update

Resource:
- AvailabilityUpdate

Fields:
- availability_update_id
- partner_id
- tenant_id
- site_id
- service_window_start
- service_window_end
- capacity_status
- notes
- effective_from
- submitted_at
- processed_at
- processing_result

Capacity status values:
- AVAILABLE
- LIMITED
- UNAVAILABLE
- EMERGENCY_ONLY

### 7.5 Catalog Batch

Resource:
- CatalogBatch

Fields:
- catalog_batch_id
- partner_id
- tenant_id
- submitted_item_count
- accepted_item_count
- rejected_item_count
- processing_status
- submitted_at
- completed_at

Processing status values:
- RECEIVED
- VALIDATING
- PARTIALLY_ACCEPTED
- ACCEPTED
- REJECTED

### 7.6 Webhook Subscription

Resource:
- WebhookSubscription

Fields:
- subscription_id
- partner_id
- tenant_id
- endpoint_url
- subscribed_event_types
- status
- signing_key_id
- created_at
- updated_at

Status values:
- ACTIVE
- PAUSED
- DISABLED
- ROTATION_PENDING

### 7.7 Event Delivery Record

Resource:
- EventDeliveryRecord

Fields:
- event_id
- event_type
- subscription_id
- delivery_status
- attempt_count
- last_attempt_at
- next_retry_at
- trace_id
- payload_hash
- signature_key_id

Delivery status values:
- PENDING
- DELIVERED
- RETRY_SCHEDULED
- FAILED
- DISABLED

## 8. Endpoint Contract

### 8.1 Read Endpoints

#### GET /v1/partner/profile

Purpose:
Return the authenticated partner profile and integration capability summary.

Authorization:
- partner.read

Response:
- 200 PartnerProfile

#### GET /v1/orders

Purpose:
List partner-owned orders.

Authorization:
- orders.read

Query parameters:
- status
- created_from
- created_to
- page
- page_size
- external_reference

Response:
- 200 paginated list of OrderSummary

#### GET /v1/orders/{order_id}

Purpose:
Return a single partner-owned order.

Authorization:
- orders.read

Response:
- 200 OrderSummary

#### GET /v1/referrals

Purpose:
List partner-owned referrals.

Authorization:
- referrals.read

Query parameters:
- status
- created_from
- created_to
- page
- page_size

Response:
- 200 paginated list of ReferralSummary

#### GET /v1/referrals/{referral_id}

Purpose:
Return a single partner-owned referral.

Authorization:
- referrals.read

Response:
- 200 ReferralSummary

#### GET /v1/catalog/batches/{catalog_batch_id}

Purpose:
Return catalog ingestion batch status.

Authorization:
- catalog.write

Response:
- 200 CatalogBatch

#### GET /v1/webhook-subscriptions

Purpose:
List webhook subscriptions for the authenticated partner.

Authorization:
- webhooks.manage

Response:
- 200 list of WebhookSubscription

#### GET /v1/events/{event_id}

Purpose:
Return partner-visible delivery record for an event.

Authorization:
- events.read

Response:
- 200 EventDeliveryRecord

### 8.2 Controlled Write Endpoints

#### POST /v1/referrals

Purpose:
Create a referral request for internal governed review.

Authorization:
- referrals.write_request

Idempotency:
- required

Request fields:
- external_reference
- tenant_id
- referral_type
- pet_id_reference
- referral_reason
- requested_service_date
- attachments
- metadata

Response:
- 202 accepted
- includes referral_id
- includes governance_state
- includes trace_id

#### POST /v1/orders

Purpose:
Create an order request for internal governed processing.

Authorization:
- orders.write_request

Idempotency:
- required

Request fields:
- external_reference
- tenant_id
- order_type
- line_items
- requested_fulfillment_window
- delivery_constraints
- metadata

Response:
- 202 accepted
- includes order_id
- includes governance_state
- includes trace_id

#### PUT /v1/availability

Purpose:
Submit partner availability state for routing and operational control.

Authorization:
- availability.write

Idempotency:
- required

Request fields:
- tenant_id
- site_id
- service_window_start
- service_window_end
- capacity_status
- notes
- effective_from

Response:
- 202 accepted
- includes availability_update_id
- includes processing_result
- includes trace_id

#### POST /v1/catalog/batches

Purpose:
Submit catalog items for validation and ingestion.

Authorization:
- catalog.write

Idempotency:
- required

Request fields:
- tenant_id
- batch_reference
- items

Item fields:
- item_code
- item_name
- item_type
- unit_price
- currency
- active
- inventory_hint
- metadata

Response:
- 202 accepted
- includes catalog_batch_id
- includes processing_status
- includes trace_id

#### POST /v1/webhook-subscriptions

Purpose:
Create webhook subscription for approved event types.

Authorization:
- webhooks.manage

Request fields:
- endpoint_url
- subscribed_event_types

Response:
- 201 created
- includes WebhookSubscription

#### POST /v1/webhook-subscriptions/{subscription_id}/pause

Purpose:
Pause event delivery to subscription.

Authorization:
- webhooks.manage

Response:
- 200 updated subscription status

#### POST /v1/webhook-subscriptions/{subscription_id}/resume

Purpose:
Resume event delivery to subscription.

Authorization:
- webhooks.manage

Response:
- 200 updated subscription status

#### DELETE /v1/webhook-subscriptions/{subscription_id}

Purpose:
Disable subscription.

Authorization:
- webhooks.manage

Response:
- 200 disabled subscription status

## 9. Webhook Contract

### 9.1 Delivery Rules

Webhook deliveries must be:
- signed
- timestamped
- retried with exponential backoff
- idempotent on receiver side
- logged with full traceability

### 9.2 Webhook Event Envelope

Required webhook payload envelope:
- event_id
- event_type
- occurred_at
- partner_id
- tenant_id
- trace_id
- payload
- payload_hash

### 9.3 Webhook Event Types

Stage 1 locked event types:
- order.created
- order.updated
- referral.created
- referral.updated
- availability.updated
- catalog.batch.completed
- webhook.subscription.disabled
- settlement.generated
- dispute.opened

### 9.4 Webhook Signing

Required signature headers:
- X-PetCare-Signature
- X-PetCare-Signature-Timestamp
- X-PetCare-Event-Id

Signature basis:
- timestamp + "." + raw_body

Signing rule:
- HMAC SHA-256

### 9.5 Retry Policy

Retry behavior:
- initial delivery attempt immediately
- subsequent retries with exponential backoff
- maximum attempts configurable by policy
- terminal failure recorded in audit trail

## 10. Error Model

### 10.1 Error Envelope

All non-2xx responses must return:

- error_code
- error_message
- trace_id
- timestamp
- retryable
- details

### 10.2 Standard Error Codes

Locked Stage 1 error codes:
- AUTHENTICATION_FAILED
- AUTHORIZATION_DENIED
- INVALID_REQUEST
- INVALID_SCOPE
- RESOURCE_NOT_FOUND
- IDEMPOTENCY_CONFLICT
- RATE_LIMIT_EXCEEDED
- GOVERNANCE_RESTRICTION
- TENANT_BOUNDARY_VIOLATION
- UNSUPPORTED_EVENT_TYPE
- ENDPOINT_VALIDATION_FAILED
- INTERNAL_PROCESSING_ERROR
- SERVICE_UNAVAILABLE

### 10.3 Governance Restriction Semantics

GOVERNANCE_RESTRICTION must be returned when:
- caller attempts forbidden action
- request violates approval boundary
- treasury boundary would be bypassed
- disallowed environment crossing is attempted
- write attempt targets non-exposed capability

## 11. Rate Limiting and Usage Controls

### 11.1 Required Controls

Controls:
- per partner default quota
- per endpoint quota
- burst threshold
- concurrent request threshold
- webhook delivery failure threshold
- anomaly-based temporary restriction

### 11.2 Response Contract

Rate limit responses must include:
- X-RateLimit-Limit
- X-RateLimit-Remaining
- X-RateLimit-Reset

429 responses must return:
- error_code = RATE_LIMIT_EXCEEDED
- retryable = true

## 12. Audit and Traceability

Every external API interaction must generate:
- partner_id
- tenant_id
- request_id
- trace_id
- correlation_id if present
- actor_type = external_partner_system
- endpoint
- method
- response_code
- policy_version
- auth_method
- idempotency_key when applicable

For controlled write requests, audit chain must also link:
- external_request_id
- internal_request_id
- approval_record_id when applicable
- execution_record_id when applicable
- outcome_record_id

## 13. Sandboxing and Environment Separation

Stage 1 environment rules:
- sandbox credentials only against sandbox base URL
- production credentials only against production base URL
- no shared webhook secrets across environments
- no shared subscriptions across environments
- no production identifiers exposed in sandbox

## 14. Security Rules

Mandatory security requirements:
- TLS required
- signed webhooks required
- least-privilege scopes required
- partner key rotation supported
- audit logs immutable after write
- schema validation before routing
- gateway policy evaluation before internal dispatch

## 15. Open Items Explicitly Deferred to Later Stages

Deferred:
- SDK generation
- partner developer portal UI
- sandbox self-service onboarding
- external API analytics dashboard
- partner certification automation
- bulk asynchronous file ingestion beyond catalog batch surface
- advanced dispute mutation APIs
- regulated payment network exposure

## 16. Stage 1 Lock Result

This contract locks:
- endpoint surface
- request and response semantics
- authentication headers
- webhook envelope
- error model
- governance restrictions
- traceability requirements
- versioning model

Implementation may proceed only within this contract.
