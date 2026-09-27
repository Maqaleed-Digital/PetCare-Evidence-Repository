"""U29 (AC-FR-06 video default-off hardening) perturbations. Run: python3 perturb_u29.py <checkout root>.

The mandated one ADDS A NEW TRACKED configuration source outside the v1.2 filename-pattern families that enables the
video switch in a non-test profile, and proves the hardened test discovers it with no filename added to any list.
New files are staged with `git add` (tracked) and removed from the index and disk afterwards.
"""
import os
import re
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
T = ["python3", "-m", "pytest",
     "petcare_api/tests/test_sq2_video_nonprod.py::test_the_video_switch_defaults_off_in_every_non_test_configuration",
     "-q", "-p", "no:cacheprovider"]
# The v1.2 (U27) discovery patterns, reproduced ONLY to prove the new source lies outside them.
V12 = re.compile(r"(^|/)(Dockerfile[^/]*|[^/]*\.env[^/]*|cloudbuild[^/]*\.ya?ml|docker-compose[^/]*\.ya?ml|"
                 r"compose[^/]*\.ya?ml|next\.config\.[mc]?[jt]s|\.github/workflows/[^/]+\.ya?ml|[^/]*\.tf|"
                 r"[^/]*\.tfvars|app\.ya?ml|Procfile)$")
NEW_PROFILE = "ops/profiles/staging-runtime.yaml"
P = [
 ("P-NEW-TRACKED-PROFILE-ENABLES-VIDEO", [], {NEW_PROFILE: "# staging runtime profile (non-test)\nenv:\n"
                                              "  PETCARE_PERSISTENCE_MODE: postgres\n"
                                              "  PETCARE_VIDEO_CAPABILITY_ENABLED: \"true\"\n"}),
 ("P-NEW-TRACKED-SECOND-READER", [], {"petcare_api/video_override.py":
                                      "import os\nFORCE = os.environ.get(\"PETCARE_VIDEO_CAPABILITY_ENABLED\")\n"}),
 ("P-SWITCH-DEFAULT-ON", [("petcare_api/video.py", "SWITCH_DEFAULT = False", "SWITCH_DEFAULT = True")], {}),
]
assert not V12.search(NEW_PROFILE), "the new profile must lie outside the v1.2 pattern families"
res = []
for pid, edits, new_files in P:
    orig = {f: open(R + f, 'rb').read() for f, _, _ in edits}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        for f, body in new_files.items():
            assert not os.path.exists(R + f), f
            os.makedirs(os.path.dirname(R + f), exist_ok=True)
            open(R + f, 'w').write(body)
            subprocess.run(["git", "add", "--", f], cwd=R, check=True)
            assert f in subprocess.run(["git", "ls-files", "--", f], cwd=R, capture_output=True, text=True).stdout
        rc = subprocess.run(T, cwd=R, capture_output=True, text=True, timeout=600)
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "failed" in l or "passed" in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
        for f in new_files:
            subprocess.run(["git", "rm", "-q", "--cached", "--", f], cwd=R)
            os.remove(R + f)
            d = os.path.dirname(R + f)
            while d.rstrip("/") != R.rstrip("/") and os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d); d = os.path.dirname(d)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    for f in new_files: assert not os.path.exists(R + f)
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
