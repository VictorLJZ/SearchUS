import os
import base64
from io import BytesIO
from PIL import Image
import cohere
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


# configs
IMAGE_DIR = "../GoogleScraper/Downloads/San Francisco"
INDEX_NAME = "san-francisco-streetview"
EMBEDDING_DIM = 1024
PINECONE_BATCH_SIZE = 96  # Pinecone upload batch size
COHERE_BATCH_SIZE = 20  # Cohere API batch size (process multiple images per API call)
MAX_WORKERS = 5  # Number of parallel threads for concurrent API calls

# load environment variables
load_dotenv()

# initialize Cohere client
co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))

# initialize Pinecone and create index if needed
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
if INDEX_NAME not in pc.list_indexes().names():
    print(f"Creating index '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    print(f"Index '{INDEX_NAME}' created")
else:
    print(f"Index '{INDEX_NAME}' already exists")
index = pc.Index(INDEX_NAME)

# function to convert image to data URI
def image_to_data_uri(image_path):
    img = Image.open(image_path)
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

# function to get already embedded IDs from Pinecone
def get_existing_ids(index, max_ids=10000):
    """Fetch existing IDs from Pinecone to skip already embedded images"""
    print("Checking for already embedded images...")
    existing_ids = set()
    try:
        # Use fetch with empty list to get stats, then list vectors
        # Note: Pinecone doesn't have a direct "list all IDs" endpoint
        # We'll use a workaround by querying with a dummy vector to get some results
        # For better performance, we'll track processed files differently
        # Actually, we can use index.describe_index_stats() and fetch by IDs
        stats = index.describe_index_stats()
        print(f"Index contains {stats.total_vector_count} vectors")
        
        # Since we can't list all IDs easily, we'll track them as we process
        # Return empty set - we'll check during processing
        return existing_ids
    except Exception as e:
        print(f"Warning: Could not fetch existing IDs: {e}")
        return existing_ids

# function to check if IDs exist in Pinecone
def check_ids_exist(index, ids):
    """Check which IDs already exist in Pinecone"""
    if not ids:
        return set()
    try:
        # Fetch vectors by IDs - returns only existing ones
        result = index.fetch(ids=list(ids))
        return set(result.vectors.keys())
    except Exception as e:
        print(f"Warning: Error checking IDs: {e}")
        return set()

# function to extract metadata from filename
def extract_metadata(filename):
    parts = filename.replace('.jpg', '').split('_')
    if len(parts) >= 3:
        lat, lon, heading = float(parts[0]), float(parts[1]), int(parts[2])
        return {
            "filename": filename,
            "lat": lat,
            "lon": lon,
            "heading": heading,
            "city": "San Francisco",
            "country": "USA"
        }
    return None

# function to process a batch of images
def process_image_batch(image_batch, existing_ids):
    """Process a batch of images and return vectors"""
    vectors = []
    images_to_embed = []
    filenames_to_embed = []
    
    # Filter out already embedded images and prepare data URIs
    for filename, image_path in image_batch:
        if filename in existing_ids:
            continue
        
        try:
            data_uri = image_to_data_uri(image_path)
            images_to_embed.append(data_uri)
            filenames_to_embed.append(filename)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    if not images_to_embed:
        return []
    
    # Get embeddings from Cohere in batch
    try:
        response = co.embed(
            model="embed-v4.0",
            input_type="image",
            embedding_types=["float"],
            images=images_to_embed,
            output_dimension=1024
        )
        embeddings = response.embeddings.float
        
        # Create vectors with metadata
        for i, filename in enumerate(filenames_to_embed):
            metadata = extract_metadata(filename)
            if metadata:
                vectors.append({
                    "id": filename,
                    "values": embeddings[i],
                    "metadata": metadata
                })
    except Exception as e:
        print(f"Error getting embeddings for batch: {e}")
        # Fallback: process one by one if batch fails
        for filename, image_path in image_batch:
            if filename in existing_ids:
                continue
            try:
                data_uri = image_to_data_uri(image_path)
                response = co.embed(
                    model="embed-v4.0",
                    input_type="image",
                    embedding_types=["float"],
                    images=[data_uri],
                    output_dimension=1024
                )
                embedding = response.embeddings.float[0]
                metadata = extract_metadata(filename)
                if metadata:
                    vectors.append({
                        "id": filename,
                        "values": embedding,
                        "metadata": metadata
                    })
            except Exception as e2:
                print(f"Error processing {filename}: {e2}")
                continue
    
    return vectors

# get all images
image_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg')]
print(f"Found {len(image_files)} images")

# Check for already embedded images (in batches to avoid overwhelming API)
print("Checking which images are already embedded...")
existing_ids = set()
check_batch_size = 100
for i in range(0, len(image_files), check_batch_size):
    batch_ids = image_files[i:i+check_batch_size]
    existing_ids.update(check_ids_exist(index, batch_ids))
    if (i // check_batch_size + 1) % 10 == 0:
        print(f"Checked {min(i+check_batch_size, len(image_files))}/{len(image_files)} images...")

images_to_process = [(f, os.path.join(IMAGE_DIR, f)) for f in image_files if f not in existing_ids]
print(f"Skipping {len(existing_ids)} already embedded images")
print(f"Processing {len(images_to_process)} new images")

if not images_to_process:
    print("All images are already embedded!")
    exit(0)

# Split images into batches for Cohere API
image_batches = []
for i in range(0, len(images_to_process), COHERE_BATCH_SIZE):
    image_batches.append(images_to_process[i:i+COHERE_BATCH_SIZE])

print(f"Processing {len(image_batches)} batches with {COHERE_BATCH_SIZE} images each")
print(f"Using {MAX_WORKERS} parallel workers")

# Process batches in parallel
all_vectors = []
completed_batches = 0

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    # Submit all batches
    future_to_batch = {executor.submit(process_image_batch, batch, existing_ids): batch for batch in image_batches}
    
    # Process completed batches
    with tqdm(total=len(image_batches), desc="Processing batches") as pbar:
        for future in as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                vectors = future.result()
                all_vectors.extend(vectors)
                completed_batches += 1
                pbar.update(1)
            except Exception as e:
                print(f"Error processing batch: {e}")

print(f"\nGenerated {len(all_vectors)} embeddings")

# Upload to Pinecone in batches
print(f"Uploading to Pinecone in batches of {PINECONE_BATCH_SIZE}...")
uploaded = 0
for i in range(0, len(all_vectors), PINECONE_BATCH_SIZE):
    batch = all_vectors[i:i+PINECONE_BATCH_SIZE]
    try:
        index.upsert(vectors=batch)
        uploaded += len(batch)
        print(f"Uploaded {uploaded}/{len(all_vectors)} vectors...", end='\r')
    except Exception as e:
        print(f"\nError uploading batch: {e}")

print(f"\n✓ Successfully uploaded {uploaded} vectors to Pinecone")
print("All images processed!")
