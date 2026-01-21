"""
Bosch WorkOn API Client
Simple Python module to interact with Bosch WorkOn REST API
"""

import requests
import json
from typing import Dict, Any, Optional, List


class WorkOnAPI:
    """Simple client for Bosch WorkOn REST API"""

    # API Constants
    DEFAULT_SOURCE_SYSTEM = "WorkON"
    DEFAULT_PROJECT_KEY = "RBGA"
    DEFAULT_ISSUE_TYPE = "rbga.issuetype.default"
    DEFAULT_PRIORITY = "default"
    APPROVAL_HISTORY_YES = "yes"

    # Content Type
    CONTENT_TYPE_JSON = "application/json"

    def __init__(self, base_url: str, key_id: str = None):
        """
        Initialize the WorkOn API client

        Args:
            base_url: The base URL for the WorkOn API
            key_id: Key ID for WorkOn API (required for authentication)
        """
        self.base_url = base_url.rstrip('/')
        self.key_id = key_id
        self.session = requests.Session()

        # Set up default headers
        self.session.headers.update({
            'Content-Type': self.CONTENT_TYPE_JSON
        })

        # Set up authentication headers if provided
        if self.key_id:
            self.session.headers.update({
                'KeyId': self.key_id
            })

    def create_rbga_request(self, summary: str, applicant: str, data: Dict[str, Any], source_system: str = DEFAULT_SOURCE_SYSTEM) -> Dict[str, Any]:
        """
        Create a new WorkOn request using RBGA template (based on official API documentation)

        Args:
            summary: Summary of the Workitem
            applicant: NT id of the applicant who creates the request (lowercase)
            data: Dictionary containing RBGA-specific data fields
            source_system: Your System Name (which calls this API)

        Returns:
            Dictionary with the created request key

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}/createrequest/create"

        # Prepare the request payload according to RBGA documentation
        payload = {
            "summary": summary,
            "pkey": self.DEFAULT_PROJECT_KEY,
            "issuetype": self.DEFAULT_ISSUE_TYPE,
            "applicant": applicant.lower(),
            "priority": self.DEFAULT_PRIORITY,
            "sourceSystem": source_system,
            "data": data
        }

        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise

    def create_draft_rbga_request(self, summary: str, applicant: str, data: Dict[str, Any], source_system: str = DEFAULT_SOURCE_SYSTEM) -> Dict[str, Any]:
        """
        Create a draft WorkOn request using RBGA template (can be saved without full validation)

        Args:
            summary: Summary of the Workitem
            applicant: NT id of the applicant who creates the request (lowercase)
            data: Dictionary containing RBGA-specific data fields (partial data allowed)
            source_system: Your System Name (which calls this API)

        Returns:
            Dictionary with the created draft request key

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}/createdraftrequest/draft"

        # Prepare the draft payload - similar structure but with less validation
        payload = {
            "summary": summary,
            "pkey": self.DEFAULT_PROJECT_KEY,
            "issuetype": self.DEFAULT_ISSUE_TYPE,
            "applicant": applicant.lower(),
            "priority": self.DEFAULT_PRIORITY,
            "sourceSystem": source_system,
            "data": data,
            "draft": True  # Indicate this is a draft request
        }

        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise

    def get_request_status(self, request_key: str) -> Dict[str, Any]:
        """
        Get the status of an existing WorkOn request

        Args:
            request_key: The key of the request (e.g., "RBGA-123")

        Returns:
            Dictionary with internationalized status information

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}/status/{request_key}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise

    def get_workitem_detail(self, request_key: str, custom_fields: Optional[List[str]] = None,
                           system_fields: Optional[List[str]] = None, include_approval_history: bool = False) -> Dict[str, Any]:
        """
        Get detailed information about a WorkOn request

        Args:
            request_key: The key of the request (e.g., "RBGA-123")
            custom_fields: List of custom RBGA fields to retrieve (e.g., ["rbga.field.description"])
            system_fields: List of system fields to retrieve (e.g., ["summary", "reporter"])
            include_approval_history: Whether to include approval history

        Returns:
            Dictionary with detailed request information

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}/workitemdetails/{request_key}"

        payload = {}
        if include_approval_history:
            payload["approvalHistory"] = self.APPROVAL_HISTORY_YES
        if custom_fields:
            payload["customFields"] = custom_fields
        if system_fields:
            payload["systemFields"] = system_fields

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise


    def get_attachments(self, request_key: str, user: str, attachment_name: Optional[str] = None, send_all: bool = False) -> Dict[str, Any]:
        """
        Get attachments for a WorkOn request

        Args:
            request_key: The key of the request (e.g., "RBGA-123")
            user: NT ID of the user requesting attachments
            attachment_name: Name of specific attachment to retrieve
            send_all: Whether to retrieve all attachments

        Returns:
            Dictionary with attachment content (Base64 encoded)

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}/workitemattachments/{request_key}"

        payload = {
            "user": user,
            "sendAll": str(send_all).lower()
        }

        if not send_all and attachment_name:
            payload["attachmentName"] = attachment_name

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise


def create_sample_rbga_data() -> Dict[str, Any]:
    """
    Create sample RBGA data structure according to documentation (similar to Java version)
    """
    rbga_data = {}

    # Common employee fields
    rbga_data["common.field.employee.firstname"] = "John"
    rbga_data["common.field.employee.lastname"] = "Doe"
    rbga_data["common.field.employee.department"] = "IT"
    rbga_data["common.field.employee.costcenter"] = "CC001"
    rbga_data["common.field.employee.location"] = "Stuttgart"

    # RBGA-specific fields
    rbga_data["rbga.field.termCheck"] = "yes"
    rbga_data["rbga.field.description"] = "Request for new software licenses"
    rbga_data["rbga.field.comments"] = "Urgent approval needed for project"
    rbga_data["rbga.field.workflowType"] = "Serial"
    rbga_data["rbga.field.wf2"] = "Serial"
    rbga_data["rbga.field.wf3"] = "Serial"
    rbga_data["rbga.field.parallelWorkflowSel"] = "Only one Approver has to approve"
    rbga_data["rbga.field.parallelWorkflowSel2"] = "Only one Approver has to approve"
    rbga_data["rbga.field.parallelWorkflowSel3"] = "Only one Approver has to approve"
    rbga_data["rbga.field.tempNew"] = "New Request"
    rbga_data["rbga.field.approvalstep"] = "One Step Approval"

    # External link
    rbga_data["rbga.field.externalLink"] = "https://www.bosch.com"

    # Additional fields
    additional_fields = [
        {
            "fields": "Target revision",
            "details": "Value1"
        },
        {
            "fields": "Preview link",
            "details": "https://www.bosch.com"
        }
    ]
    rbga_data["rbga.field.additionalFields"] = additional_fields

    # Attachments
    attachments = [
        {
            "filename": "filename.ext",
            "file": "Base64EncodedString"
        }
    ]
    rbga_data["rbga.field.attach"] = attachments

    # Primary approver (rbga.field.approver1)
    approvers1 = [
        {
            "addAfterEnabled": True,
            "deleteFlag": "Yes",
            "description": "",
            "fixed": False,
            "removable": True,
            "userid": "mrj6cob",
            "ccList": ""
        },
        {
            "addAfterEnabled": True,
            "deleteFlag": "Yes",
            "description": "",
            "fixed": False,
            "removable": True,
            "userid": "mrj6cob",
            "ccList": ""
        }
    ]

    approver1 = {
        "approvers": approvers1,
        "checkDuplicate": "false",
        "maxApprover": "20",
        "type": "1"
    }
    rbga_data["rbga.field.approver1"] = approver1

    # When approved workflow
    approvers_approved = [
        {
            "addAfterEnabled": True,
            "deleteFlag": "Yes",
            "description": "",
            "fixed": False,
            "removable": True,
            "userid": "mrj6cob",
            "ccList": ""
        }
    ]

    when_approved = {
        "approvers": approvers_approved,
        "checkDuplicate": "false",
        "maxApprover": "20",
        "type": "1"
    }
    rbga_data["rbga.field.whenApproved"] = when_approved

    # When declined workflow
    approvers_declined = [
        {
            "addAfterEnabled": True,
            "deleteFlag": "Yes",
            "description": "",
            "fixed": False,
            "removable": True,
            "userid": "mrj6cob",
            "ccList": ""
        }
    ]

    when_declined = {
        "approvers": approvers_declined,
        "checkDuplicate": "false",
        "maxApprover": "20",
        "type": "1"
    }
    rbga_data["rbga.field.whenDeclined"] = when_declined

    return rbga_data


# Example usage (for testing)
if __name__ == "__main__":
    try:
        print("=== RBGA API Demo: 5 Core Operations (Python) ===\n")

        # Initialize API client - pointing to mock server
        api_client = WorkOnAPI("http://localhost:5001", "test-key-id")
        # For production: api_client = WorkOnAPI("https://workon-api.bosch.com", "your-key-id-here")

        # Example RBGA data structure according to documentation
        rbga_data = create_sample_rbga_data()

        # 1. Create Full Request (complete data with validation)
        print("1. Creating full RBGA request...")
        result = api_client.create_rbga_request(
            "Request for Software License Approval",
            "john.doe",
            rbga_data,
            "Python API Client"
        )
        print(f"Full request created successfully: {result}\n")

        # 2. Create Draft Request (partial data allowed)
        print("2. Creating RBGA draft request...")
        draft_data = {
            "rbga.field.termCheck": "yes",
            "rbga.field.description": "Draft request for software licenses",
            "rbga.field.workflowType": "Parallel"
        }

        draft_result = api_client.create_draft_rbga_request(
            "Draft: Software License Request",
            "john.doe",
            draft_data,
            "Python API Client"
        )
        print(f"Draft created: {draft_result}\n")

        # If creation was successful, demonstrate the other 3 operations
        if 'key' in result:
            request_key = result['key']

            # 3. Get Status
            print(f"3. Getting status for request: {request_key}")
            status = api_client.get_request_status(request_key)
            print(f"Request status: {status}\n")

            # 4. Get Request Details
            print(f"4. Getting detailed information for request: {request_key}")
            custom_fields = [
                "rbga.field.description",
                "common.field.employee.companycode"
            ]
            system_fields = [
                "summary",
                "reporter",
                "created",
                "updated",
                "assignee",
                "status",
                "priority"
            ]
            details = api_client.get_workitem_detail(request_key, custom_fields, system_fields, True)
            print(f"Request details: {details}\n")

            # 5. Get Workitem Attachments
            print(f"5. Getting attachments for request: {request_key}")
            attachments = api_client.get_attachments(request_key, "john.doe", None, True)
            print(f"Attachments: {attachments}")

        print("\n=== All 5 RBGA operations completed successfully! ===")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()