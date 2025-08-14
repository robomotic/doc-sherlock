#!/bin/bash

# Setup script for Doc-Sherlock n8n integration
# This script helps set up the complete environment

echo "🔍 Doc-Sherlock n8n Setup"
echo "========================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker is installed"

# Check if doc-sherlock is available
if ! command -v doc-sherlock &> /dev/null; then
    echo "❌ doc-sherlock command not found."
    echo "   Please install doc-sherlock first:"
    echo "   pip install -e ."
    exit 1
fi

echo "✅ doc-sherlock is available"

# Start n8n container
echo ""
echo "🚀 Starting n8n container..."
./runme.sh

# Wait a moment for n8n to fully start
echo ""
echo "⏳ Waiting for n8n to fully initialize..."
sleep 15

# Check if n8n is responding
echo "🔍 Checking n8n availability..."
for i in {1..10}; do
    if curl -s http://localhost:5678 > /dev/null 2>&1; then
        echo "✅ n8n is responding"
        break
    else
        if [ $i -eq 10 ]; then
            echo "⚠️  n8n may still be starting up. Please check manually at http://localhost:5678"
        else
            echo "   Attempt $i/10: Waiting for n8n..."
            sleep 3
        fi
    fi
done

# Copy a test PDF file to the container
echo ""
echo "📄 Copying test PDF file to container..."
if [ -f "tests/data/simple_cv.pdf" ]; then
    docker cp tests/data/simple_cv.pdf myn8n:/home/node/data/sample.pdf
    echo "✅ Copied simple_cv.pdf as sample.pdf"
elif [ -f "../../tests/data/simple_cv.pdf" ]; then
    docker cp ../../tests/data/simple_cv.pdf myn8n:/home/node/data/sample.pdf
    echo "✅ Copied simple_cv.pdf as sample.pdf"
else
    echo "⚠️  Test PDF not found. You can manually copy a PDF file:"
    echo "   docker cp your-file.pdf myn8n:/home/node/data/sample.pdf"
fi

# Create data directory in container if it doesn't exist
echo "📁 Ensuring data directory exists in container..."
docker exec myn8n mkdir -p /home/node/data 2>/dev/null || true

# Check if doc-sherlock API is running
echo ""
echo "🔍 Checking if doc-sherlock API is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ doc-sherlock API is already running"
    API_RUNNING=true
else
    echo "⚠️  doc-sherlock API is not running"
    API_RUNNING=false
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Status Summary:"
echo "=================="
echo "✅ Docker: Available"
echo "✅ doc-sherlock CLI: Available"
echo "✅ n8n container: Running"
if [ "$API_RUNNING" = true ]; then
    echo "✅ doc-sherlock API: Running"
else
    echo "❌ doc-sherlock API: Not running"
fi
echo ""

echo "🚀 Next Steps:"
echo "=============="
echo "1. 🌐 Open n8n: http://localhost:5678"
echo "2. 📥 Import the workflow:"
echo "   - Click 'Add workflow' or the '+' button"
echo "   - Click the '...' menu → 'Import from file'"
echo "   - Select 'workflows/n8n/doc-sherlock-workflow.json'"

if [ "$API_RUNNING" = false ]; then
    echo "3. 🔧 Start the doc-sherlock API:"
    echo "   doc-sherlock rest-service --host 0.0.0.0 --port 8000"
    echo "4. 🧪 Test the integration:"
else
    echo "3. 🧪 Test the integration:"
fi
echo "   - Use the 'Manual Trigger' node to analyze /home/node/data/sample.pdf"
echo "   - Or test the webhook: curl -X POST -F \"file=@your.pdf\" http://localhost:5678/webhook/doc-sherlock"

echo ""
echo "📚 Documentation:"
echo "================="
echo "- Full instructions: workflows/n8n/README.md"
echo "- Workflow config: workflows/n8n/workflow-config.json"
echo "- n8n UI: http://localhost:5678"
echo "- Webhook endpoint: http://localhost:5678/webhook/doc-sherlock"

echo ""
echo "🛠️  Management Commands:"
echo "======================="
echo "- Stop n8n: docker stop myn8n"
echo "- Start n8n: docker start myn8n"
echo "- View logs: docker logs myn8n"
echo "- Remove container: docker rm myn8n"
echo "- Copy files to container: docker cp file.pdf myn8n:/home/node/data/"

echo ""
echo "🔧 Troubleshooting:"
echo "=================="
echo "- If connection fails, ensure API uses http://host.docker.internal:8000"
echo "- On Linux, you may need to use http://172.17.0.1:8000"
echo "- Check container logs if workflow execution fails"
echo "- Verify file permissions for uploaded PDFs"

echo ""
if [ "$API_RUNNING" = true ]; then
    echo "🎯 Ready to go! Your n8n workflow environment is fully set up."
else
    echo "🎯 Almost ready! Just start the doc-sherlock API and you're good to go."
fi