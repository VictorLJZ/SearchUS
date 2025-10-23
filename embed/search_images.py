import os
import base64
from io import BytesIO
from PIL import Image
import cohere
from pinecone import Pinecone
from dotenv import load_dotenv

from embed_images import image_to_data_uri


# function to search by text
def search_by_text(query_text, top_k=TOP_K, filter_dict=None):
    print(f"Searching for: '{query_text}'")
    
    # get text embedding from Cohere
    response = co.embed(
        model="embed-v4.0",
        input_type="search_query",
        embedding_types=["float"],
        texts=[query_text],
        output_dimension=1024
    )
    query_embedding = response.embeddings.float[0]
    
    # query Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter=filter_dict
    )
    
    return results


# function to search by image
def search_by_image(image_path, top_k=TOP_K, filter_dict=None):
    print(f"Searching with image: {image_path}")
    
    # convert image to data URI
    data_uri = image_to_data_uri(image_path)
    
    # get image embedding from Cohere
    response = co.embed(
        model="embed-v4.0",
        input_type="image",
        embedding_types=["float"],
        images=[data_uri],
        output_dimension=1024
    )
    query_embedding = response.embeddings.float[0]
    
    # query Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter=filter_dict
    )
    
    return results


# ------------------------------------------------------------------------------------------------
# configs
INDEX_NAME = "street-view-images"
TOP_K = 10  # number of results to return

# load environment variables
load_dotenv()

# initialize clients
co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(INDEX_NAME)


# function to print results
def print_results(results):
    print(f"\nFound {len(results.matches)} results:")
    
    for i, match in enumerate(results.matches, 1):
        metadata = match.metadata
        print(f"{i}. Score: {match.score:.4f}")
        print(f"   Filename: {metadata.get('filename', 'N/A')}")
        print(f"   Location: ({metadata.get('lat', 'N/A')}, {metadata.get('lon', 'N/A')})")
        print(f"   Heading: {metadata.get('heading', 'N/A')}°")
        print(f"   Country: {metadata.get('country', 'N/A')}")


if __name__ == "__main__":
    # ask user for search query
    query = input("What are you looking for? ")
    
    # search
    print(f"\nSearching for: '{query}'...")
    results = search_by_text(query)
    
    # print results
    print_results(results)
