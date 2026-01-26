/**
 * Bosch WorkOn API Client - Java Implementation
 * Simple Java client to interact with Bosch WorkOn REST API using RBGA template
 *
 * This Java client provides the same 5 core RBGA operations as the Python version:
 * 1. Create Request
 * 2. Create Draft Request
 * 3. Get Status
 * 4. Get Request Details
 * 5. Get Workitem Attachments
 */

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;

/**
 * Simple client for Bosch WorkOn REST API with RBGA template support
 */
public class WorkOnAPI {

    private final String baseUrl;
    private final String keyId;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;

    /**
     * Initialize the WorkOn API client
     *
     * @param baseUrl The base URL for the WorkOn API
     * @param keyId Key ID for WorkOn API authentication (can be null for testing)
     */
    public WorkOnAPI(String baseUrl, String keyId) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.keyId = keyId;
        this.httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();
        this.objectMapper = new ObjectMapper();
    }

    /**
     * Add common headers to HTTP request builder
     */
    private void addCommonHeaders(HttpRequest.Builder requestBuilder) {
        requestBuilder.header("Content-Type", "application/json");

        if (keyId != null && !keyId.isEmpty()) {
            requestBuilder.header("KeyId", keyId);
        }
    }

    /**
     * Initialize the WorkOn API client without authentication
     *
     * @param baseUrl The base URL for the WorkOn API
     */
    public WorkOnAPI(String baseUrl) {
        this(baseUrl, null);
    }

    /**
     * Create a new WorkOn request using RBGA template (based on official API documentation)
     *
     * @param summary Summary of the Workitem
     * @param applicant NT id of the applicant who creates the request (lowercase)
     * @param data Map containing RBGA-specific data fields
     * @param sourceSystem Your System Name (which calls this API)
     * @return Map with the created request key
     * @throws IOException If the API request fails
     * @throws InterruptedException If the request is interrupted
     */
    public Map<String, Object> createRbgaRequest(String summary, String applicant, Map<String, Object> data, String sourceSystem)
            throws IOException, InterruptedException {

        String url = baseUrl + "/createrequest/create";

        // Prepare the request payload according to RBGA documentation
        Map<String, Object> payload = new HashMap<>();
        payload.put("summary", summary);
        payload.put("pkey", "RBGA");
        payload.put("issuetype", "rbga.issuetype.default");
        payload.put("applicant", applicant.toLowerCase());
        payload.put("priority", "default");

        // Add sourceSystem to data object, not top level
        Map<String, Object> dataWithSource = new HashMap<>(data);
        dataWithSource.put("rbga.field.sourceSystem", sourceSystem);
        payload.put("data", dataWithSource);

        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .PUT(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(payload)));

        // Add common headers (Content-Type, Authorization, KeyId)
        addCommonHeaders(requestBuilder);

        HttpRequest request = requestBuilder.build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() >= 200 && response.statusCode() < 300) {
            return objectMapper.readValue(response.body(), Map.class);
        } else {
            throw new IOException("Error creating WorkOn request: HTTP " + response.statusCode() + " - " + response.body());
        }
    }

    /**
     * Create a draft WorkOn request using RBGA template (can be saved without full validation)
     *
     * @param summary Summary of the Workitem
     * @param applicant NT id of the applicant who creates the request (lowercase)
     * @param data Map containing RBGA-specific data fields (partial data allowed)
     * @param sourceSystem Your System Name (which calls this API)
     * @return Map with the created draft request key
     * @throws IOException If the API request fails
     * @throws InterruptedException If the request is interrupted
     */
    public Map<String, Object> createDraftRbgaRequest(String summary, String applicant, Map<String, Object> data, String sourceSystem)
            throws IOException, InterruptedException {

        String url = baseUrl + "/createdraftrequest/draft";

        // Prepare the draft payload - similar structure but with less validation
        Map<String, Object> payload = new HashMap<>();
        payload.put("summary", summary);
        payload.put("pkey", "RBGA");
        payload.put("issuetype", "rbga.issuetype.default");
        payload.put("applicant", applicant.toLowerCase());
        payload.put("priority", "default");

        // Add sourceSystem to data object, not top level
        Map<String, Object> dataWithSource = new HashMap<>(data);
        dataWithSource.put("rbga.field.sourceSystem", sourceSystem);
        payload.put("data", dataWithSource);
        payload.put("draft", true); // Indicate this is a draft request

        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .PUT(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(payload)));

        // Add common headers (Content-Type, Authorization, KeyId)
        addCommonHeaders(requestBuilder);

        HttpRequest request = requestBuilder.build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() >= 200 && response.statusCode() < 300) {
            return objectMapper.readValue(response.body(), Map.class);
        } else {
            throw new IOException("Error creating WorkOn draft request: HTTP " + response.statusCode() + " - " + response.body());
        }
    }

    /**
     * Get the status of an existing WorkOn request
     *
     * @param requestKey The key of the request (e.g., "RBGA-123")
     * @return Map with internationalized status information
     * @throws IOException If the API request fails
     * @throws InterruptedException If the request is interrupted
     */
    public Map<String, Object> getRequestStatus(String requestKey) throws IOException, InterruptedException {
        String url = baseUrl + "/status/" + requestKey;

        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .GET();

        // Add common headers (Content-Type, Authorization, KeyId)
        addCommonHeaders(requestBuilder);

        HttpRequest request = requestBuilder.build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() >= 200 && response.statusCode() < 300) {
            return objectMapper.readValue(response.body(), Map.class);
        } else {
            throw new IOException("Error fetching request status: HTTP " + response.statusCode() + " - " + response.body());
        }
    }

    /**
     * Get detailed information about a WorkOn request
     *
     * @param requestKey The key of the request (e.g., "RBGA-123")
     * @param customFields List of specific custom fields to retrieve (e.g., ["rbga.field.description"])
     * @param systemFields List of specific system fields to retrieve (e.g., ["summary", "status"])
     * @param includeApprovalHistory Whether to include approval history
     * @return Map with detailed request information
     * @throws IOException If the API request fails
     * @throws InterruptedException If the request is interrupted
     */
    public Map<String, Object> getWorkitemDetail(String requestKey, List<String> customFields, List<String> systemFields, boolean includeApprovalHistory)
            throws IOException, InterruptedException {

        String url = baseUrl + "/workitemdetails/" + requestKey;

        Map<String, Object> payload = new HashMap<>();
        if (includeApprovalHistory) {
            payload.put("approvalHistory", "yes");
        }
        if (customFields != null && !customFields.isEmpty()) {
            payload.put("customFields", customFields);
        }
        if (systemFields != null && !systemFields.isEmpty()) {
            payload.put("systemFields", systemFields);
        }

        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .POST(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(payload)));

        // Add common headers (Content-Type, Authorization, KeyId)
        addCommonHeaders(requestBuilder);

        HttpRequest request = requestBuilder.build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() >= 200 && response.statusCode() < 300) {
            return objectMapper.readValue(response.body(), Map.class);
        } else {
            throw new IOException("Error fetching workitem details: HTTP " + response.statusCode() + " - " + response.body());
        }
    }

    /**
     * Get attachments for a WorkOn request
     *
     * @param requestKey The key of the request (e.g., "RBGA-123")
     * @param user NT ID of the user requesting attachments
     * @param attachmentName Name of specific attachment to retrieve (optional)
     * @param sendAll Whether to retrieve all attachments
     * @return Map with attachment content (Base64 encoded)
     * @throws IOException If the API request fails
     * @throws InterruptedException If the request is interrupted
     */
    public Map<String, Object> getAttachments(String requestKey, String user, String attachmentName, boolean sendAll)
            throws IOException, InterruptedException {

        String url = baseUrl + "/workitemattachments/" + requestKey;

        Map<String, Object> payload = new HashMap<>();
        payload.put("user", user);
        payload.put("sendAll", String.valueOf(sendAll).toLowerCase());

        if (!sendAll && attachmentName != null && !attachmentName.isEmpty()) {
            payload.put("attachmentName", attachmentName);
        }

        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .POST(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(payload)));

        // Add common headers (Content-Type, Authorization, KeyId)
        addCommonHeaders(requestBuilder);

        HttpRequest request = requestBuilder.build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() >= 200 && response.statusCode() < 300) {
            return objectMapper.readValue(response.body(), Map.class);
        } else {
            throw new IOException("Error fetching attachments: HTTP " + response.statusCode() + " - " + response.body());
        }
    }

    // Convenience method overloads
    public Map<String, Object> createRbgaRequest(String summary, String applicant, Map<String, Object> data)
            throws IOException, InterruptedException {
        return createRbgaRequest(summary, applicant, data, "WorkON");
    }

    public Map<String, Object> createDraftRbgaRequest(String summary, String applicant, Map<String, Object> data)
            throws IOException, InterruptedException {
        return createDraftRbgaRequest(summary, applicant, data, "WorkON");
    }

    public Map<String, Object> getWorkitemDetail(String requestKey) throws IOException, InterruptedException {
        return getWorkitemDetail(requestKey, null, null, false);
    }

    public Map<String, Object> getWorkitemDetail(String requestKey, List<String> customFields, boolean includeApprovalHistory) throws IOException, InterruptedException {
        return getWorkitemDetail(requestKey, customFields, null, includeApprovalHistory);
    }

    public Map<String, Object> getAttachments(String requestKey, String user) throws IOException, InterruptedException {
        return getAttachments(requestKey, user, null, true);
    }
}