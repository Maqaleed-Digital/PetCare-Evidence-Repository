export function routeSurfaceRequest(surfaceType, requestPayload) {

  const supportedSurfaces = [
    "vet_surface",
    "admin_surface",
    "pharmacy_surface",
    "emergency_surface"
  ];

  if (!supportedSurfaces.includes(surfaceType)) {
    throw new Error("Unsupported AI surface");
  }

  return {
    surface: surfaceType,
    request: requestPayload,
    routed: true
  };
}
