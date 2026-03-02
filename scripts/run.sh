#!/bin/bash
set -e

echo "🚀 Starting Recipe Recommender..."
docker run -p 8501:8501 \
  -v $(pwd)/.streamlit:/app/.streamlit \
  --env-file .env \
  recipe-recommender:latest

