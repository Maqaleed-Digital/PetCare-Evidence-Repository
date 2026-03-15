export function injectSurfaceContext(surface, context) {

  return {
    surfaceContext: surface,
    domainContext: context,
    timestamp: new Date().toISOString()
  };

}
