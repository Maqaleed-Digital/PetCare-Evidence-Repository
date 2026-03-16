CROSS DOMAIN AUDIT PROPAGATION

Purpose:
Define minimum audit propagation requirements across orchestration flows.

Requirements:
- every cross-domain transition emits audit event
- event must retain source entity id
- event must retain target entity id when created
- actor identity must remain attached
- tenant scope must remain attached
