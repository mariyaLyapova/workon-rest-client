"""
Comprehensive unit tests for WorkOn API Client
Tests all methods of the WorkOnAPI class with mock responses
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout

# Import the module under test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from workon_api import WorkOnAPI, create_sample_rbga_data


class TestWorkOnAPIInit(unittest.TestCase):
    """Test WorkOnAPI class initialization"""

    def test_init_with_required_params(self):
        """Test initialization with base_url only"""
        api = WorkOnAPI("https://api.example.com")

        self.assertEqual(api.base_url, "https://api.example.com")
        self.assertIsNone(api.key_id)
        self.assertEqual(api.timeout, 30)  # Default timeout
        self.assertIsInstance(api.session, requests.Session)
        self.assertEqual(api.session.headers['Content-Type'], WorkOnAPI.CONTENT_TYPE_JSON)
        self.assertNotIn('KeyId', api.session.headers)

    def test_init_with_all_params(self):
        """Test initialization with both base_url and key_id"""
        api = WorkOnAPI("https://api.example.com/", "test-key-123")

        self.assertEqual(api.base_url, "https://api.example.com")  # Should strip trailing slash
        self.assertEqual(api.key_id, "test-key-123")
        self.assertEqual(api.timeout, 30)  # Default timeout
        self.assertEqual(api.session.headers['Content-Type'], WorkOnAPI.CONTENT_TYPE_JSON)
        self.assertEqual(api.session.headers['KeyId'], "test-key-123")

    def test_constants_are_defined(self):
        """Test that all expected constants are defined"""
        self.assertEqual(WorkOnAPI.DEFAULT_SOURCE_SYSTEM, "WorkON")
        self.assertEqual(WorkOnAPI.DEFAULT_PROJECT_KEY, "RBGA")
        self.assertEqual(WorkOnAPI.DEFAULT_ISSUE_TYPE, "rbga.issuetype.default")
        self.assertEqual(WorkOnAPI.DEFAULT_PRIORITY, "default")
        self.assertEqual(WorkOnAPI.APPROVAL_HISTORY_YES, "yes")
        self.assertEqual(WorkOnAPI.CONTENT_TYPE_JSON, "application/json")

    def test_init_with_custom_timeout(self):
        """Test initialization with custom timeout value"""
        api = WorkOnAPI("https://api.example.com", "test-key", timeout=60)

        self.assertEqual(api.base_url, "https://api.example.com")
        self.assertEqual(api.key_id, "test-key")
        self.assertEqual(api.timeout, 60)  # Custom timeout
        self.assertEqual(api.session.headers['Content-Type'], WorkOnAPI.CONTENT_TYPE_JSON)
        self.assertEqual(api.session.headers['KeyId'], "test-key")


class TestCreateRBGARequest(unittest.TestCase):
    """Test create_rbga_request method"""

    def setUp(self):
        """Set up test fixtures"""
        self.api = WorkOnAPI("https://api.example.com", "test-key")
        self.sample_data = {
            "rbga.field.termCheck": "yes",
            "rbga.field.description": "Test request"
        }

    @patch('requests.Session.put')
    def test_create_rbga_request_success(self, mock_put):
        """Test successful RBGA request creation"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "RBGA-12345", "status": "created"}
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response

        result = self.api.create_rbga_request(
            summary="Test Summary",
            applicant="john.doe",
            data=self.sample_data,
            source_system="TestSystem"
        )

        # Verify the result
        self.assertEqual(result["key"], "RBGA-12345")
        self.assertEqual(result["status"], "created")

        # Verify the request was made correctly
        mock_put.assert_called_once()
        args, kwargs = mock_put.call_args

        # Check URL
        expected_url = "https://api.example.com/createrequest/create"
        self.assertEqual(args[0], expected_url)

        # Check payload
        expected_payload = {
            "summary": "Test Summary",
            "pkey": WorkOnAPI.DEFAULT_PROJECT_KEY,
            "issuetype": WorkOnAPI.DEFAULT_ISSUE_TYPE,
            "applicant": "john.doe",  # Should be lowercased
            "priority": WorkOnAPI.DEFAULT_PRIORITY,
            "sourceSystem": "TestSystem",
            "data": self.sample_data
        }
        self.assertEqual(kwargs['json'], expected_payload)

    @patch('requests.Session.put')
    def test_create_rbga_request_with_defaults(self, mock_put):
        """Test RBGA request creation with default source_system"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "RBGA-12346"}
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response

        self.api.create_rbga_request("Test", "JOHN.DOE", self.sample_data)

        # Check that applicant is lowercased and default source_system is used
        args, kwargs = mock_put.call_args
        payload = kwargs['json']
        self.assertEqual(payload['applicant'], "john.doe")
        self.assertEqual(payload['sourceSystem'], WorkOnAPI.DEFAULT_SOURCE_SYSTEM)

    @patch('requests.Session.put')
    def test_create_rbga_request_http_error(self, mock_put):
        """Test RBGA request creation with HTTP error"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = HTTPError("Bad Request")
        mock_put.return_value = mock_response

        with self.assertRaises(HTTPError):
            self.api.create_rbga_request("Test", "john.doe", self.sample_data)

    @patch('requests.Session.put')
    def test_create_rbga_request_connection_error(self, mock_put):
        """Test RBGA request creation with connection error"""
        mock_put.side_effect = ConnectionError("Connection failed")

        with self.assertRaises(ConnectionError):
            self.api.create_rbga_request("Test", "john.doe", self.sample_data)


