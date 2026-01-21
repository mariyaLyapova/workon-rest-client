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
            WorkOnAPI apiClient = new WorkOnAPI("http://localhost:5001", null, "test-key-id");
            // For production: WorkOnAPI apiClient = new WorkOnAPI("https://workon-api.bosch.com", null, "your-key-id-here");

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
                    "common.field.employee.companycode"
                );
                List<String> systemFields = Arrays.asList(
                    "summary",
                    "reporter",
                    "created",
                    "updated",
                    "assignee",
                    "status",
                    "priority"
                );
                Map<String, Object> details = apiClient.getWorkitemDetail(requestKey, customFields, systemFields, true);
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
        rbgaData.put("rbga.field.workflowType", "Serial");
        rbgaData.put("rbga.field.wf2", "Serial");
        rbgaData.put("rbga.field.wf3", "Serial");
        rbgaData.put("rbga.field.parallelWorkflowSel", "Only one Approver has to approve");
        rbgaData.put("rbga.field.parallelWorkflowSel2", "Only one Approver has to approve");
        rbgaData.put("rbga.field.parallelWorkflowSel3", "Only one Approver has to approve");
        rbgaData.put("rbga.field.tempNew", "New Request");
        rbgaData.put("rbga.field.approvalstep", "One Step Approval");

        // External link
        rbgaData.put("rbga.field.externalLink", "https://www.bosch.com");

        // Additional fields
        List<Map<String, String>> additionalFields = new ArrayList<>();
        Map<String, String> targetRevision = new HashMap<>();
        targetRevision.put("fields", "Target revision");
        targetRevision.put("details", "Value1");
        additionalFields.add(targetRevision);

        Map<String, String> previewLink = new HashMap<>();
        previewLink.put("fields", "Preview link");
        previewLink.put("details", "https://www.bosch.com");
        additionalFields.add(previewLink);

        rbgaData.put("rbga.field.additionalFields", additionalFields);

        // Attachments (like in your JSON)
        List<Map<String, String>> attachments = new ArrayList<>();
        Map<String, String> attachment = new HashMap<>();
        attachment.put("filename", "filename.ext");
        attachment.put("file", "Base64EncodedString");
        attachments.add(attachment);
        rbgaData.put("rbga.field.attach", attachments);

        // Primary approver (rbga.field.approver1)
        Map<String, Object> approver1 = new HashMap<>();
        List<Map<String, Object>> approvers1 = new ArrayList<>();

        // First approver
        Map<String, Object> approver1a = new HashMap<>();
        approver1a.put("addAfterEnabled", true);
        approver1a.put("deleteFlag", "Yes");
        approver1a.put("description", "");
        approver1a.put("fixed", false);
        approver1a.put("removable", true);
        approver1a.put("userid", "mrj6cob");
        approver1a.put("ccList", "");
        approvers1.add(approver1a);

        // Second approver
        Map<String, Object> approver1b = new HashMap<>();
        approver1b.put("addAfterEnabled", true);
        approver1b.put("deleteFlag", "Yes");
        approver1b.put("description", "");
        approver1b.put("fixed", false);
        approver1b.put("removable", true);
        approver1b.put("userid", "mrj6cob");
        approver1b.put("ccList", "");
        approvers1.add(approver1b);

        approver1.put("approvers", approvers1);
        approver1.put("checkDuplicate", "false");
        approver1.put("maxApprover", "20");
        approver1.put("type", "1");
        rbgaData.put("rbga.field.approver1", approver1);

        // When approved workflow
        Map<String, Object> whenApproved = new HashMap<>();
        List<Map<String, Object>> approversApproved = new ArrayList<>();
        Map<String, Object> approverApproved = new HashMap<>();
        approverApproved.put("addAfterEnabled", true);
        approverApproved.put("deleteFlag", "Yes");
        approverApproved.put("description", "");
        approverApproved.put("fixed", false);
        approverApproved.put("removable", true);
        approverApproved.put("userid", "mrj6cob");
        approverApproved.put("ccList", "");
        approversApproved.add(approverApproved);

        whenApproved.put("approvers", approversApproved);
        whenApproved.put("checkDuplicate", "false");
        whenApproved.put("maxApprover", "20");
        whenApproved.put("type", "1");
        rbgaData.put("rbga.field.whenApproved", whenApproved);

        // When declined workflow
        Map<String, Object> whenDeclined = new HashMap<>();
        List<Map<String, Object>> approversDeclined = new ArrayList<>();
        Map<String, Object> approverDeclined = new HashMap<>();
        approverDeclined.put("addAfterEnabled", true);
        approverDeclined.put("deleteFlag", "Yes");
        approverDeclined.put("description", "");
        approverDeclined.put("fixed", false);
        approverDeclined.put("removable", true);
        approverDeclined.put("userid", "mrj6cob");
        approverDeclined.put("ccList", "");
        approversDeclined.add(approverDeclined);

        whenDeclined.put("approvers", approversDeclined);
        whenDeclined.put("checkDuplicate", "false");
        whenDeclined.put("maxApprover", "20");
        whenDeclined.put("type", "1");
        rbgaData.put("rbga.field.whenDeclined", whenDeclined);

        return rbgaData;
    }
}