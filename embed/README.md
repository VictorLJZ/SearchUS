# Image Embedding Pipeline

Embeds Street View images using Cohere Embed v4 and uploads to Pinecone.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add to your `.env`:
```
COHERE_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
```

3. Run the pipeline:
```bash
python embed_images.py
```

That's it! The script automatically creates the Pinecone index if it doesn't exist.

## What it does

- Checks if Pinecone index exists (creates it if not)
- Loads all `.jpg` images from Google Street View downloads
- Converts images to data URIs
- Generates 1024-dim embeddings using Cohere Embed v4.0
- Extracts metadata (lat, lon, heading) from filenames
- Uploads to Pinecone in batches of 96

## Output

Each vector in Pinecone contains:
- **ID**: filename
- **Vector**: 1024-dim Cohere embedding
- **Metadata**: filename, lat, lon, heading, country

