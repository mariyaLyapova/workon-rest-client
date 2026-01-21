# WorkOn REST Client

Mock server implementation for Bosch WorkOn RBGA (Request for Budget, Governance & Approval) API.

## Features

- Mock implementation of WorkOn RBGA REST API
- Full support for RBGA template fields and validation
- 5 core API operations:
  1. Create Request
  2. Create Draft Request
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

## Requirements

- Python 3.7+
- Flask

Dependencies are automatically installed by the startup script.
