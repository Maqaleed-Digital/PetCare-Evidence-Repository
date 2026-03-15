export function aiOverrideTracker(action) {

  return {
    eventType: "ai_override",
    timestamp: new Date().toISOString(),
    agent: action.agent,
    reason: action.reason || "manual_override",
    assistiveOnly: true
  };

}
