# Plaintext absence — measured by fingerprint

Located by hashing every 25-byte window of every tracked text file and
comparing the digest. The value is never searched for, printed or stored.

```
TRACKED_FILES                  = 3706
SCANNED_TEXT                   = 3702
SKIPPED_BINARY_OR_LARGE        = 4
PLAINTEXT_IN_TRACKED_FILES     = 0
FINGERPRINT_OCCURRENCES        = 4   (implementation, tests, evidence — legitimate)
```

Before this change the same scan reported **11 occurrences across 5 files**:
the guard comparand and a docstring in `auth.py`, two test constants, five
scanner fixtures, and one line of governance prose.

## Boundary

```
CURRENT_HEAD_TRACKED_PLAINTEXT = 0    <- what this PR achieves
ALL_GIT_HISTORY_PLAINTEXT      = NOT 0 <- Gate-5, still outstanding
```
