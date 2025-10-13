import os
import base64
from io import BytesIO
from PIL import Image
import cohere
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from tqdm import tqdm


# configs
IMAGE_DIR = ""
INDEX_NAME = ""
EMBEDDING_DIM = 1024
BATCH_SIZE = 96

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

# get all images
image_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg')]
print(f"Found {len(image_files)} images")

# process images
vectors = []
for filename in tqdm(image_files):
    # convert to data URI
    image_path = os.path.join(IMAGE_DIR, filename)
    data_uri = image_to_data_uri(image_path)
    
    # get embedding from Cohere
    response = co.embed(
        model="embed-v4.0",
        input_type="image",
        embedding_types=["float"],
        images=[data_uri],
        output_dimension=1024
    )
    embedding = response.embeddings.float[0]
    
    # extract metadata from filename
    parts = filename.replace('.jpg', '').split('_')
    lat, lon, heading = float(parts[0]), float(parts[1]), int(parts[2])
    
    # add metadata to vector
    vectors.append({
        "id": filename,
        "values": embedding,
        "metadata": {
            "filename": filename,
            "lat": lat,
            "lon": lon,
            "heading": heading,
            "country": "USA"
        }
    })
    
    # upload in batches
    if len(vectors) >= BATCH_SIZE:
        index.upsert(vectors=vectors)
        vectors = []

# upload remaining vectors
if vectors:
    index.upsert(vectors=vectors)

# print completion message
print("All images uploaded to Pinecone")