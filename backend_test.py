#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class PetCareAPITester:
    def __init__(self, base_url="https://petcare-evidence.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status=200, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json() if response.content else {}
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    elif isinstance(response_data, dict):
                        print(f"   Response: Dict with keys: {list(response_data.keys())[:5]}")
                    return True, response_data
                except:
                    # For text responses like markdown
                    print(f"   Response: Text content ({len(response.content)} bytes)")
                    return True, response.text
            else:
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'url': url,
                    'response': response.text[:200] if response.text else 'No response'
                })
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False, {}

        except Exception as e:
            self.failed_tests.append({
                'name': name,
                'expected': expected_status,
                'actual': 'Exception',
                'url': url,
                'response': str(e)
            })
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "")

    def test_evidence_endpoints(self):
        """Test evidence-related endpoints"""
        print("\n📁 Testing Evidence Endpoints...")
        
        # Test evidence packs
        success, packs = self.run_test("Evidence Packs", "GET", "evidence/packs")
        if success and packs:
            print(f"   Found {len(packs)} evidence pack(s)")
            
            # Test pack files for first pack
            if len(packs) > 0:
                pack_id = packs[0]['id']
                success, files = self.run_test(f"Pack Files ({pack_id})", "GET", f"evidence/packs/{pack_id}/files")
                if success and files:
                    print(f"   Found {len(files)} file(s) in pack")
                    
                    # Test file download for first file
                    if len(files) > 0:
                        file_name = files[0]['name']
                        self.run_test(f"File Download ({file_name})", "GET", f"evidence/packs/{pack_id}/file", params={'path': file_name})

    def test_governance_endpoints(self):
        """Test governance-related endpoints"""
        print("\n🛡️ Testing Governance Endpoints...")
        
        success, summary = self.run_test("Governance Summary", "GET", "governance/summary")
        if success and summary:
            print(f"   Found {len(summary)} governance section(s)")

    def test_security_endpoints(self):
        """Test security-related endpoints"""
        print("\n🔒 Testing Security Endpoints...")
        
        self.run_test("RLS Status", "GET", "security/rls")
        self.run_test("Bypass RLS Roles", "GET", "security/bypassrls")
        self.run_test("Security Policies", "GET", "security/policies")
        self.run_test("Role Grants", "GET", "security/grants")

    def test_audit_endpoints(self):
        """Test audit-related endpoints"""
        print("\n📋 Testing Audit Endpoints...")
        
        self.run_test("Audit Events", "GET", "audit/events")
        self.run_test("Audit Event Types", "GET", "audit/event-types")
        self.run_test("Audit Event Catalog", "GET", "audit/event-catalog")
        
        # Test with filters
        self.run_test("Audit Events (filtered)", "GET", "audit/events", params={'severity': 'info'})

    def test_explainability_endpoints(self):
        """Test explainability-related endpoints"""
        print("\n🧠 Testing Explainability Endpoints...")
        
        self.run_test("Explainability Runs", "GET", "explainability/runs")
        self.run_test("Explainability Logs", "GET", "explainability/logs")
        self.run_test("Explainability Schema", "GET", "explainability/schema")

    def test_report_endpoints(self):
        """Test report-related endpoints"""
        print("\n📄 Testing Report Endpoints...")
        
        self.run_test("Day 3 Report", "GET", "report/day3")

    def run_all_tests(self):
        """Run all API tests"""
        print(f"🚀 Starting PetCare API Tests")
        print(f"   Base URL: {self.base_url}")
        print(f"   API URL: {self.api_url}")
        
        # Test all endpoints
        self.test_root_endpoint()
        self.test_evidence_endpoints()
        self.test_governance_endpoints()
        self.test_security_endpoints()
        self.test_audit_endpoints()
        self.test_explainability_endpoints()
        self.test_report_endpoints()
        
        # Print results
        print(f"\n📊 Test Results:")
        print(f"   Tests run: {self.tests_run}")
        print(f"   Tests passed: {self.tests_passed}")
        print(f"   Tests failed: {len(self.failed_tests)}")
        print(f"   Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"   - {test['name']}: Expected {test['expected']}, got {test['actual']}")
                print(f"     URL: {test['url']}")
                print(f"     Response: {test['response']}")
        
        return len(self.failed_tests) == 0

def main():
    tester = PetCareAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())