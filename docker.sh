#!/bin/bash

# Build the Docker image
echo "Building ollama-model-manager Docker image..."
docker build -t ollama-model-manager .

if [ $? -eq 0 ]; then
    echo "Docker image built successfully!"
    echo "You can run it with: docker run -p 8000:8000 -e OLLAMA_URL=http://your-ollama-host:11434 ollama-model-manager"
else
    echo "Docker build failed"
    exit 1
fi
