PETCARE PHASE 2
DF-01 Network Baseline
Status: LOCKED

Projects:
- prj-maq-network-host-prod
- prj-maq-network-host-nonprod
- prj-petcare-sandbox

VPCs:
- vpc-petcare-prod
- vpc-petcare-nonprod
- vpc-petcare-sandbox

Subnets:
- snet-petcare-prod-mec2
- snet-petcare-nonprod-mec2
- snet-petcare-sandbox-mec2

Rules:
- no default network
- custom mode only
- firewall logging enabled
- flow logs enabled
- no ingress 0.0.0.0/0 except explicitly required later
- no peering between sandbox and prod
- sandbox isolated from prod by design
