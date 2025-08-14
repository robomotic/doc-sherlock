# n8n Workflow for Doc-Sherlock API

This directory contains an n8n workflow that demonstrates how to submit PDF files to the doc-sherlock API for analysis.

## Files

- `doc-sherlock-workflow.json` - The n8n workflow definition
- `workflow-config.json` - Workflow configuration metadata
- `runme.sh` - Docker command to start n8n
- `setup.sh` - Complete setup script
- `README.md` - This documentation

## Prerequisites

1. **Docker** - Required to run n8n in a container
2. **Doc-Sherlock API** - Must be running on the host machine

## Setup Instructions

### 1. Start Doc-Sherlock API

First, ensure the doc-sherlock REST API is running on your host machine:

```bash
# From the project root directory
doc-sherlock rest-service --host 0.0.0.0 --port 8000
```

### 2. Start n8n

Run the n8n container:

```bash
cd workflows/n8n
./runme.sh
```

This will start n8n on `http://localhost:5678`

### 3. Import the Workflow

1. Open n8n in your browser: `http://localhost:5678`
2. Click "Add workflow" or the "+" button
3. Click the "..." menu in the top right
4. Select "Import from file"
5. Choose `doc-sherlock-workflow.json`
6. Click "Import"

### 4. No Additional Dependencies Required

The workflow uses n8n's built-in HTTP Request node and JavaScript code nodes, so no additional packages are needed.

## Workflow Components

The workflow includes two main approaches:

### Approach 1: Direct API Call
- **Manual Trigger** - Manual trigger to start the process
- **Read PDF File** - Reads a PDF from the container filesystem
- **Prepare File Upload** - Prepares the file for multipart upload
- **POST to Doc-Sherlock API** - Sends the request to the analysis endpoint
- **Process Response** - Parses and formats the API response
- **Display Results** - Shows the analysis results

### Approach 2: Webhook Interface
- **Webhook Trigger** - HTTP webhook endpoint for file uploads
- **Process Upload** - Handles incoming file uploads
- **Analyze PDF** - Sends file to doc-sherlock API
- **Return Results** - Returns analysis results as JSON

## Usage

### Method 1: Direct File Analysis

1. The setup script automatically copies `tests/data/simple_cv.pdf` to the container
2. Execute the workflow by clicking the "Manual Trigger" node
3. View results in the workflow execution log

To test with different PDF files:

```bash
# Copy any PDF to the container
docker cp your-file.pdf myn8n:/home/node/data/sample.pdf

# Or copy one of the test files with specific issues
docker cp tests/data/low_contrast.pdf myn8n:/home/node/data/sample.pdf
docker cp tests/data/hidden_layer.pdf myn8n:/home/node/data/sample.pdf
docker cp tests/data/suspicious_metadata.pdf myn8n:/home/node/data/sample.pdf
```

Available test files in `tests/data/`:
- `simple_cv.pdf` - Basic CV document (default)
- `low_contrast.pdf` - Contains low contrast text
- `hidden_layer.pdf` - Has hidden layers
- `low_opacity.pdf` - Contains low opacity text
- `obscured_text.pdf` - Has obscured text elements
- `suspicious_metadata.pdf` - Contains suspicious metadata
- `tiny_font.pdf` - Uses very small fonts
- `encoding_anomaly.pdf` - Has encoding issues
- `only_images.pdf` - Contains only images
- `outside_boundary.pdf` - Has content outside boundaries
- `rendering_discrepancy.pdf` - Has rendering issues

### Method 2: Webhook Interface

1. The workflow exposes a webhook endpoint at `http://localhost:5678/webhook/doc-sherlock`
2. Send a POST request with a PDF file in the `file` field
3. Receive analysis results as JSON response

Example using curl:

```bash
curl -X POST \
  -F "file=@/path/to/your/document.pdf" \
  http://localhost:5678/webhook/doc-sherlock
```

## API Response Format

The doc-sherlock API returns findings in this format:

```json
{
  "findings": [
    {
      "finding_type": "HIDDEN_TEXT",
      "severity": "HIGH",
      "page_number": 1,
      "description": "Text with very low opacity detected",
      "location": {
        "x": 0.123,
        "y": 0.456,
        "width": 0.789,
        "height": 0.012
      }
    }
  ]
}
```

## Troubleshooting

### Connection Issues

If you get connection errors:

1. Ensure doc-sherlock API is running on the host
2. Check that the API URL in the workflow uses `http://host.docker.internal:8000/analyze`
3. For Linux hosts, you may need to use `http://172.17.0.1:8000/analyze`

### File Access Issues

If the workflow can't read files:

1. Ensure the PDF file exists in the container at `/home/node/data/sample.pdf`
2. Check file permissions
3. Verify the file path in the "Read PDF File" node

### Workflow Execution Issues

If workflow execution fails:

1. Check the execution log for detailed error messages
2. Ensure all nodes are properly connected
3. Verify the API endpoint is accessible
4. Check that the file upload format is correct

## Customization

You can modify the workflow to:

- Change the PDF file path
- Add email notifications for findings
- Store results in a database
- Integrate with other systems
- Add authentication
- Process multiple files in batch
- Add file validation and filtering
- Implement retry logic for failed requests

## Docker Network Notes

The workflow uses `host.docker.internal` to access the host machine from within the Docker container. This works on Docker Desktop for Mac and Windows. On Linux, you may need to:

1. Use `--add-host=host.docker.internal:host-gateway` when running the container
2. Or modify the API URL to use the host's IP address

## Security Considerations

- The webhook interface has no authentication by default
- Files are temporarily stored in the container
- Consider adding rate limiting for production use
- Validate file types and sizes before processing
- Implement proper error handling and logging

## n8n Specific Features

This workflow takes advantage of n8n's features:

- **Visual Workflow Editor** - Easy to modify and extend
- **Built-in HTTP Request Node** - No additional packages needed
- **JavaScript Code Nodes** - Custom logic for data processing
- **Webhook Support** - Easy API endpoint creation
- **Error Handling** - Built-in error handling and retry mechanisms
- **Execution History** - Track all workflow executions
- **Environment Variables** - Easy configuration management

## Performance Considerations

- Large PDF files may take longer to process
- Consider implementing file size limits
- Use n8n's queue mode for high-volume processing
- Monitor container resource usage
- Implement proper logging for debugging