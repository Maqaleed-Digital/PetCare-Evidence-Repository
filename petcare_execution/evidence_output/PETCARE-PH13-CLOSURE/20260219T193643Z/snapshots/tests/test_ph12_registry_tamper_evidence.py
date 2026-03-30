import hashlib
import os
import unittest

def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

class TestPH12RegistryTamperEvidence(unittest.TestCase):
    def test_registry_sha256_file_matches(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reg = os.path.join(root, "ops", "ph12_gate_registry.json")
        sha = os.path.join(root, "ops", "ph12_gate_registry.sha256")

        self.assertTrue(os.path.exists(reg), f"missing {reg}")
        self.assertTrue(os.path.exists(sha), f"missing {sha}")

        expected = _sha256_file(reg)
        with open(sha, "r", encoding="utf-8") as f:
            line = f.read().strip()

        self.assertTrue(line, "sha256 file empty")
        got = line.split()[0]
        self.assertEqual(got, expected)

if __name__ == "__main__":
    unittest.main()
