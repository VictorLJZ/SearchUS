# Quick Start Guide

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- API keys for Cohere and Pinecone

## Step 1: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your COHERE_API_KEY and PINECONE_API_KEY

# Run backend server
uvicorn app.main:app --reload --port 8000
```

Backend will be running at `http://localhost:8000`

## Step 2: Frontend Setup

```bash
# Open a new terminal, navigate to frontend
cd frontend

# Install dependencies
bun install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL=http://localhost:8000
# Optionally add NEXT_PUBLIC_GOOGLE_MAPS_API_KEY for embedded maps

# Run frontend development server
bun run dev
```

Frontend will be running at `http://localhost:3000`

## Step 3: Use the Application

1. Open `http://localhost:3000` in your browser
2. Choose between Text Search or Image Search
3. Enter a query or upload an image
4. View results with similarity scores
5. Click "Maps" or "Street View" buttons to view locations

## API Testing

You can test the backend API directly:

### Text Search
```bash
curl -X POST http://localhost:8000/api/search/text \
  -H "Content-Type: application/json" \
  -d '{"query": "urban street scene", "top_k": 5}'
```

### Image Search
```bash
curl -X POST http://localhost:8000/api/search/image \
  -F "file=@/path/to/image.jpg" \
  -F "top_k=5"
```

## Troubleshooting

### Backend Issues
- Ensure `.env` file exists with correct API keys
- Check that Pinecone index `san-francisco-streetview` exists
- Verify port 8000 is not in use

### Frontend Issues
- Ensure backend is running on port 8000
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Clear browser cache if experiencing issues
- Check browser console for errors

### CORS Issues
- Backend CORS is configured for `localhost:3000`
- If using different port, update `backend/app/main.py` origins list

## Project Structure

```
SearchUS/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/     # API endpoints
│   │   ├── services/# Business logic
│   │   └── utils/   # Utilities
│   └── requirements.txt
├── frontend/         # Next.js frontend
│   ├── app/         # Pages
│   ├── components/  # React components
│   ├── lib/         # API client
│   └── package.json
└── embed/           # Embedding pipeline
```

## Next Steps

- Ensure your Pinecone index has embedded images (run `embed/embed_images.py`)
- Test with various search queries
- Customize styling in `frontend/app/globals.css`
- Add Google Maps API key for embedded maps (optional)

