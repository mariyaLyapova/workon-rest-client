/**
 * Demo application for the WorkOn API Java client
 * Demonstrates all 5 core RBGA operations
 */

import java.util.*;

public class WorkOnAPIDemo {

    public static void main(String[] args) {
        try {
            System.out.println("=== RBGA API Demo: 5 Core Operations (Java) ===\n");

            // Initialize API client - pointing to mock server
            WorkOnAPI apiClient = new WorkOnAPI("http://localhost:5001", null);
            // For production: WorkOnAPI apiClient = new WorkOnAPI("https://workon-api.bosch.com", "your-api-key-here");

            // Example RBGA data structure according to documentation
            Map<String, Object> rbgaData = createSampleRbgaData();

            // 1. Create Full Request (complete data with validation)
            System.out.println("1. Creating full RBGA request...");
            Map<String, Object> result = apiClient.createRbgaRequest(
                "Request for Software License Approval",
                "john.doe",
                rbgaData,
                "Java API Client"
            );
            System.out.println("Full request created successfully: " + result + "\n");

            // 2. Create Draft Request (partial data allowed)
            System.out.println("2. Creating RBGA draft request...");
            Map<String, Object> draftData = new HashMap<>();
            draftData.put("rbga.field.termCheck", "yes");
            draftData.put("rbga.field.description", "Draft request for software licenses");
            draftData.put("rbga.field.workflowType", "Parallel");

            Map<String, Object> draftResult = apiClient.createDraftRbgaRequest(
                "Draft: Software License Request",
                "john.doe",
                draftData,
                "Java API Client"
            );
            System.out.println("Draft created: " + draftResult + "\n");

            // If creation was successful, demonstrate the other 3 operations
            if (result.containsKey("key")) {
                String requestKey = (String) result.get("key");

                // 3. Get Status
                System.out.println("3. Getting status for request: " + requestKey);
                Map<String, Object> status = apiClient.getRequestStatus(requestKey);
                System.out.println("Request status: " + status + "\n");

                // 4. Get Request Details
                System.out.println("4. Getting detailed information for request: " + requestKey);
                List<String> customFields = Arrays.asList(
                    "rbga.field.description",
                    "rbga.field.comments",
                    "rbga.field.workflowType"
                );
                Map<String, Object> details = apiClient.getWorkitemDetail(requestKey, customFields, true);
                System.out.println("Request details: " + details + "\n");

                // 5. Get Workitem Attachments
                System.out.println("5. Getting attachments for request: " + requestKey);
                Map<String, Object> attachments = apiClient.getAttachments(requestKey, "john.doe", null, true);
                System.out.println("Attachments: " + attachments);
            }

            System.out.println("\n=== All 5 RBGA operations completed successfully! ===");

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Create sample RBGA data structure according to documentation
     */
    private static Map<String, Object> createSampleRbgaData() {
        Map<String, Object> rbgaData = new HashMap<>();

        // Common employee fields
        rbgaData.put("common.field.employee.firstname", "John");
        rbgaData.put("common.field.employee.lastname", "Doe");
        rbgaData.put("common.field.employee.department", "IT");
        rbgaData.put("common.field.employee.costcenter", "CC001");
        rbgaData.put("common.field.employee.location", "Stuttgart");

        // RBGA-specific fields
        rbgaData.put("rbga.field.termCheck", "yes");
        rbgaData.put("rbga.field.description", "Request for new software licenses");
        rbgaData.put("rbga.field.comments", "Urgent approval needed for project");
        rbgaData.put("rbga.field.workflowType", "Parallel");
        rbgaData.put("rbga.field.wf2", "Serial");
        rbgaData.put("rbga.field.wf3", "Serial");
        rbgaData.put("rbga.field.parallelWorkflowSel", "One approver approves the request");
        rbgaData.put("rbga.field.parallelWorkflowSel2", "All the Approvers has to approve");
        rbgaData.put("rbga.field.parallelWorkflowSel3", "All the Approvers has to approve");
        rbgaData.put("rbga.field.tempNew", "New Request");
        rbgaData.put("rbga.field.approvalstep", "One Step Approval");

        // Additional fields
        List<Map<String, String>> additionalFields = new ArrayList<>();
        Map<String, String> budgetField = new HashMap<>();
        budgetField.put("fields", "Budget");
        budgetField.put("details", "5000 EUR");
        additionalFields.add(budgetField);
        rbgaData.put("rbga.field.additionalFields", additionalFields);

        // Approver information
        Map<String, Object> approver1 = new HashMap<>();
        List<Map<String, Object>> approvers = new ArrayList<>();

        Map<String, Object> approver = new HashMap<>();
        approver.put("addAfterEnabled", true);
        approver.put("deleteFlag", "Yes");
        approver.put("description", "Manager");
        approver.put("fixed", false);
        approver.put("removable", true);
        approver.put("userid", "manager.ntid");
        approver.put("ccList", "backup.manager");
        approvers.add(approver);

        approver1.put("approvers", approvers);
        approver1.put("checkDuplicate", "false");
        approver1.put("maxApprover", "20");
        approver1.put("type", "1");
        rbgaData.put("rbga.field.approver1", approver1);

        // Attachments
        List<Map<String, String>> attachments = new ArrayList<>();
        Map<String, String> attachment = new HashMap<>();
        attachment.put("filename", "requirements.pdf");
        attachment.put("file", "Base64EncodedString"); // Base64 encoded file content
        attachments.add(attachment);
        rbgaData.put("rbga.field.attach", attachments);

        return rbgaData;
    }
}