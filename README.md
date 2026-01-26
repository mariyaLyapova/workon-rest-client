# WorkOn REST Client

Complete implementation of Bosch WorkOn RBGA (Request for Budget, Governance & Approval) API with both mock server and multi-language clients.

## 🚀 Features

- **Mock Server**: Python Flask implementation of WorkOn RBGA REST API
- **Java Client**: Complete Java client library for WorkOn API
- **Python Client**: Modern Python client with type hints and clean architecture
- **Full RBGA Support**: Complete template fields and validation
- **5 Core API Operations**:
  1. Create Request (full validation)
  2. Create Draft Request (partial validation)
  3. Get Status
  4. Get Request Details
  5. Get Workitem Attachments

## 📁 Project Structure

```
workon-rest-client/
├── README.md                          # This file
├── .gitignore                         # Git exclusions
├── body_request/                      # Sample request JSON files
│   ├── create_request_body.json       # RBGA request template
│   └── get_work_item_details.json     # Detail query template
├── java_client/                      # Java implementation
│   ├── WorkOnAPI.java                 # Main Java client library
│   ├── WorkOnAPIDemo.java            # Demo/test application
│   ├── WorkOnAPI.class               # Compiled Java classes
│   ├── WorkOnAPIDemo.class           # Compiled demo class
│   └── lib/                          # Jackson JSON dependencies
├── mock-server/                      # Python Flask mock server
│   ├── mock_workon_server.py         # Complete mock implementation
│   ├── start_mock.sh                 # Server startup script
│   └── stop_mock.sh                  # Server shutdown script
└── python_client/                   # Python implementation
    ├── workon_api.py                 # Python client library with demo
    ├── tests/                        # Comprehensive test suite
    │   ├── test_workon_api.py         # Unit tests (18k+ lines)
    │   └── test_integration.py       # Integration tests (16k+ lines)
    └── venv/                         # Python virtual environment (optional)
```

## 🛠️ Prerequisites

### Java Client
- **Java 11+**
- Jackson JSON library (included in `lib/` directory)

### Python Client
- **Python 3.7+**
- `requests` library

### Mock Server
- **Python 3.7+**
- `Flask` library

## ⚡ Quick Start

### 1. Start the Mock Server

```bash
cd mock-server
./start_mock.sh
```

The server will start on `http://localhost:5001`

### 2. Run Java Client Demo

```bash
cd java_client
javac -cp ".:lib/*" *.java
java -cp ".:lib/*" WorkOnAPIDemo
```

### 3. Run Python Client Demo

```bash
cd python_client

# Install dependencies (if needed)
pip install requests

# Run demo
python3 workon_api.py
```

### 4. Stop Mock Server

```bash
cd mock-server
./stop_mock.sh
```

## 📚 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `PUT` | `/createrequest/create` | Create a new RBGA request |
| `PUT` | `/createdraftrequest/draft` | Create a draft RBGA request |
| `GET` | `/status/<request_key>` | Get request status |
| `POST` | `/workitemdetails/<request_key>` | Get request details |
| `POST` | `/workitemattachments/<request_key>` | Get attachments |

## 🔧 Client Usage Examples

### Java Client

```java
// Initialize client
WorkOnAPI apiClient = new WorkOnAPI("http://localhost:5001", "test-key-id");

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

### Python Client

```python
# Initialize client
api_client = WorkOnAPI("http://localhost:5001", "test-key-id")

# Create RBGA request
rbga_data = create_sample_rbga_data()
result = api_client.create_rbga_request(
    "Request for Software License Approval",
    "john.doe",
    rbga_data,
    "Python API Client"
)

# Get request status
request_key = result['key']
status = api_client.get_request_status(request_key)
```

### cURL Example

```bash
# Get request details
curl -X POST \
  -H "Content-Type: application/json" \
  -H "KeyId: test-key-id" \
  -d '{
    "customFields": ["rbga.field.description"],
    "systemFields": ["summary", "status"],
    "approvalHistory": "yes"
  }' \
  http://localhost:5001/workitemdetails/RBGA-1
