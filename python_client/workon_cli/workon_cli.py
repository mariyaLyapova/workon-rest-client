#!/usr/bin/env python3
"""
WorkOn CLI - Command Line Interface for WorkOn RBGA API

This script provides a command-line interface for:
1. Creating RBGA work requests from input files
2. Viewing request details
3. Managing configurations

Usage:
    python workon_cli.py create --input request.json
    python workon_cli.py view --request-id RBGA-12345
    python workon_cli.py config --set-endpoint https://workon-api.bosch.com
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import configparser
from datetime import datetime

# Import the WorkOn API client from parent directory
# Add the parent directory (python_client) to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from workon_api import WorkOnAPI, create_sample_rbga_data

class WorkOnCLI:
    """Command-line interface for WorkOn API operations."""

    def __init__(self):
        self.config_file = Path.home() / '.workon_cli_config'
        self.config = self.load_config()

    def load_config(self) -> configparser.ConfigParser:
        """Load configuration from config file."""
        config = configparser.ConfigParser()

        # Set defaults
        config['DEFAULT'] = {
            'endpoint': 'http://localhost:5001',
            'key_id': 'test-key-id',
            'timeout': '30',
            'source_system': 'WorkOn CLI'
        }

        # Load from file if exists
        if self.config_file.exists():
            config.read(self.config_file)

        return config

    def save_config(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
        print(f"Configuration saved to {self.config_file}")

    def get_api_client(self) -> WorkOnAPI:
        """Create and return configured API client."""
        endpoint = self.config['DEFAULT']['endpoint']
        key_id = self.config['DEFAULT']['key_id']
        timeout = int(self.config['DEFAULT']['timeout'])

        return WorkOnAPI(endpoint, key_id, timeout)

    def create_request_from_file(self, input_file: str, draft: bool = False) -> None:
        """Create a WorkOn request from input file."""
        try:
            # Read and parse input file
            with open(input_file, 'r', encoding='utf-8') as f:
                if input_file.endswith('.json'):
                    request_data = json.load(f)
                else:
                    print(f"Error: Unsupported file format. Only JSON files are supported.")
                    sys.exit(1)

            print(f"📄 Reading request data from: {input_file}")

            # Validate required fields
            required_fields = ['summary', 'applicant', 'data']
            missing_fields = [field for field in required_fields if field not in request_data]
            if missing_fields:
                print(f"Error: Missing required fields in input file: {', '.join(missing_fields)}")
                sys.exit(1)

            # Extract data
            summary = request_data['summary']
            applicant = request_data['applicant']
            data = request_data['data']
            source_system = request_data.get('sourceSystem', self.config['DEFAULT']['source_system'])

            print(f"📝 Summary: {summary}")
            print(f"👤 Applicant: {applicant}")
            print(f"🔧 Source System: {source_system}")

            # Create API client and make request
            api_client = self.get_api_client()

            if draft:
                print("📋 Creating draft request...")
                result = api_client.create_draft_rbga_request(summary, applicant, data, source_system)
            else:
                print("📋 Creating request...")
                result = api_client.create_rbga_request(summary, applicant, data, source_system)

            # Display results
            if result:
                print("✅ Request created successfully!")
                print(f"🆔 Request ID: {result.get('key', 'N/A')}")
                print(f"🔗 Self Link: {result.get('self', 'N/A')}")

                # Save result to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"workon_request_{timestamp}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"💾 Full response saved to: {output_file}")
            else:
                print("❌ Failed to create request")
                sys.exit(1)

        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in input file: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def view_request_details(self, request_id: str) -> None:
        """View details of a WorkOn request."""
        try:
            print(f"🔍 Fetching details for request: {request_id}")

            api_client = self.get_api_client()
            details = api_client.get_workitem_detail(request_id)

            if details:
                print("✅ Request details retrieved successfully!")
                print("=" * 60)

                # Display basic information
                print(f"🆔 Request ID: {details.get('key', 'N/A')}")
                print(f"📝 Summary: {details.get('summary', 'N/A')}")
                print(f"📊 Status: {details.get('status', 'N/A')}")
                print(f"🔗 Resolution: {details.get('resolution', 'N/A')}")
                print(f"📅 Created: {details.get('created_at', 'N/A')}")
                print(f"📅 Updated: {details.get('updated_at', 'N/A')}")

                # Display description from data if available
                data = details.get('data', {})
                description = data.get('rbga.field.description')
                if description:
                    print(f"📄 Description: {description}")

                # Display comments if available
                comments = data.get('rbga.field.comments')
                if comments:
                    print(f"💬 Comments: {comments}")

                # Display key RBGA fields
                if data:
                    print("\n🔧 RBGA Fields:")

                    # Show workflow type
                    workflow_type = data.get('rbga.field.workflowType')
                    if workflow_type:
                        print(f"  Workflow Type: {workflow_type}")

                    # Show source system
                    source_system = data.get('rbga.field.sourceSystem')
                    if source_system:
                        print(f"  Source System: {source_system}")

                    # Show external link
                    external_link = data.get('rbga.field.externalLink')
                    if external_link:
                        print(f"  External Link: {external_link}")

                    # Show additional fields
                    additional_fields = data.get('rbga.field.additionalFields', [])
                    if additional_fields:
                        print("  Additional Fields:")
                        for field in additional_fields:
                            print(f"    - {field.get('fields')}: {field.get('details')}")

                    # Show approvers
                    approver1 = data.get('rbga.field.approver1')
                    if approver1 and approver1.get('approvers'):
                        print(f"  Approvers (Level 1): {len(approver1['approvers'])} approver(s)")
                        for idx, approver in enumerate(approver1['approvers'], 1):
                            print(f"    {idx}. {approver.get('userid')}")

                # Save detailed result to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"workon_details_{request_id}_{timestamp}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(details, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Full details saved to: {output_file}")

            else:
                print("❌ Failed to retrieve request details")
                sys.exit(1)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def get_request_status(self, request_id: str) -> None:
        """Get internationalized status information for a request."""
        try:
            print(f"📊 Fetching status for request: {request_id}")

            api_client = self.get_api_client()
            status_info = api_client.get_request_status(request_id)

            if status_info:
                print("✅ Status information retrieved successfully!")
                print("=" * 60)

                for key, value in status_info.items():
                    print(f"{key}: {value}")

                # Save status result to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"workon_status_{request_id}_{timestamp}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(status_info, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Status information saved to: {output_file}")

            else:
                print("❌ Failed to retrieve status information")
                sys.exit(1)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def generate_sample_files(self) -> None:
        """Generate sample input files for different scenarios."""
        print("📝 Generating sample input files...")

        # Generate basic request template
        basic_template = {
            "summary": "Request for Software License Approval",
            "applicant": "john.doe",
            "sourceSystem": "WorkOn CLI",
            "data": create_sample_rbga_data()
        }

        with open('sample_basic_request.json', 'w', encoding='utf-8') as f:
            json.dump(basic_template, f, indent=2, ensure_ascii=False)
        print("✅ Created: sample_basic_request.json")

        # Generate minimal template
        minimal_template = {
            "summary": "Minimal Request Template",
            "applicant": "user.name",
            "data": {
                "rbga.field.termCheck": "yes",
                "rbga.field.description": "Brief description of the request",
                "rbga.field.workflowType": "Serial",
                "rbga.field.approver1": {
                    "approvers": [
                        {
                            "addAfterEnabled": True,
                            "deleteFlag": "Yes",
                            "description": "",
                            "fixed": False,
                            "removable": True,
                            "userid": "approver.userid",
                            "ccList": ""
                        }
                    ],
                    "checkDuplicate": "false",
                    "maxApprover": "20",
                    "type": "1"
                }
            }
        }

        with open('sample_minimal_request.json', 'w', encoding='utf-8') as f:
            json.dump(minimal_template, f, indent=2, ensure_ascii=False)
        print("✅ Created: sample_minimal_request.json")

        print("\n📚 Sample files created successfully!")
        print("Edit these files with your actual data before using them with the CLI.")

    def show_config(self) -> None:
        """Display current configuration."""
        print("⚙️  Current Configuration:")
        print("=" * 40)
        for section_name in self.config.sections() or ['DEFAULT']:
            section = self.config[section_name]
            print(f"[{section_name}]")
            for key, value in section.items():
                # Mask sensitive information
                if 'key' in key.lower() or 'password' in key.lower():
                    masked_value = '*' * len(value) if value else value
                    print(f"  {key} = {masked_value}")
                else:
                    print(f"  {key} = {value}")
            print()

    def set_config(self, key: str, value: str) -> None:
        """Set configuration value."""
        self.config['DEFAULT'][key] = value
        self.save_config()
        print(f"✅ Configuration updated: {key} = {value}")

    def setup_config(self, endpoint: str, key_id: str) -> None:
        """Set both endpoint and key_id configuration in one command."""
        print("⚙️  Setting up WorkOn CLI configuration...")

        # Update both values
        self.config['DEFAULT']['endpoint'] = endpoint
        self.config['DEFAULT']['key_id'] = key_id
        self.save_config()

        print("✅ Configuration setup completed!")
        print(f"📡 Endpoint: {endpoint}")
        print(f"🔑 Key ID: {'*' * len(key_id) if key_id else '(not set)'}")
        print("\n🚀 You can now create WorkOn requests using the CLI.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='WorkOn CLI - Command Line Interface for WorkOn RBGA API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a request from input file
  python workon_cli.py create --input sample_basic_request.json

  # Create a draft request
  python workon_cli.py create --input sample_minimal_request.json --draft

  # View request details
  python workon_cli.py view --request-id RBGA-12345

  # Get request status
  python workon_cli.py status --request-id RBGA-12345

  # Generate sample input files
  python workon_cli.py samples

  # Show current configuration
  python workon_cli.py config --show

  # Set up both endpoint and key_id in one command
  python workon_cli.py config --setup https://workon-api.bosch.com your-api-key-here

  # Set individual configuration values
  python workon_cli.py config --set endpoint https://workon-api.bosch.com
  python workon_cli.py config --set key_id your-api-key-here
        """)

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new WorkOn request')
    create_parser.add_argument('--input', '-i', required=True,
                              help='Path to JSON input file with request data')
    create_parser.add_argument('--draft', action='store_true',
                              help='Create as draft (with partial validation)')

    # View command
    view_parser = subparsers.add_parser('view', help='View request details')
    view_parser.add_argument('--request-id', '-r', required=True,
                            help='Request ID to view (e.g., RBGA-12345)')

    # Status command
    status_parser = subparsers.add_parser('status', help='Get request status')
    status_parser.add_argument('--request-id', '-r', required=True,
                              help='Request ID to check status (e.g., RBGA-12345)')

    # Samples command
    subparsers.add_parser('samples', help='Generate sample input files')

    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_group = config_parser.add_mutually_exclusive_group(required=True)
    config_group.add_argument('--show', action='store_true', help='Show current configuration')
    config_group.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'),
                             help='Set configuration value (e.g., endpoint https://api.example.com)')
    config_group.add_argument('--setup', nargs=2, metavar=('ENDPOINT', 'KEY_ID'),
                             help='Set both endpoint and key_id in one command (e.g., https://workon-api.bosch.com your-key-id)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cli = WorkOnCLI()

    try:
        if args.command == 'create':
            cli.create_request_from_file(args.input, args.draft)
        elif args.command == 'view':
            cli.view_request_details(args.request_id)
        elif args.command == 'status':
            cli.get_request_status(args.request_id)
        elif args.command == 'samples':
            cli.generate_sample_files()
        elif args.command == 'config':
            if args.show:
                cli.show_config()
            elif args.set:
                key, value = args.set
                cli.set_config(key, value)
            elif args.setup:
                endpoint, key_id = args.setup
                cli.setup_config(endpoint, key_id)

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()