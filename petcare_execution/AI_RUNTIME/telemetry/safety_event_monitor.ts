export function safetyEventMonitor(signal) {

  return {
    eventType: "safety_event",
    severity: signal.level || "info",
    description: signal.description,
    assistiveOnly: true
  };

}
