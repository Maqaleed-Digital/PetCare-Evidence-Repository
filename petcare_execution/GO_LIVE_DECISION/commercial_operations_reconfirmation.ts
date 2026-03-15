export const COMMERCIAL_OPERATIONS_RECONFIRMATION = {
  commercialOperationsReconfirmed: true,
  checks: [
    "pharmacy_operator_confirmed",
    "billing_and_payment_go_live_complete",
    "partner_network_operational_closure_complete",
    "routing_and_settlement_controls_confirmed",
    "commercial_access_controls_confirmed",
  ],
  commercialOperationsStatus: "pass",
} as const
