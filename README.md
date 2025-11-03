# SearchUS

A web application for searching San Francisco Street View images using semantic search powered by Cohere embeddings and Pinecone vector database.

## Project Structure

```
SearchUS/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utility functions
│   └── requirements.txt
├── frontend/            # Next.js frontend
│   ├── app/            # Next.js App Router pages
│   ├── components/     # React components
│   ├── lib/            # API client
│   ├── types/          # TypeScript types
│   └── utils/          # Utility functions
├── embed/              # Embedding pipeline (existing)
└── GoogleScraper/       # Street View scraper (existing)
```

## Features

- **Text Search**: Search Street View images using natural language queries
- **Image Search**: Upload an image to find similar Street View images
- **Interactive Results**: View results with similarity scores and metadata
- **Google Maps Integration**: Direct links to locations and Street View
- **Responsive Design**: Works on desktop and mobile devices

## Setup

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. Run the backend:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
bun install
```

3. Set up environment variables:
```bash
cp .env.local.example .env.local
# Edit .env.local and configure API URL
```

4. Run the frontend:
```bash
bun run dev
```

The app will be available at `http://localhost:3000`

## Environment Variables

### Backend (.env)
- `COHERE_API_KEY`: Your Cohere API key
- `PINECONE_API_KEY`: Your Pinecone API key

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)
- `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`: (Optional) Google Maps API key for embedded maps

## API Endpoints

### POST /api/search/text
Search by text query.

**Request:**
```json
{
  "query": "urban street scene",
  "top_k": 10
}
```

**Response:**
```json
{
  "results": [...],
  "query_type": "text",
  "total_results": 10
}
```

### POST /api/search/image
Search by image upload.

**Request:** multipart/form-data
- `file`: Image file
- `top_k`: Number of results (optional, default: 10)

**Response:**
```json
{
  "results": [...],
  "query_type": "image",
  "total_results": 10
}
```

## Development

### Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

## License

MIT
