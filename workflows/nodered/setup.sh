#!/bin/bash

# Setup script for Doc-Sherlock Node-RED integration
# This script helps set up the complete environment

echo "🔍 Doc-Sherlock Node-RED Setup"
echo "=============================="
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

# Start Node-RED container
echo ""
echo "🚀 Starting Node-RED container..."
./runme.sh

# Wait a moment for Node-RED to fully start
echo ""
echo "⏳ Waiting for Node-RED to fully initialize..."
sleep 10

# Note: No external npm packages required - using built-in Node.js functionality
echo "📦 Node-RED container ready (no additional packages needed)"

# Copy a test PDF file to the container
echo "📄 Copying test PDF file to container..."
if [ -f "tests/data/simple_cv.pdf" ]; then
    docker cp tests/data/simple_cv.pdf mynodered:/data/sample.pdf
    echo "✅ Copied simple_cv.pdf as sample.pdf"
elif [ -f "../../tests/data/simple_cv.pdf" ]; then
    docker cp ../../tests/data/simple_cv.pdf mynodered:/data/sample.pdf
    echo "✅ Copied simple_cv.pdf as sample.pdf"
else
    echo "⚠️  Test PDF not found. You can manually copy a PDF file:"
    echo "   docker cp your-file.pdf mynodered:/data/sample.pdf"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. 🌐 Open Node-RED: http://localhost:1880"
echo "2. 📥 Import the flow:"
echo "   - Click the hamburger menu (☰) → Import"
echo "   - Select 'workflows/nodered/doc-sherlock-flow.json'"
echo "3. 🔧 Start the doc-sherlock API:"
echo "   doc-sherlock rest-service --host 0.0.0.0 --port 8000"
echo "4. 🧪 Test the integration:"
echo "   - Use the 'Trigger Analysis' node with a PDF at /data/sample.pdf"
echo "   - Or visit http://localhost:1880/upload for web interface"
echo ""
echo "📚 For detailed instructions, see: workflows/nodered/README.md"
echo ""
echo "To stop everything:"
echo "  docker stop mynodered"