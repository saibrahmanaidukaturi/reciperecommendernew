#!/bin/bash
set -e

echo "🔨 Building Docker image..."
docker build -t recipe-recommender:latest .

echo "✅ Build complete!"
echo "🚀 Run with: docker run -p 8501:8501 recipe-recommender:latest"