class TestCreateDraftRBGARequest(unittest.TestCase):
    """Test create_draft_rbga_request method"""

    def setUp(self):
        self.api = WorkOnAPI("https://api.example.com", "test-key")
        self.draft_data = {"rbga.field.description": "Draft request"}

    @patch('requests.Session.put')
    def test_create_draft_rbga_request_success(self, mock_put):
        """Test successful draft RBGA request creation"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "RBGA-DRAFT-123", "status": "draft"}
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response

        result = self.api.create_draft_rbga_request(
            summary="Draft Summary",
            applicant="jane.doe",
            data=self.draft_data
        )

        self.assertEqual(result["key"], "RBGA-DRAFT-123")

        # Verify draft-specific payload
        args, kwargs = mock_put.call_args
        payload = kwargs['json']
        self.assertTrue(payload['draft'])
        self.assertEqual(args[0], "https://api.example.com/createdraftrequest/draft")


class TestGetRequestStatus(unittest.TestCase):
    """Test get_request_status method"""

    def setUp(self):
        self.api = WorkOnAPI("https://api.example.com", "test-key")

    @patch('requests.Session.get')
    def test_get_request_status_success(self, mock_get):
        """Test successful status retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "In Progress",
            "statusCode": "IN_PROGRESS",
            "internationalizedStatus": {
                "en": "In Progress",
                "de": "In Bearbeitung"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.api.get_request_status("RBGA-12345")

        self.assertEqual(result["status"], "In Progress")
        self.assertIn("internationalizedStatus", result)

        # Verify correct URL was called with timeout
        mock_get.assert_called_once_with("https://api.example.com/status/RBGA-12345", timeout=30)

    @patch('requests.Session.get')
    def test_get_request_status_not_found(self, mock_get):
        """Test status retrieval for non-existent request"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError("Not Found")
        mock_get.return_value = mock_response

        with self.assertRaises(HTTPError):
            self.api.get_request_status("RBGA-NONEXISTENT")


class TestGetWorkitemDetail(unittest.TestCase):
    """Test get_workitem_detail method"""

    def setUp(self):
        self.api = WorkOnAPI("https://api.example.com", "test-key")

    @patch('requests.Session.post')
    def test_get_workitem_detail_minimal(self, mock_post):
        """Test workitem detail retrieval with minimal parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "RBGA-12345", "summary": "Test Request"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.api.get_workitem_detail("RBGA-12345")

        self.assertEqual(result["key"], "RBGA-12345")

        # Verify URL and empty payload
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://api.example.com/workitemdetails/RBGA-12345")
        self.assertEqual(kwargs['json'], {})

    @patch('requests.Session.post')
    def test_get_workitem_detail_with_all_options(self, mock_post):
        """Test workitem detail retrieval with all optional parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "key": "RBGA-12345",
            "summary": "Test Request",
            "customFields": {"rbga.field.description": "Test description"},
            "systemFields": {"reporter": "john.doe"},
            "approvalHistory": [{"step": 1, "approver": "jane.doe"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        custom_fields = ["rbga.field.description", "rbga.field.termCheck"]
        system_fields = ["summary", "reporter", "status"]

        result = self.api.get_workitem_detail(
            request_key="RBGA-12345",
            custom_fields=custom_fields,
            system_fields=system_fields,
            include_approval_history=True
        )

        self.assertIn("approvalHistory", result)

        # Verify payload structure
        args, kwargs = mock_post.call_args
        expected_payload = {
            "approvalHistory": WorkOnAPI.APPROVAL_HISTORY_YES,
            "customFields": custom_fields,
            "systemFields": system_fields
        }
        self.assertEqual(kwargs['json'], expected_payload)


class TestGetAttachments(unittest.TestCase):
    """Test get_attachments method"""

    def setUp(self):
        self.api = WorkOnAPI("https://api.example.com", "test-key")

    @patch('requests.Session.post')
    def test_get_attachments_single(self, mock_post):
        """Test getting a specific attachment"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "attachments": [{
                "filename": "document.pdf",
                "content": "base64encodedcontent"
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.api.get_attachments(
            request_key="RBGA-12345",
            user="john.doe",
            attachment_name="document.pdf"
        )

        self.assertIn("attachments", result)

        # Verify payload
        args, kwargs = mock_post.call_args
        expected_payload = {
            "user": "john.doe",
            "sendAll": "false",
            "attachmentName": "document.pdf"
        }
        self.assertEqual(kwargs['json'], expected_payload)

    @patch('requests.Session.post')
    def test_get_attachments_all(self, mock_post):
        """Test getting all attachments"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"attachments": []}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        self.api.get_attachments(
            request_key="RBGA-12345",
            user="john.doe",
            send_all=True
        )

        # Verify payload excludes attachmentName when send_all=True
        args, kwargs = mock_post.call_args
        expected_payload = {
            "user": "john.doe",
            "sendAll": "true"
        }
        self.assertEqual(kwargs['json'], expected_payload)
        self.assertNotIn("attachmentName", kwargs['json'])


class TestCreateSampleRBGAData(unittest.TestCase):
    """Test create_sample_rbga_data function"""

    def test_create_sample_rbga_data_structure(self):
        """Test that sample data has correct structure"""
        data = create_sample_rbga_data()

        # Test that it's a dictionary
        self.assertIsInstance(data, dict)

        # Test required common fields
        self.assertIn("common.field.employee.firstname", data)
        self.assertIn("common.field.employee.lastname", data)
        self.assertIn("common.field.employee.department", data)

        # Test required RBGA fields
        self.assertIn("rbga.field.termCheck", data)
        self.assertIn("rbga.field.description", data)
        self.assertIn("rbga.field.workflowType", data)

        # Test complex fields
        self.assertIn("rbga.field.additionalFields", data)
        self.assertIn("rbga.field.attach", data)
        self.assertIn("rbga.field.approver1", data)

        # Verify data types
        self.assertIsInstance(data["rbga.field.additionalFields"], list)
        self.assertIsInstance(data["rbga.field.attach"], list)
        self.assertIsInstance(data["rbga.field.approver1"], dict)

    def test_sample_data_approver_structure(self):
        """Test approver data structure is correct"""
        data = create_sample_rbga_data()
        approver1 = data["rbga.field.approver1"]

        # Test approver structure
        self.assertIn("approvers", approver1)
        self.assertIn("checkDuplicate", approver1)
        self.assertIn("maxApprover", approver1)
        self.assertIn("type", approver1)

        # Test approver list structure
        approvers = approver1["approvers"]
        self.assertIsInstance(approvers, list)
        self.assertGreater(len(approvers), 0)

        # Test individual approver structure
        first_approver = approvers[0]
        required_fields = ["addAfterEnabled", "deleteFlag", "description",
                          "fixed", "removable", "userid", "ccList"]
        for field in required_fields:
            self.assertIn(field, first_approver)

    def test_sample_data_attachment_structure(self):
        """Test attachment data structure"""
        data = create_sample_rbga_data()
        attachments = data["rbga.field.attach"]

        self.assertIsInstance(attachments, list)
        self.assertGreater(len(attachments), 0)

        first_attachment = attachments[0]
        self.assertIn("filename", first_attachment)
        self.assertIn("file", first_attachment)

    def test_sample_data_additional_fields_structure(self):
        """Test additional fields data structure"""
        data = create_sample_rbga_data()
        additional_fields = data["rbga.field.additionalFields"]

        self.assertIsInstance(additional_fields, list)
        self.assertGreater(len(additional_fields), 0)

        first_field = additional_fields[0]
        self.assertIn("fields", first_field)
        self.assertIn("details", first_field)


class TestWorkOnAPIErrorHandling(unittest.TestCase):
    """Test error handling across all methods"""

    def setUp(self):
        self.api = WorkOnAPI("https://api.example.com", "test-key")

    @patch('requests.Session.put')
    def test_timeout_error(self, mock_put):
        """Test timeout error handling"""
        mock_put.side_effect = Timeout("Request timed out")

        with self.assertRaises(Timeout):
            self.api.create_rbga_request("Test", "user", {})

    @patch('requests.Session.get')
    def test_connection_error(self, mock_get):
        """Test connection error handling"""
        mock_get.side_effect = ConnectionError("Unable to connect")

        with self.assertRaises(ConnectionError):
            self.api.get_request_status("RBGA-123")

    @patch('requests.Session.post')
    def test_json_decode_error(self, mock_post):
        """Test handling of invalid JSON responses"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with self.assertRaises(json.JSONDecodeError):
            self.api.get_workitem_detail("RBGA-123")


class TestWorkOnAPIIntegration(unittest.TestCase):
    """Integration-style tests that verify method interactions"""

    def setUp(self):
        self.api = WorkOnAPI("https://api.example.com", "test-key")

    def test_session_reuse(self):
        """Test that the same session is reused across calls"""
        original_session = self.api.session

        # Make multiple calls and verify session is the same
        with patch.object(self.api.session, 'put') as mock_put, \
             patch.object(self.api.session, 'get') as mock_get:

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"key": "test"}
            mock_response.raise_for_status.return_value = None
            mock_put.return_value = mock_response
            mock_get.return_value = mock_response

            self.api.create_rbga_request("Test", "user", {})
            self.api.get_request_status("RBGA-123")

            self.assertIs(self.api.session, original_session)

    def test_headers_persistence(self):
        """Test that headers are maintained across requests"""
        with patch.object(self.api.session, 'put') as mock_put:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"key": "test"}
            mock_response.raise_for_status.return_value = None
            mock_put.return_value = mock_response

            self.api.create_rbga_request("Test", "user", {})

            # Verify that session headers are preserved
            self.assertEqual(self.api.session.headers['Content-Type'],
                           WorkOnAPI.CONTENT_TYPE_JSON)
            self.assertEqual(self.api.session.headers['KeyId'], "test-key")


if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)