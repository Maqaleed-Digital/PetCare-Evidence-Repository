export function requireHumanApproval(actionType) {

  const restrictedActions = [
    "diagnosis",
    "prescription",
    "treatment_authorization",
    "consultation_closure"
  ];

  if (restrictedActions.includes(actionType)) {
    return {
      approved: false,
      reason: "Human approval required"
    };
  }

  return {
    approved: true
  };
}
