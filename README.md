# WorkOn REST Client

Complete implementation of Bosch WorkOn RBGA (Request for Budget, Governance & Approval) API with both mock server and Java client.

## Features

- **Mock Server**: Python Flask implementation of WorkOn RBGA REST API
- **Java Client**: Complete Java client library for WorkOn API
- **Full RBGA Support**: Complete template fields and validation
- **5 Core API Operations**:
  1. Create Request (full validation)
  2. Create Draft Request (partial validation)
  3. Get Status
  4. Get Request Details
  5. Get Workitem Attachments

## Mock Server

The mock server is located in the `mock-server/` directory.

### Starting the Server

```bash
cd mock-server
./start_mock.sh
```

The server will start on `http://localhost:5001`

### Stopping the Server

```bash
cd mock-server
./stop_mock.sh
```

## API Endpoints

- `PUT /createrequest/create` - Create a new RBGA request
- `PUT /createdraftrequest/draft` - Create a draft RBGA request
- `GET /status/<request_key>` - Get request status
- `POST /workitemdetails/<request_key>` - Get request details
- `POST /workitemattachments/<request_key>` - Get attachments
- `GET /rbga/template` - Get RBGA template information
- `GET /requests` - List all requests
- `GET /health` - Health check

## Java Client

The Java client is located in the `java_client/` directory and provides a complete API wrapper for WorkOn RBGA operations.

### Prerequisites

- Java 11+
- Jackson JSON library (included in `lib/` directory)

### Quick Start

1. **Start the mock server:**
   ```bash
   cd mock-server
   ./start_mock.sh
   ```

2. **Compile and run the Java client:**
   ```bash
   cd java_client
   javac -cp ".:lib/*" *.java
   java -cp ".:lib/*" WorkOnAPIDemo
   ```

3. **Stop the mock server:**
   ```bash
   cd mock-server
   ./stop_mock.sh
   ```

### Java Client Usage

```java
// Initialize client (for mock server)
WorkOnAPI apiClient = new WorkOnAPI("http://localhost:5001", null);

// Create RBGA request
Map<String, Object> rbgaData = createSampleRbgaData();
Map<String, Object> result = apiClient.createRbgaRequest(
    "Request for Software License Approval",
    "john.doe",
    rbgaData,
    "Java API Client"
);

// Get request status
String requestKey = (String) result.get("key");
Map<String, Object> status = apiClient.getRequestStatus(requestKey);
```

## Project Structure

```
├── java_client/
│   ├── WorkOnAPI.java          # Main API client class
│   ├── WorkOnAPIDemo.java      # Demo/test application
│   └── lib/                    # Jackson JSON dependencies
└── mock-server/
    ├── mock_workon_server.py   # Flask mock server
    ├── start_mock.sh           # Server startup script
    └── stop_mock.sh            # Server shutdown script
```

## Requirements

### Mock Server
- Python 3.7+
- Flask (automatically installed by startup script)

### Java Client
- Java 11+
- Jackson JSON library (included)
