#!/bin/bash

# Node-RED Docker container for Doc-Sherlock integration
# This script starts a Node-RED container with proper networking to access the host

# Container name
CONTAINER_NAME="mynodered"

# Check if container already exists
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Container $CONTAINER_NAME already exists."
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        echo "Container is running. Access Node-RED at: http://localhost:1880"
        echo "To stop: docker stop $CONTAINER_NAME"
    else
        echo "Starting existing container..."
        docker start $CONTAINER_NAME
        echo "Node-RED is now running at: http://localhost:1880"
    fi
else
    echo "Creating and starting new Node-RED container..."
    
    # Detect OS for proper host networking
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - use host-gateway for host.docker.internal
        docker run -d \
            --name $CONTAINER_NAME \
            --add-host=host.docker.internal:host-gateway \
            -p 1880:1880 \
            -v node_red_data:/data \
            nodered/node-red:latest
    else
        # macOS/Windows - host.docker.internal works by default
        docker run -d \
            --name $CONTAINER_NAME \
            -p 1880:1880 \
            -v node_red_data:/data \
            nodered/node-red:latest
    fi
    
    echo "Waiting for Node-RED to start..."
    sleep 5
    
    echo ""
    echo "Node-RED is now running!"
    echo "Access it at: http://localhost:1880"
    echo ""
    echo "Next steps:"
    echo "1. Import the flow: workflows/nodered/doc-sherlock-flow.json"
    echo "2. Install form-data package: docker exec -it $CONTAINER_NAME npm install form-data"
    echo "3. Start doc-sherlock API: doc-sherlock rest-service --host 0.0.0.0 --port 8000"
    echo ""
    echo "To stop Node-RED: docker stop $CONTAINER_NAME"
    echo "To remove container: docker rm $CONTAINER_NAME"
fi