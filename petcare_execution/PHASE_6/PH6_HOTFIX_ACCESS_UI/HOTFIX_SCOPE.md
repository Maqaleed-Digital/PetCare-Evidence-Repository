PH6 HOTFIX SCOPE

PROBLEM
- public users can access landing page only
- app routes return forbidden requiring vet/admin
- UI not strong enough for pilot activation

OBJECTIVES
- preserve RBAC and governance
- separate public routes from protected routes
- add role-aware app routing
- replace raw forbidden response with proper unauthorized UI
- uplift visual quality for pilot readiness

NON-NEGOTIABLES
- no weakening of protected vet/admin access
- no DB bypass
- no fake roles
- fail-closed remains active
