#!/bin/bash

# n8n Docker container for Doc-Sherlock integration
# This script starts an n8n container with proper networking to access the host

# Container name
CONTAINER_NAME="myn8n"

# Check if container already exists
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Container $CONTAINER_NAME already exists."
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        echo "Container is running. Access n8n at: http://localhost:5678"
        echo "To stop: docker stop $CONTAINER_NAME"
    else
        echo "Starting existing container..."
        docker start $CONTAINER_NAME
        echo "n8n is now running at: http://localhost:5678"
    fi
else
    echo "Creating and starting new n8n container..."
    
    # Detect OS for proper host networking
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - use host-gateway for host.docker.internal
        docker run -d \
            --name $CONTAINER_NAME \
            --add-host=host.docker.internal:host-gateway \
            -p 5678:5678 \
            -v n8n_data:/home/node/.n8n \
            -v n8n_files:/home/node/data \
            -e N8N_HOST=localhost \
            -e N8N_PORT=5678 \
            -e N8N_PROTOCOL=http \
            -e WEBHOOK_URL=http://localhost:5678/ \
            -e GENERIC_TIMEZONE=UTC \
            n8nio/n8n:latest
    else
        # macOS/Windows - host.docker.internal works by default
        docker run -d \
            --name $CONTAINER_NAME \
            -p 5678:5678 \
            -v n8n_data:/home/node/.n8n \
            -v n8n_files:/home/node/data \
            -e N8N_HOST=localhost \
            -e N8N_PORT=5678 \
            -e N8N_PROTOCOL=http \
            -e WEBHOOK_URL=http://localhost:5678/ \
            -e GENERIC_TIMEZONE=UTC \
            n8nio/n8n:latest
    fi
    
    echo "Waiting for n8n to start..."
    sleep 10
    
    echo ""
    echo "n8n is now running!"
    echo "Access it at: http://localhost:5678"
    echo ""
    echo "Next steps:"
    echo "1. Import the workflow: workflows/n8n/doc-sherlock-workflow.json"
    echo "2. Start doc-sherlock API: doc-sherlock rest-service --host 0.0.0.0 --port 8000"
    echo "3. Test the workflow with the manual trigger"
    echo ""
    echo "Webhook endpoint: http://localhost:5678/webhook/doc-sherlock"
    echo ""
    echo "To stop n8n: docker stop $CONTAINER_NAME"
    echo "To remove container: docker rm $CONTAINER_NAME"
    echo "To view logs: docker logs $CONTAINER_NAME"
fi

echo ""
echo "Container status:"
docker ps -f name=$CONTAINER_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"