```

## 🔐 Authentication

All API endpoints require a `KeyId` header for authentication:

```
KeyId: your-key-id-here
```

## 📝 RBGA Data Structure

The RBGA (Request for Budget, Governance & Approval) template includes:

### Common Fields
- Employee information (firstname, lastname, department, etc.)
- Company details (costcenter, location)

### RBGA-Specific Fields
- **Workflow Configuration**: Serial/Parallel approval flows
- **Approval Steps**: Multi-level approver hierarchies
- **Term Check**: Compliance validation
- **External Links**: Reference documentation
- **Attachments**: Base64 encoded file support

### Sample Structure
```json
{
  "common.field.employee.firstname": "John",
  "common.field.employee.lastname": "Doe",
  "rbga.field.termCheck": "yes",
  "rbga.field.description": "Request for new software licenses",
  "rbga.field.workflowType": "Serial",
  "rbga.field.approver1": {
    "approvers": [...],
    "type": "1"
  }
}
```

## 🌐 Production Configuration

### Java Client (Production)
```java
WorkOnAPI apiClient = new WorkOnAPI("https://workon-api.bosch.com", "your-key-id-here");
```

### Python Client (Production)
```python
# Default 30-second timeout
api_client = WorkOnAPI("https://workon-api.bosch.com", "your-key-id-here")

# Custom timeout for slow networks
api_client = WorkOnAPI("https://workon-api.bosch.com", "your-key-id-here", timeout=60)
```

## 🧪 Mock Server Features

The mock server provides:

- **Complete RBGA API simulation** with 649 lines of code
- **45+ validated RBGA fields** with specific error messages
- **Internationalized status responses** (5 languages)
- **In-memory data storage** for requests and attachments
- **KeyId header authentication** enforcement
- **Sample data pre-loaded** for immediate testing

## 🔍 Development

### Dependencies Management

**Java**: Jackson dependencies are included in `lib/` directory
- `jackson-core-2.15.2.jar`
- `jackson-databind-2.15.2.jar`
- `jackson-annotations-2.15.2.jar`

**Python**: Install via pip
```bash
pip install requests flask
```

### Virtual Environment (Recommended for Python)

```bash
# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install requests

# Deactivate when done
deactivate
```

## 🐛 Troubleshooting

### Common Issues

**1. Python ImportError: No module named 'requests'**
```bash
pip install requests
# or on macOS: pip3 install requests
```

**2. Java ClassNotFoundException**
```bash
# Ensure you're compiling and running with classpath
javac -cp ".:lib/*" *.java
java -cp ".:lib/*" WorkOnAPIDemo
```

**3. Connection Refused**
```bash
# Make sure mock server is running
cd mock-server && ./start_mock.sh
```

**4. Mock Server Permission Denied**
```bash
# Make scripts executable
chmod +x start_mock.sh stop_mock.sh
```

## 📊 Code Quality

### Python Features
- **Type hints** for better code documentation
- **Configurable timeouts** for production reliability (default: 30s)
- **Clean error handling** with proper exception propagation
- **Constants** for maintainable configuration
- **Comprehensive docstrings** with examples
- **Modern f-string** formatting
- **Extensive test suite** with 34k+ lines of unit and integration tests

### Java Features
- **Modern HTTP Client** (java.net.http)
- **Jackson integration** for seamless JSON handling
- **Method overloading** for flexible usage
- **Comprehensive JavaDoc** documentation
- **Timeout configuration** for production reliability

## 🤝 Contributing

This is a professional WorkOn API client implementation demonstrating:
- Enterprise-level API integration patterns
- Multi-language client development
- Comprehensive testing with mock servers
- Production-ready error handling
- Clean architecture and documentation

## 📄 License

This project demonstrates professional API client implementation for the Bosch WorkOn RBGA system.

---

**Developed with ❤️ for enterprise API integration**