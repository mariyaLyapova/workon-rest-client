# WorkOn CLI - Command Line Interface for WorkOn RBGA API

A command-line interface for creating and managing WorkOn RBGA (Role-Based Global Approval) requests using the WorkOn API.

## Features

- ✅ **Create RBGA requests** from JSON input files
- ✅ **View request details** with comprehensive information display
- ✅ **Get request status** with internationalized status information
- ✅ **Configuration management** for API endpoints and credentials
- ✅ **Sample file generation** for different request types
- ✅ **Draft request support** for partial validation scenarios

## Installation

1. **Clone or navigate to the workon_cli directory**

   ```bash
   cd /path/to/workon_cli
   ```
2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### 1. Generate Sample Files

```bash
python3 workon_cli.py samples
```

This creates:

- `sample_basic_request.json` - Comprehensive example with all fields
- `sample_minimal_request.json` - Minimal required fields only

### 2. Configure API Endpoint

```bash
# For local testing (default)
python3 workon_cli.py config --set endpoint http://localhost:5001

# For production
python3 workon_cli.py config --set endpoint https://workon-api.bosch.com
python3 workon_cli.py config --set key_id your-api-key-here
```

### 3. Create a Request

```bash
# Edit the sample file with your data first
python3 workon_cli.py create --input sample_basic_request.json
```

### 4. View Request Details

```bash
python3 workon_cli.py view --request-id RBGA-12345
```

## Available Commands

### `create` - Create New WorkOn Request

```bash
python3 workon_cli.py create --input <file.json> [--draft]
```

- `--input, -i`: Path to JSON input file with request data (required)
- `--draft`: Create as draft with partial validation (optional)

**Input File Format:**

```json
{
  "summary": "Request title",
  "applicant": "user.name",
  "sourceSystem": "WorkOn CLI",
  "data": {
    "rbga.field.termCheck": "yes",
    "rbga.field.description": "Description",
    "rbga.field.workflowType": "Serial",
    "rbga.field.approver1": {
      // Approver configuration object
    }
  }
}
```

### `view` - View Request Details

```bash
python3 workon_cli.py view --request-id <RBGA-ID>
```

- `--request-id, -r`: Request ID to view (e.g., RBGA-12345)

### `status` - Get Request Status

```bash
python3 workon_cli.py status --request-id <RBGA-ID>
```

- `--request-id, -r`: Request ID to check status

### `samples` - Generate Sample Files

```bash
python3 workon_cli.py samples
```

Generates template files you can customize for your requests.

### `config` - Manage Configuration

```bash
# Show current configuration
python3 workon_cli.py config --show

# Set configuration values
python3 workon_cli.py config --set <key> <value>
```

**Configuration Keys:**

- `endpoint`: API endpoint URL
- `key_id`: API authentication key
- `timeout`: Request timeout in seconds (default: 30)
- `source_system`: Source system identifier

## Input File Structure

The CLI accepts JSON files with the following structure:

### Required Fields

- `summary`: Request title/summary
- `applicant`: NT ID (username) in lowercase
- `data`: RBGA-specific data object

### RBGA Data Fields

- `rbga.field.termCheck`: "yes" or "no"
- `rbga.field.description`: Request description
- `rbga.field.workflowType`: "Serial" or "Parallel"
- `rbga.field.approver1`: Approver configuration object

### Optional Fields

- `sourceSystem`: Override default source system
- `rbga.field.comments`: Additional comments
- `rbga.field.externalLink`: External reference link
- `rbga.field.additionalFields`: Array of additional field objects
- `rbga.field.attach`: Array of file attachments (Base64 encoded)

## Examples

### Creating a Basic Request

1. Generate sample file: `python3 workon_cli.py samples`
2. Edit `sample_basic_request.json` with your data
3. Create request: `python3 workon_cli.py create --input sample_basic_request.json`

### Creating a Draft Request

```bash
python3 workon_cli.py create --input sample_minimal_request.json --draft
```

### Checking Request Status

```bash
python3 workon_cli.py status --request-id RBGA-12345
```

### Configuring for Production Use

```bash
python3 workon_cli.py config --set endpoint https://workon-api.bosch.com
python3 workon_cli.py config --set key_id your-production-api-key
python3 workon_cli.py config --set timeout 60
```

## Output Files

The CLI automatically saves responses to timestamped files:

- Request creation: `workon_request_YYYYMMDD_HHMMSS.json`
- Request details: `workon_details_<REQUEST-ID>_YYYYMMDD_HHMMSS.json`
- Status information: `workon_status_<REQUEST-ID>_YYYYMMDD_HHMMSS.json`

## Configuration File

Configuration is stored in `~/.workon_cli_config` in INI format:

```ini
[DEFAULT]
endpoint = http://localhost:5001
key_id = your-api-key
timeout = 30
source_system = WorkOn CLI
```

## Error Handling

The CLI provides comprehensive error handling for:

- Missing or invalid input files
- Network connection issues
- API authentication errors
- Invalid request data
- Missing required fields

## Dependencies

- `requests>=2.25.0`: HTTP client for API communication
- Python 3.7+ (built-in modules: `argparse`, `json`, `configparser`, etc.)

## API Module

This CLI uses the `workon_api.py` module which provides:

- `WorkOnAPI` class for API interactions
- `create_sample_rbga_data()` function for generating sample data
- Comprehensive error handling and timeout support
- Session management for efficient HTTP connections

## Troubleshooting

### ModuleNotFoundError: No module named 'requests'

Ensure you have activated the virtual environment and installed dependencies:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Connection Errors

- For local testing: Ensure mock server is running on http://localhost:5001
- For production: Verify API endpoint and network connectivity

### Authentication Errors

- Verify your API key is correctly set: `python3 workon_cli.py config --show`
- Ensure the key has proper permissions for the WorkOn API

### Invalid JSON Errors

- Use `python3 -m json.tool input_file.json` to validate JSON syntax
- Check that all required fields are present in your input file

## Support

For issues with the CLI tool, check:

1. Input file format matches the expected structure
2. Configuration is properly set
3. Network connectivity to the API endpoint
4. API key permissions and validity
