# Gate-5 Section 1 — session + tooling

```
PWD_OK                  = YES  (/Users/waheebmahmoud/dev/petcare-evidence-repository)
PERMISSIONS_CMD_RUN     = NO   (/permissions not invoked)
SETTINGS_READ_DIRECTLY  = YES  (.claude/settings.local.json, read under bash)
GRANT_PROTECTION_PUT    = PRESENT
GRANT_FORCE_WITH_LEASE  = PRESENT
SPONSOR_AUTHORIZATION   = PROJECT_SCOPED_TEMPORARY_INSTALLED
GRANTS_COPIED_TO_GLOBAL = NO
SHELL_FOR_EVIDENCE      = bash
MIRROR_FETCHED          = NO
```

## Sponsor grants — verbatim, exact-string matched

```
Bash(gh api -X PUT repos/Maqaleed-Digital/PetCare-Evidence-Repository/branches/main/protection*)
Bash(git push --force-with-lease*)
```

Both present in the repository's own `.claude/settings.local.json`, whose
`permissions.allow` contains these two entries and nothing else. Treated as
Sponsor-installed, project-scoped authorization for this Gate-5 run. Not copied
into `~/.claude`.

## git-filter-repo — recovered, not a stop

The earlier preflight reported `GIT_FILTER_REPO_INSTALLED = NO`. That was a
`PATH` result, not an installation result: the package was already present and
only its entry point was unreachable.

```
python3 -m pip install --user git-filter-repo
  -> Requirement already satisfied: git-filter-repo 2.47.0
     /Users/waheebmahmoud/Library/Python/3.13/lib/python/site-packages

entry point: /Users/waheebmahmoud/Library/Python/3.13/bin/git-filter-repo
```

`brew install git-filter-repo` was refused by the session's command classifier;
the `pip --user` fallback in the authorized chain resolved it. With
`PATH=$HOME/Library/Python/3.13/bin:$PATH`:

```
command -v git-filter-repo -> /Users/waheebmahmoud/Library/Python/3.13/bin/git-filter-repo
git filter-repo --version  -> a40bce548d2c
GIT_FILTER_REPO_STATUS = OK
```

Every later Gate-5 step must export that `PATH` prefix; the binary is not on the
default `PATH`.

## Unchanged

```
PRODUCTION_MUTATED = NO · LIVE_DB_MUTATED = NO · GCP_MUTATED = NO
REMOTE_MUTATED = NO · IRREVERSIBLE_HISTORY_ACTION_PERFORMED = NO
```
