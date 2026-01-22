"""
Integration tests for WorkOn API Client against mock server
These tests require the mock server to be running on localhost:5001
"""

import unittest
import requests
import time
import subprocess
import sys
import os
from typing import Optional

# Import the module under test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from workon_api import WorkOnAPI, create_sample_rbga_data


class MockServerManager:
    """Helper class to manage mock server for integration tests"""

    def __init__(self, host="localhost", port=5001):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.process: Optional[subprocess.Popen] = None

    def start_server(self) -> bool:
        """Start the mock server and wait for it to be ready"""
        mock_server_dir = os.path.join(os.path.dirname(__file__), '../../mock-server')
        mock_server_script = os.path.join(mock_server_dir, 'mock_workon_server.py')

        if not os.path.exists(mock_server_script):
            print(f"Mock server script not found at: {mock_server_script}")
            return False

        try:
            # Start the mock server
            self.process = subprocess.Popen([
                sys.executable, mock_server_script
            ], cwd=mock_server_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait for server to start (max 10 seconds)
            for _ in range(20):
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=1)
                    if response.status_code == 200:
                        print("Mock server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    pass
                time.sleep(0.5)

            print("Mock server failed to start within timeout")
            self.stop_server()
            return False

        except Exception as e:
            print(f"Error starting mock server: {e}")
            return False

    def stop_server(self):
        """Stop the mock server"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def is_server_running(self) -> bool:
        """Check if the mock server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


class TestWorkOnAPIIntegration(unittest.TestCase):
    """Integration tests against the mock server"""

    @classmethod
    def setUpClass(cls):
        """Set up the mock server for all integration tests"""
        cls.server_manager = MockServerManager()

        # Try to start the server, or check if it's already running
        if not cls.server_manager.is_server_running():
            if not cls.server_manager.start_server():
                raise unittest.SkipTest("Could not start mock server for integration tests")

        cls.api_client = WorkOnAPI("http://localhost:5001", "test-key-id")

    @classmethod
    def tearDownClass(cls):
        """Clean up the mock server"""
        if hasattr(cls, 'server_manager'):
            cls.server_manager.stop_server()

    def setUp(self):
        """Set up each test"""
        # Verify server is still running
        if not self.server_manager.is_server_running():
            self.skipTest("Mock server is not running")

    def test_server_health_check(self):
        """Test that the mock server is responding"""
        response = requests.get("http://localhost:5001/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")

    def test_create_rbga_request_integration(self):
        """Test creating a full RBGA request against mock server"""
        rbga_data = create_sample_rbga_data()

        result = self.api_client.create_rbga_request(
            summary="Integration Test Request",
            applicant="john.doe",
            data=rbga_data,
            source_system="Integration Test"
        )

        # Verify response structure (mock server only returns key)
        self.assertIn("key", result)

        # Store the key for subsequent tests
        self.request_key = result["key"]
        self.assertIsInstance(self.request_key, str)
        self.assertTrue(self.request_key.startswith("RBGA-"))

    def test_create_draft_request_integration(self):
        """Test creating a draft request against mock server"""
        draft_data = {
            "rbga.field.termCheck": "yes",
            "rbga.field.description": "Integration test draft request",
            "rbga.field.workflowType": "Parallel"
        }

        result = self.api_client.create_draft_rbga_request(
            summary="Integration Test Draft",
            applicant="jane.doe",
            data=draft_data,
            source_system="Integration Test"
        )

        self.assertIn("key", result)
        self.assertTrue(result["key"].startswith("RBGA-"))

    def test_get_request_status_integration(self):
        """Test getting request status against mock server"""
        # First create a request with required fields
        rbga_data = {
            "rbga.field.description": "Status test request",
            "rbga.field.termCheck": "yes",
            "rbga.field.workflowType": "Serial",
            "rbga.field.approver1": {
                "approvers": [{"userid": "test.approver", "addAfterEnabled": True, "deleteFlag": "Yes", "description": "", "fixed": False, "removable": True, "ccList": ""}],
                "checkDuplicate": "false",
                "maxApprover": "20",
                "type": "1"
            }
        }
        create_result = self.api_client.create_rbga_request(
            "Status Test", "test.user", rbga_data
        )

        request_key = create_result["key"]

        # Now get its status
        status_result = self.api_client.get_request_status(request_key)

        # Verify status structure (mock server format)
        self.assertIn("status", status_result)
        self.assertIn("requestKey", status_result)

        # Status should be a list of internationalized values
        status_list = status_result["status"]
        self.assertIsInstance(status_list, list)
        self.assertGreater(len(status_list), 0)

        # Check that each status entry has the expected structure
        for status_entry in status_list:
            self.assertIn("i8nValue", status_entry)
            self.assertIn("localeName", status_entry)
            self.assertIsInstance(status_entry["i8nValue"], str)
            self.assertIsInstance(status_entry["localeName"], str)

    def test_get_workitem_detail_integration(self):
        """Test getting workitem details against mock server"""
        # Create a request first
        rbga_data = create_sample_rbga_data()
        create_result = self.api_client.create_rbga_request(
            "Detail Test Request", "detail.user", rbga_data
        )

        request_key = create_result["key"]

        # Test with custom fields and system fields
        custom_fields = [
            "rbga.field.description",
            "common.field.employee.companycode"
        ]
        system_fields = [
            "summary", "reporter", "created", "updated",
            "assignee", "status", "priority"
        ]

        details = self.api_client.get_workitem_detail(
            request_key=request_key,
            custom_fields=custom_fields,
            system_fields=system_fields,
            include_approval_history=True
        )

        # Verify response structure
        self.assertIn("key", details)
        self.assertEqual(details["key"], request_key)

        # Check for requested fields
        if "systemFields" in details:
            system_data = details["systemFields"]
            # At least some system fields should be present
            self.assertIsInstance(system_data, dict)

        if "customFields" in details:
            custom_data = details["customFields"]
            self.assertIsInstance(custom_data, dict)

        # Check for approval history if included
        if "approvalHistory" in details:
            self.assertIsInstance(details["approvalHistory"], list)

    def test_get_attachments_integration(self):
        """Test getting attachments against mock server"""
        # Create a request with attachments first
        rbga_data = create_sample_rbga_data()
        create_result = self.api_client.create_rbga_request(
            "Attachment Test Request", "attachment.user", rbga_data
        )

        request_key = create_result["key"]

        # Test getting all attachments
        attachments_result = self.api_client.get_attachments(
            request_key=request_key,
            user="attachment.user",
            send_all=True
        )

        # Verify response structure
        self.assertIsInstance(attachments_result, dict)
        # The mock server might return an empty attachments list or specific structure

    def test_missing_auth_header_error(self):
        """Test that requests without proper authentication fail"""
        # Create client without KeyId
        api_no_auth = WorkOnAPI("http://localhost:5001")

        rbga_data = {
            "rbga.field.description": "Test without auth",
            "rbga.field.termCheck": "yes",
            "rbga.field.workflowType": "Serial",
            "rbga.field.approver1": {
                "approvers": [{"userid": "test.approver", "addAfterEnabled": True, "deleteFlag": "Yes", "description": "", "fixed": False, "removable": True, "ccList": ""}],
                "checkDuplicate": "false",
                "maxApprover": "20",
                "type": "1"
            }
        }

        with self.assertRaises(requests.exceptions.HTTPError) as context:
            api_no_auth.create_rbga_request("No Auth Test", "test.user", rbga_data)

        # Should get 400 Bad Request for missing KeyId header
        self.assertIn("400", str(context.exception))

    def test_field_validation_error(self):
        """Test that invalid field data triggers validation errors"""
        # Use invalid data that should trigger validation
        invalid_data = {
            "rbga.field.termCheck": "invalid_value",  # Should be "yes" or "no"
            "rbga.field.workflowType": "InvalidType"  # Should be "Serial" or "Parallel"
        }

        with self.assertRaises(requests.exceptions.HTTPError) as context:
            self.api_client.create_rbga_request(
                "Invalid Data Test", "test.user", invalid_data
            )

        # Should get 400 Bad Request for validation error
        self.assertIn("400", str(context.exception))

    def test_nonexistent_request_status(self):
        """Test getting status for non-existent request"""
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            self.api_client.get_request_status("RBGA-NONEXISTENT")

        # Should get 404 Not Found
        self.assertIn("404", str(context.exception))

    def test_end_to_end_workflow(self):
        """Test a complete workflow from creation to status check"""
        # 1. Create a full request
        rbga_data = create_sample_rbga_data()
        rbga_data["rbga.field.description"] = "End-to-end workflow test"

        create_result = self.api_client.create_rbga_request(
            summary="E2E Workflow Test",
            applicant="workflow.user",
            data=rbga_data,
            source_system="E2E Test"
        )

        self.assertIn("key", create_result)
        request_key = create_result["key"]

        # 2. Get the request status
        status_result = self.api_client.get_request_status(request_key)
        self.assertIn("status", status_result)
        self.assertIn("requestKey", status_result)

        # 3. Get detailed information
        details = self.api_client.get_workitem_detail(
            request_key=request_key,
            custom_fields=["rbga.field.description"],
            system_fields=["summary", "status"],
            include_approval_history=False
        )

        self.assertEqual(details["key"], request_key)

        # 4. Try to get attachments
        try:
            attachments = self.api_client.get_attachments(
                request_key=request_key,
                user="workflow.user",
                send_all=True
            )
            # Should not raise an exception
            self.assertIsInstance(attachments, dict)
        except requests.exceptions.HTTPError as e:
            # Some mock implementations might not support this endpoint
            if "404" not in str(e):
                raise


class TestMockServerBehavior(unittest.TestCase):
    """Test specific mock server behaviors and features"""

    def setUp(self):
        """Set up API client"""
        # Skip if server is not running
        try:
            response = requests.get("http://localhost:5001/health", timeout=2)
            if response.status_code != 200:
                self.skipTest("Mock server not available")
        except requests.exceptions.RequestException:
            self.skipTest("Mock server not available")

        self.api_client = WorkOnAPI("http://localhost:5001", "test-key-id")

    def test_request_counter_functionality(self):
        """Test that the mock server increments request counters"""
        # Create multiple requests and verify they get different keys
        keys = set()

        for i in range(3):
            result = self.api_client.create_rbga_request(
                f"Counter Test {i}",
                "counter.user",
                {
                    "rbga.field.description": f"Test request {i}",
                    "rbga.field.termCheck": "yes",
                    "rbga.field.workflowType": "Serial",
                    "rbga.field.approver1": {
                        "approvers": [{"userid": "test.approver", "addAfterEnabled": True, "deleteFlag": "Yes", "description": "", "fixed": False, "removable": True, "ccList": ""}],
                        "checkDuplicate": "false",
                        "maxApprover": "20",
                        "type": "1"
                    }
                }
            )
            keys.add(result["key"])

        # All keys should be unique
        self.assertEqual(len(keys), 3)

        # All keys should follow the pattern RBGA-{number}
        for key in keys:
            self.assertTrue(key.startswith("RBGA-"))
            self.assertTrue(key[5:].isdigit())

    def test_draft_vs_full_request_difference(self):
        """Test that draft and full requests behave differently"""
        # Minimal data for draft (can be incomplete)
        draft_data = {"rbga.field.description": "Draft vs Full test"}

        # Complete data for full request (must have required fields)
        full_data = {
            "rbga.field.description": "Draft vs Full test",
            "rbga.field.termCheck": "yes",
            "rbga.field.workflowType": "Serial",
            "rbga.field.approver1": {
                "approvers": [
                    {
                        "addAfterEnabled": True,
                        "deleteFlag": "Yes",
                        "description": "",
                        "fixed": False,
                        "removable": True,
                        "userid": "test.approver",
                        "ccList": ""
                    }
                ],
                "checkDuplicate": "false",
                "maxApprover": "20",
                "type": "1"
            }
        }

        # Create a draft request (should work with minimal data)
        draft_result = self.api_client.create_draft_rbga_request(
            "Draft Test", "draft.user", draft_data
        )

        # Create a full request (needs complete data)
        full_result = self.api_client.create_rbga_request(
            "Full Test", "full.user", full_data
        )

        # Both should succeed but might have different properties
        self.assertIn("key", draft_result)
        self.assertIn("key", full_result)
        self.assertNotEqual(draft_result["key"], full_result["key"])


if __name__ == '__main__':
    # Print helpful information
    print("=" * 60)
    print("WorkOn API Integration Tests")
    print("=" * 60)
    print("These tests require the mock server to be running.")
    print("If the server is not running, tests will attempt to start it.")
    print("Make sure you're in the correct directory and have dependencies installed.")
    print("=" * 60)
    print()

    # Run the tests
    unittest.main(verbosity=2, buffer=True)