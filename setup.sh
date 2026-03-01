#!/bin/bash

echo "Creating project structure..."

mkdir -p app/ui
mkdir -p app/core
mkdir -p app/data
mkdir -p app/ml
mkdir -p app/auth
mkdir -p data
mkdir -p .streamlit

touch app/ui/streamlit_app.py
touch app/ui/screens.py
touch app/core/config.py
touch app/core/session_keys.py
touch app/data/repository.py
touch app/data/text.py
touch app/ml/bert_embedder.py
touch app/ml/recommender.py
touch app/auth/firebase_auth.py
touch requirements.txt
touch Dockerfile
touch .dockerignore
touch .streamlit/config.toml
touch styles.css

echo "Project structure created successfully."
