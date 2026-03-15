export const REFUND_RECONCILIATION_CONTROLS = {
  controlName: "refund_reconciliation_controls",
  controls: [
    "refund_requires_authorized_review",
    "refund_reason_recorded",
    "daily_reconciliation_supported",
    "exception_flags_recorded",
    "audit_log_capture_confirmed",
  ],
  refundReconciliationStatus: "pass",
} as const
