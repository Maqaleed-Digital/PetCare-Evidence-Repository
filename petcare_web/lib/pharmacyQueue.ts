/**
 * FR-27 (MVC-BUILD-RUNNER-001 U6) — the dispensing dashboard refreshes itself.
 *
 * Ratified AC-FR-27-01 (ACCEPT_WITH_THRESHOLD, REAL_TIME_BOUND=5_SECONDS): a new
 * verified prescription becomes visible on another authorised dashboard session with
 * p95 <= 5 seconds. The page re-reads the served queue every QUEUE_REFRESH_MS, so the
 * UI's contribution to that latency is bounded by this interval; the server's
 * contribution is measured in petcare_api/tests/test_pharmacy_dashboard_realtime.py.
 */
export const QUEUE_REFRESH_MS = 2000
