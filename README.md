# 🍽️ AI Recipe Recommender

An end-to-end AI-powered recipe recommendation web app that understands natural language queries and returns personalized recipe suggestions using semantic search and sentence embeddings.

> Type something like *"spicy chicken with garlic"* or *"quick vegetarian dinner under 30 minutes"* and the app finds the best matching recipes from a dataset of thousands.

---

## 🚀 Features

- **Semantic Search** — Uses `sentence-transformers` (MiniLM-L6-v2) to embed queries and recipes into vector space, then ranks results by cosine similarity
- **Smart Filters** — Filter recommendations by cuisine, course, diet type, and maximum cooking time
- **User Authentication** — Firebase-based login and signup system
- **Dockerized** — Fully containerized with Docker for consistent local and production environments
- **CI/CD Pipeline** — GitHub Actions workflow automatically builds and pushes a Docker image on every push to `main`
- **Clean Architecture** — Modular codebase split into `ml`, `data`, `ui`, `auth`, and `core` layers

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Web Framework | Streamlit 1.40 |
| ML / Embeddings | Sentence-Transformers (MiniLM-L6-v2) |
| Similarity Search | Scikit-learn (Cosine Similarity) |
| Data Processing | Pandas, NumPy |
| Authentication | Firebase Admin SDK |
| Containerization | Docker |
| CI/CD | GitHub Actions |

---

## 📁 Project Structure

```
reciperecommendernew/
├── .github/
│   └── workflows/
│       └── docker-image.yml   # CI/CD: builds & pushes Docker image
├── app/
│   ├── auth/                  # Firebase authentication
│   ├── core/
│   │   └── config.py          # App configuration (model name, top-k, batch size)
│   ├── data/
│   │   ├── repository.py      # Loads recipes & precomputed embeddings
│   │   └── text.py            # Builds combined text for embedding
│   ├── ml/
│   │   ├── embedder.py        # SentenceTransformer model loader & encoder
│   │   └── recommender.py     # Core recommendation & filter logic
│   └── ui/
│       ├── screens.py         # Auth and app screen definitions
│       └── streamlit_app.py   # Main Streamlit entry point
├── data/                      # Recipe dataset & precomputed embeddings
├── scripts/                   # Utility scripts
├── .env.example               # Environment variable template
├── Dockerfile                 # Container definition
└── requirements.txt           # Python dependencies
```

---

## ⚙️ How It Works

1. **Preprocessing** — Recipes are loaded and their text fields (name, ingredients, cuisine, etc.) are combined into a single string per recipe
2. **Embedding** — Each recipe string is encoded into a dense vector using `all-MiniLM-L6-v2`, a fast and accurate sentence embedding model
3. **Query Matching** — When a user submits a query, it is embedded using the same model and compared against all precomputed recipe embeddings using cosine similarity
4. **Ranking & Filtering** — The top-K most similar recipes are returned, with optional post-filtering by cuisine, course, diet, and cook time
5. **Display** — Results are rendered in a clean Streamlit UI with recipe details

---

## 🏃 Running Locally

### Option 1: Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/saibrahmanaidukaturi/reciperecommendernew.git
cd reciperecommendernew

# Copy environment variables
cp .env.example .env

# Build and run
docker build -t recipe-recommender .
docker run -p 8501:8501 recipe-recommender
```

Open your browser at `http://localhost:8501`

### Option 2: Local Python

```bash
# Clone the repo
git clone https://github.com/saibrahmanaidukaturi/reciperecommendernew.git
cd reciperecommendernew

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run the app
streamlit run app/ui/streamlit_app.py
```

---

## 🔐 Environment Variables

Copy `.env.example` to `.env` and fill in the required values:

```env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

For Firebase authentication, add your Firebase project credentials.

---

## 📦 CI/CD

Every push to `main` triggers a GitHub Actions workflow (`.github/workflows/docker-image.yml`) that:
- Builds the Docker image
- Pushes it to the container registry

---

## 🤝 Author

**Sai Brahma Naidu Katuri**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-saikaturi-blue?logo=linkedin)](https://www.linkedin.com/in/saikaturi)
[![GitHub](https://img.shields.io/badge/GitHub-saibrahmanaidukaturi-black?logo=github)](https://github.com/saibrahmanaidukaturi)
