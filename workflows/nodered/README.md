# Node-RED Flow for Doc-Sherlock API

This directory contains a Node-RED flow that demonstrates how to submit PDF files to the doc-sherlock API for analysis.

## Files

- `doc-sherlock-flow.json` - The Node-RED flow definition
- `runme.sh` - Docker command to start Node-RED
- `README.md` - This documentation

## Prerequisites

1. **Docker** - Required to run Node-RED in a container
2. **Doc-Sherlock API** - Must be running on the host machine

## Setup Instructions

### 1. Start Doc-Sherlock API

First, ensure the doc-sherlock REST API is running on your host machine:

```bash
# From the project root directory
doc-sherlock rest-service --host 0.0.0.0 --port 8000
```

### 2. Start Node-RED

Run the Node-RED container:

```bash
cd workflows/nodered
./runme.sh
```

This will start Node-RED on `http://localhost:1880`

### 3. Import the Flow

1. Open Node-RED in your browser: `http://localhost:1880`
2. Click the hamburger menu (☰) in the top right
3. Select "Import"
4. Choose "select a file to import" and select `doc-sherlock-flow.json`
5. Click "Import"

### 4. No Additional Dependencies Required

The flow uses built-in Node.js functionality to create multipart form data, so no additional npm packages are needed. The setup script handles everything automatically.

## Flow Components

The flow includes two main approaches:

### Approach 1: Direct API Call
- **Trigger Analysis** - Inject node to start the process
- **Read PDF File** - Reads a PDF from `/data/sample.pdf`
- **Prepare Multipart Form** - Creates form data for the API
- **POST to Doc-Sherlock API** - Sends the request
- **Process Findings** - Parses and summarizes the response

### Approach 2: Web Upload Interface
- **Upload Page Endpoint** - HTTP endpoint at `/upload`
- **Create Upload Form** - Generates an HTML upload form
- **Serve Upload Page** - Returns the HTML page

## Usage

### Method 1: Direct File Analysis

1. The setup script automatically copies `tests/data/simple_cv.pdf` as `/data/sample.pdf`
2. Click the "Trigger Analysis" inject node
3. View results in the debug panel

To test with different PDF files:

```bash
# Copy any PDF to the container
docker cp your-file.pdf mynodered:/data/sample.pdf

# Or copy one of the test files with specific issues
docker cp tests/data/low_contrast.pdf mynodered:/data/sample.pdf
docker cp tests/data/hidden_layer.pdf mynodered:/data/sample.pdf
docker cp tests/data/suspicious_metadata.pdf mynodered:/data/sample.pdf
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

### Method 2: Web Upload Interface

1. Navigate to `http://localhost:1880/upload`
2. Use the web form to select and upload a PDF
3. View analysis results on the page

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
2. Check that the API URL in the flow uses `http://host.docker.internal:8000/analyze`
3. For Linux hosts, you may need to use `http://172.17.0.1:8000/analyze`

### File Access Issues

If the flow can't read files:

1. Ensure the PDF file exists in the container at `/data/sample.pdf`
2. Check file permissions
3. Verify the file path in the "Read PDF File" node

### Form Data Issues

If multipart form upload fails:

1. Ensure `form-data` package is installed
2. Check the function node code for syntax errors
3. Verify the API endpoint is accessible

## Customization

You can modify the flow to:

- Change the PDF file path
- Add email notifications for findings
- Store results in a database
- Integrate with other systems
- Add authentication
- Process multiple files in batch

## Docker Network Notes

The flow uses `host.docker.internal` to access the host machine from within the Docker container. This works on Docker Desktop for Mac and Windows. On Linux, you may need to:

1. Use `--add-host=host.docker.internal:host-gateway` when running the container
2. Or modify the API URL to use the host's IP address

## Security Considerations

- The web upload interface has no authentication
- Files are temporarily stored in the container
- Consider adding rate limiting for production use
- Validate file types and sizes before processing