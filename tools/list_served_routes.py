#!/usr/bin/env python3
"""
Enumerate routes the SERVED application object exposes.
Usage:
  python3 tools/list_served_routes.py <module.path:app_attr>

MVC-BUILD-W1. The served object is the one the deployment runs, not one
assembled for a test: petcare_api/Dockerfile serves `uvicorn main:app`, so the
canonical invocation (repository root, TEST/LOCAL configuration only) is

  SECRET_KEY=test-only-not-a-deployed-secret PETCARE_SECRET_MODE=environment \
  PETCARE_PERSISTENCE_MODE=memory PETCARE_DOCUMENT_STORE_MODE=local \
  PETCARE_DOCUMENT_ROOT="$TMPDIR/petcare-test-documents" PYTHONPATH=petcare_api \
  python3 tools/list_served_routes.py main:app > requirements/served_routes.json

Those are the non-production values the repository-root conftest.py sets; none
is a credential and none reaches a deployed store.
"""
import importlib
import json
import sys


def walk(routes, prefix=""):
    for r in routes:
        path = prefix + getattr(r, "path", "")
        sub = getattr(r, "routes", None)
        endpoint = getattr(r, "endpoint", None)
        if sub:
            yield from walk(sub, path)
        elif endpoint is not None:
            yield {
                "path": path,
                "methods": sorted(getattr(r, "methods", None) or []),
                "endpoint": f"{endpoint.__module__}:{endpoint.__qualname__}",
            }


def main(target):
    mod, attr = target.split(":")
    app = getattr(importlib.import_module(mod), attr)
    rows = sorted(
        walk(app.routes),
        key=lambda x: (x["path"], x["methods"], x["endpoint"])
    )
    print(json.dumps(
        {"app": target, "routes": rows},
        indent=2,
        sort_keys=True
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
