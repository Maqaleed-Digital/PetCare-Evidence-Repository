# D2M-SIGNIN-REDIRECT-COLD-DEV (ar-desktop, run 1 of the per-project acceptance series) — INTERMITTENT test/runtime finding

Observed: test timeout inside the shared `newOwner` fixture (fixtures.ts:108) — `expect(page).toHaveURL(/\/owner/)` saw
`/signin` for 30 s. The retained page snapshot (`error-context.md`) shows the sign-in SUCCEEDED (navigation carries the signed-in
owner's name and a sign-out button) but the page was not redirected. The server log of the same series shows `next dev` "Fast
Refresh had to perform a full reload" during the sign-in phase of a cold dev server.

Cause: development-server artefact (Fast Refresh full reload discarding the client-side redirect on a cold compile), not J-O8
code and not an application defect reachable in a production build. The fixture's assertion is NOT weakened.
Disposition: re-run ar-desktop unchanged -> PASS (`../../jo8-cod-ar-desktop.json`). The trace zip of run 1 was retained in the
runner's scratch area (binary, not committed).
