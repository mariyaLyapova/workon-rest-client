"""
Mock HTTP Server for Bosch WorkOn API with RBGA Template Support
Based on the official WorkOn REST API documentation
This server simulates the WorkOn API endpoints for testing purposes.
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import uuid
import json
import base64
from typing import Dict, Any, List

app = Flask(__name__)

# In-memory storage for mock data
requests_db = {}
attachments_db = {}

# RBGA-specific field mappings from the documentation
RBGA_FIELDS = {
    # Common employee fields
    "common.field.employee.firstname": {"type": "string", "required": False},
    "common.field.employee.lastname": {"type": "string", "required": False},
    "common.field.employee.department": {"type": "string", "required": False},
    "common.field.employee.costcenter": {"type": "string", "required": False},
    "common.field.employee.location": {"type": "string", "required": False},

    # RBGA-specific fields
    "rbga.field.termCheck": {"type": "enum", "options": ["yes", "no"], "required": True},
    "rbga.field.description": {"type": "string", "required": True},
    "rbga.field.comments": {"type": "string", "required": False},
    "rbga.field.workflowType": {"type": "enum", "options": ["Parallel", "Serial"], "required": True},
    "rbga.field.wf2": {"type": "enum", "options": ["Parallel", "Serial"], "required": False},
    "rbga.field.wf3": {"type": "enum", "options": ["Parallel", "Serial"], "required": False},
    "rbga.field.parallelWorkflowSel": {"type": "enum", "options": ["One approver approves the request", "All the Approvers has to approve"], "required": False},
    "rbga.field.parallelWorkflowSel2": {"type": "enum", "options": ["One approver approves the request", "All the Approvers has to approve"], "required": False},
    "rbga.field.parallelWorkflowSel3": {"type": "enum", "options": ["One approver approves the request", "All the Approvers has to approve"], "required": False},
    "rbga.field.tempNew": {"type": "enum", "options": ["New Request"], "required": False},
    "rbga.field.approvalstep": {"type": "enum", "options": ["One Step Approval", "Multi Step Approval"], "required": False},
    "rbga.field.additionalFields": {"type": "array", "required": False},
    "rbga.field.approver1": {"type": "object", "required": True},
    "rbga.field.attach": {"type": "array", "required": False},
    "rbga.field.item": {"type": "array", "required": False},
    "rbga.field.grid": {"type": "array", "required": False}
}

def generate_request_key() -> str:
    """Generate a unique RBGA request key in the format RBGA-XXX"""
    # Get highest existing number
    max_num = 0
    for key in requests_db.keys():
        if key.startswith("RBGA-"):
            try:
                num = int(key.split("-")[1])
                max_num = max(max_num, num)
            except:
                pass
    return f"RBGA-{max_num + 1}"

def validate_rbga_request(payload: Dict[str, Any]) -> tuple[bool, str]:
    """Validate RBGA request payload according to documentation"""
    # Check required top-level fields
    required_fields = ["summary", "pkey", "issuetype", "applicant", "priority", "sourceSystem", "data"]
    for field in required_fields:
        if field not in payload:
            return False, f"Missing required field: {field}"

    # Validate specific field values
    if payload.get("pkey") != "RBGA":
        return False, "pkey must be 'RBGA'"

    if payload.get("issuetype") != "rbga.issuetype.default":
        return False, "issuetype must be 'rbga.issuetype.default'"

    if payload.get("priority") != "default":
        return False, "priority must be 'default'"

    # Validate data fields
    data = payload.get("data", {})

    # Check required RBGA fields
    rbga_required = ["rbga.field.termCheck", "rbga.field.description", "rbga.field.workflowType", "rbga.field.approver1"]
    for field in rbga_required:
        if field not in data:
            return False, f"Missing required RBGA field: {field}"

    # Validate field values
    if data.get("rbga.field.termCheck") not in ["yes", "no"]:
        return False, "rbga.field.termCheck must be 'yes' or 'no'"

    workflow_type = data.get("rbga.field.workflowType")
    if workflow_type not in ["Parallel", "Serial"]:
        return False, "rbga.field.workflowType must be 'Parallel' or 'Serial'"

    # Validate approver structure
    approver1 = data.get("rbga.field.approver1")
    if not isinstance(approver1, dict) or "approvers" not in approver1:
        return False, "rbga.field.approver1 must contain 'approvers' array"

    approvers = approver1.get("approvers", [])
    if not isinstance(approvers, list) or len(approvers) == 0:
        return False, "rbga.field.approver1.approvers must be a non-empty array"

    # Validate each approver
    for i, approver in enumerate(approvers):
        if not isinstance(approver, dict):
            return False, f"Approver {i} must be an object"

        required_approver_fields = ["userid", "description"]
        for field in required_approver_fields:
            if field not in approver:
                return False, f"Approver {i} missing required field: {field}"

    return True, ""

@app.route('/createdraftrequest/draft', methods=['PUT'])
def create_draft_request():
    """Create Draft Request API - Creates a draft WorkON request with relaxed validation"""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "Request body is required"}), 400

        # Basic validation for draft - less strict than full request
        required_fields = ["summary", "pkey", "applicant"]
        for field in required_fields:
            if field not in payload:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        if payload.get("pkey") != "RBGA":
            return jsonify({"error": "pkey must be 'RBGA'"}), 400

        # Generate unique draft request key
        request_key = f"RBGA-DRAFT-{str(uuid.uuid4())[:8].upper()}"

        # Create the draft request object with minimal validation
        created_request = {
            "key": request_key,
            "summary": payload["summary"],
            "pkey": payload["pkey"],
            "issuetype": payload.get("issuetype", "rbga.issuetype.default"),
            "applicant": payload["applicant"],
            "priority": payload.get("priority", "default"),
            "sourceSystem": payload.get("sourceSystem", "WorkON"),
            "data": payload.get("data", {}),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "Draft",
            "resolution": None,
            "workflow_stage": "Draft",
            "approvals": [],
            "is_draft": True
        }

        # Store in mock database
        requests_db[request_key] = created_request

        # Return success response
        return jsonify({
            "success": True,
            "message": "RBGA draft request created successfully",
            "key": request_key,
            "status": "Draft",
            "created_at": created_request["created_at"]
        }), 201

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/createrequest/create', methods=['PUT'])
def create_request():
    """Create Request API - Creates a new WorkON request"""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "Request body is required"}), 400

        # Validate the request payload
        is_valid, error_message = validate_rbga_request(payload)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        # Generate unique request key
        request_key = generate_request_key()

        # Create the request object matching the documentation structure
        created_request = {
            "key": request_key,
            "summary": payload["summary"],
            "pkey": payload["pkey"],
            "issuetype": payload["issuetype"],
            "applicant": payload["applicant"],
            "priority": payload["priority"],
            "sourceSystem": payload["sourceSystem"],
            "data": payload["data"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "Submitted",
            "resolution": None,
            "workflow_stage": "Initial Review",
            "approvals": []
        }

        # Handle attachments if present
        if "rbga.field.attach" in payload["data"]:
            attachments = payload["data"]["rbga.field.attach"]
            attachment_ids = []
            for i, attachment in enumerate(attachments):
                attachment_id = str(uuid.uuid4())
                attachments_db[attachment_id] = {
                    "id": attachment_id,
                    "filename": attachment.get("filename", f"attachment_{i}"),
                    "file": attachment.get("file", ""),
                    "request_key": request_key,
                    "created_at": datetime.now().isoformat()
                }
                attachment_ids.append(attachment_id)
            created_request["attachment_ids"] = attachment_ids

        # Store in mock database
        requests_db[request_key] = created_request

        # Return success response as shown in documentation
        return jsonify({"key": request_key}), 201

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/status/<request_key>', methods=['GET'])
def get_status(request_key: str):
    """Get Status API - Returns the status of a request with internationalized values"""
    try:
        if request_key not in requests_db:
            return jsonify({"error": f"Request with key {request_key} not found"}), 404

        request_data = requests_db[request_key]

        # Mock internationalized status response as shown in documentation
        status_response = {
            "status": [
                {
                    "i8nValue": "Cerrado",
                    "localeName": "es_ES"
                },
                {
                    "i8nValue": "クローズ済み",
                    "localeName": "ja_JP"
                },
                {
                    "i8nValue": "종료",
                    "localeName": "ko_KR"
                },
                {
                    "i8nValue": "Closed",
                    "localeName": "en_UK"
                },
                {
                    "i8nValue": "Abgeschlossen",
                    "localeName": "de_DE"
                }
            ],
            "requestKey": request_key,
            "resolution": "Approved"
        }

        return jsonify(status_response), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/workitemdetails/<request_key>', methods=['POST'])
def get_workitem_detail(request_key: str):
    """Get Workitem Detail API - Fetches detailed request information"""
    try:
        if request_key not in requests_db:
            return jsonify({"error": f"Request with key {request_key} not found"}), 404

        payload = request.get_json() or {}
        request_data = requests_db[request_key]

        # Base response
        response = {
            "key": request_key,
            "summary": request_data["summary"],
            "status": request_data["status"],
            "resolution": request_data["resolution"],
            "created_at": request_data["created_at"],
            "updated_at": request_data["updated_at"]
        }

        # Include approval history if requested
        if payload.get("approvalHistory") == "yes":
            response["approvalHistory"] = request_data.get("approvals", [])

        # Include custom fields if specified
        custom_fields = payload.get("customFields", [])
        if custom_fields:
            response["customFields"] = {}
            for field in custom_fields:
                if field in request_data["data"]:
                    response["customFields"][field] = request_data["data"][field]

        # If no specific fields requested, return all data
        if not custom_fields:
            response["data"] = request_data["data"]

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/workitemattachments/<request_key>', methods=['POST'])
def get_workitem_attachments(request_key: str):
    """Get Workitem Attachments API - Fetches attachment content"""
    try:
        if request_key not in requests_db:
            return jsonify({"error": f"Request with key {request_key} not found"}), 404

        payload = request.get_json() or {}
        user = payload.get("user", "")
        send_all = payload.get("sendAll", "false").lower() == "true"
        attachment_name = payload.get("attachmentName")
        attachment_id = payload.get("attachmentId")

        # Find attachments for this request
        request_attachments = []
        for att_id, attachment in attachments_db.items():
            if attachment["request_key"] == request_key:
                request_attachments.append({
                    "id": att_id,
                    "filename": attachment["filename"],
                    "file": attachment["file"],
                    "created_at": attachment["created_at"]
                })

        if send_all:
            return jsonify({
                "attachments": request_attachments,
                "count": len(request_attachments)
            }), 200

        # Find specific attachment
        target_attachment = None
        for attachment in request_attachments:
            if (attachment_name and attachment["filename"] == attachment_name) or \
               (attachment_id and attachment["id"] == attachment_id):
                target_attachment = attachment
                break

        if not target_attachment:
            return jsonify({"error": "Attachment not found"}), 404

        return jsonify({
            "attachment": target_attachment
        }), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/rbga/template', methods=['GET'])
def get_rbga_template():
    """Get RBGA template structure and field definitions"""
    try:
        template_info = {
            "template_name": "RBGA",
            "description": "Request for Budget, Governance & Approval template",
            "version": "1.0",
            "application_key": "RBGA",
            "issue_type": "rbga.issuetype.default",
            "required_fields": {
                "summary": {
                    "type": "string",
                    "description": "Summary of the Workitem"
                },
                "pkey": {
                    "type": "string",
                    "value": "RBGA",
                    "description": "Application Key"
                },
                "issuetype": {
                    "type": "string",
                    "value": "rbga.issuetype.default",
                    "description": "IssueType of Workitem"
                },
                "applicant": {
                    "type": "string",
                    "description": "NT id of the applicant who creates the request in lower case"
                },
                "priority": {
                    "type": "string",
                    "value": "default",
                    "description": "Priority of Workitem : default in workon"
                },
                "sourceSystem": {
                    "type": "string",
                    "description": "Your System Name (which calls this API)"
                }
            },
            "data_fields": RBGA_FIELDS,
            "sample_payload": {
                "summary": "Request for Substitution",
                "pkey": "RBGA",
                "issuetype": "rbga.issuetype.default",
                "applicant": "ntid",
                "priority": "default",
                "sourceSystem": "WorkON",
                "data": {
                    "common.field.employee.firstname": "firstName",
                    "common.field.employee.lastname": "lastname",
                    "common.field.employee.department": "department",
                    "common.field.employee.costcenter": "costcenter",
                    "common.field.employee.location": "location",
                    "rbga.field.termCheck": "yes",
                    "rbga.field.description": "Detailed Description for the request",
                    "rbga.field.comments": "Comments",
                    "rbga.field.workflowType": "Parallel",
                    "rbga.field.wf2": "Serial",
                    "rbga.field.wf3": "Serial",
                    "rbga.field.parallelWorkflowSel": "One approver approves the request",
                    "rbga.field.parallelWorkflowSel2": "All the Approvers has to approve",
                    "rbga.field.parallelWorkflowSel3": "All the Approvers has to approve",
                    "rbga.field.tempNew": "New Request",
                    "rbga.field.approvalstep": "One Step Approval",
                    "rbga.field.additionalFields": [
                        {
                            "fields": "fieldname",
                            "details": "value"
                        }
                    ],
                    "rbga.field.approver1": {
                        "approvers": [
                            {
                                "addAfterEnabled": True,
                                "deleteFlag": "Yes",
                                "description": "Manager",
                                "fixed": False,
                                "removable": True,
                                "userid": "ntid",
                                "ccList": "ntid"
                            }
                        ],
                        "checkDuplicate": "false",
                        "maxApprover": "20",
                        "type": "1"
                    },
                    "rbga.field.attach": [
                        {
                            "filename": "example.pdf",
                            "file": "Base64EncodedString"
                        }
                    ]
                }
            }
        }

        return jsonify(template_info), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/requests', methods=['GET'])
def list_requests():
    """List all requests with optional filtering"""
    try:
        # Get query parameters
        status_filter = request.args.get('status')
        pkey_filter = request.args.get('pkey')

        # Filter requests
        filtered_requests = []
        for req_key, req_data in requests_db.items():
            if status_filter and req_data['status'] != status_filter:
                continue
            if pkey_filter and req_data['pkey'] != pkey_filter:
                continue

            filtered_requests.append({
                "key": req_key,
                "summary": req_data['summary'],
                "status": req_data['status'],
                "applicant": req_data['applicant'],
                "created_at": req_data['created_at'],
                "workflow_stage": req_data['workflow_stage']
            })

        return jsonify({
            "requests": filtered_requests,
            "count": len(filtered_requests)
        }), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Mock WorkOn RBGA API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "rbga_operations": {
            "1": "PUT /createrequest/create - Create Request",
            "2": "PUT /createdraftrequest/draft - Create Draft Request",
            "3": "GET /status/<request_key> - Get Status",
            "4": "POST /workitemdetails/<request_key> - Get Request Details",
            "5": "POST /workitemattachments/<request_key> - Get Workitem Attachments"
        },
        "additional_endpoints": [
            "GET /rbga/template",
            "GET /requests",
            "GET /health"
        ]
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed for this endpoint"}), 405

if __name__ == '__main__':
    # Add some sample data for testing
    sample_key = "RBGA-1"
    requests_db[sample_key] = {
        "key": sample_key,
        "summary": "Sample RBGA Request for Testing",
        "pkey": "RBGA",
        "issuetype": "rbga.issuetype.default",
        "applicant": "test.user",
        "priority": "default",
        "sourceSystem": "WorkON",
        "data": {
            "common.field.employee.firstname": "John",
            "common.field.employee.lastname": "Doe",
            "common.field.employee.department": "IT",
            "common.field.employee.costcenter": "CC001",
            "common.field.employee.location": "Stuttgart",
            "rbga.field.termCheck": "yes",
            "rbga.field.description": "Sample RBGA request for testing mock server",
            "rbga.field.comments": "This is a test request",
            "rbga.field.workflowType": "Parallel",
            "rbga.field.approver1": {
                "approvers": [
                    {
                        "addAfterEnabled": True,
                        "deleteFlag": "Yes",
                        "description": "Test Manager",
                        "fixed": False,
                        "removable": True,
                        "userid": "manager.test",
                        "ccList": "cc.test"
                    }
                ],
                "checkDuplicate": "false",
                "maxApprover": "20",
                "type": "1"
            }
        },
        "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "updated_at": datetime.now().isoformat(),
        "status": "In Review",
        "resolution": None,
        "workflow_stage": "Manager Approval",
        "approvals": [
            {
                "action": "submit",
                "user": "test.user",
                "comment": "Initial submission",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
            }
        ]
    }

    print("🚀 Mock WorkOn RBGA API Server starting...")
    print(f"📋 Sample request key: {sample_key}")
    print(f"🌐 Server URL: http://localhost:5001")
    print(f"❤️  Health check: http://localhost:5001/health")
    print(f"📖 RBGA template: http://localhost:5001/rbga/template")
    print(f"📝 List requests: http://localhost:5001/requests")
    print("\n🎯 5 Core RBGA Operations:")
    print("   1. PUT /createrequest/create - Create Request")
    print("   2. PUT /createdraftrequest/draft - Create Draft Request")
    print("   3. GET /status/<key> - Get Status")
    print("   4. POST /workitemdetails/<key> - Get Request Details")
    print("   5. POST /workitemattachments/<key> - Get Workitem Attachments")

    app.run(debug=True, host='0.0.0.0', port=5001)