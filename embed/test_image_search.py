#!/usr/bin/env python3
"""
Test script for image similarity search using Pinecone.
Searches for similar images from the United States of America folder.
"""

import os
import sys
import random
import math
from pathlib import Path
from PIL import Image
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from search_images import search_by_image, INDEX_NAME, TOP_K


# Configuration
IMAGE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "GoogleScraper", "Downloads", "San Francisco"
)


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on Earth using Haversine formula.
    Returns distance in kilometers.
    """
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon1_rad = math.radians(lon1)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def get_image_files(image_dir):
    """Get all .jpg files from the image directory."""
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"Image directory not found: {image_dir}")
    
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
    if not image_files:
        raise ValueError(f"No .jpg files found in {image_dir}")
    
    return sorted(image_files)


def select_random_image(image_dir):
    """Select a random image from the directory."""
    image_files = get_image_files(image_dir)
    return os.path.join(image_dir, random.choice(image_files))


def display_results(query_image_path, results, top_k=TOP_K):
    """Display search results with detailed information."""
    query_filename = os.path.basename(query_image_path)
    
    # Extract query image metadata
    query_parts = query_filename.replace('.jpg', '').split('_')
    if len(query_parts) == 3:
        query_lat = float(query_parts[0])
        query_lon = float(query_parts[1])
        query_heading = int(query_parts[2])
    else:
        query_lat = query_lon = query_heading = None
    
    print("\n" + "="*80)
    print(f"QUERY IMAGE: {query_filename}")
    if query_lat is not None:
        print(f"Location: ({query_lat:.6f}, {query_lon:.6f})")
        print(f"Heading: {query_heading}°")
    print("="*80)
    
    print(f"\nFound {len(results.matches)} results (top {top_k}):\n")
    
    for i, match in enumerate(results.matches, 1):
        metadata = match.metadata
        score = match.score
        filename = metadata.get('filename', 'N/A')
        lat = metadata.get('lat')
        lon = metadata.get('lon')
        heading = metadata.get('heading', 'N/A')
        
        # Check if this is the query image itself
        is_query_image = filename == query_filename
        
        # Calculate distance if we have coordinates
        distance_km = None
        if query_lat is not None and lat is not None and lon is not None:
            distance_km = calculate_distance(query_lat, query_lon, lat, lon)
        
        # Format output
        match_indicator = " <-- QUERY IMAGE (Perfect Match!)" if is_query_image else ""
        print(f"{i}. Similarity Score: {score:.4f}{match_indicator}")
        print(f"   Filename: {filename}")
        
        if lat is not None and lon is not None:
            print(f"   Location: ({lat:.6f}, {lon:.6f})")
            
            if distance_km is not None:
                if distance_km < 0.1:
                    print(f"   Distance: {distance_km*1000:.1f} meters away")
                else:
                    print(f"   Distance: {distance_km:.2f} km away")
        
        print(f"   Heading: {heading}°")
        print(f"   Country: {metadata.get('country', 'N/A')}")
        print()
    
    # Summary statistics
    print("\n" + "-"*80)
    print("SUMMARY:")
    print(f"  • Query image found in results: {'YES' if any(m.metadata.get('filename') == query_filename for m in results.matches) else 'NO'}")
    if results.matches:
        top_score = results.matches[0].score
        print(f"  • Top similarity score: {top_score:.4f}")
        if top_score > 0.99:
            print(f"  • Status: ✅ Perfect match! (score > 0.99)")
        elif top_score > 0.9:
            print(f"  • Status: ✅ Very similar (score > 0.9)")
        elif top_score > 0.7:
            print(f"  • Status: ⚠️  Moderately similar (score > 0.7)")
        else:
            print(f"  • Status: ⚠️  Low similarity (score < 0.7)")
    
    # Count images from same location (within 100m)
    if query_lat is not None:
        same_location_count = sum(
            1 for m in results.matches
            if m.metadata.get('lat') and m.metadata.get('lon') and
            calculate_distance(query_lat, query_lon, m.metadata['lat'], m.metadata['lon']) < 0.1
        )
        print(f"  • Images from same location (within 100m): {same_location_count}/{len(results.matches)}")
    
    print("-"*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Test image similarity search using Pinecone",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with a random image
  python test_image_search.py
  
  # Test with a specific image
  python test_image_search.py --image "34.72898233613289_-88.94644607532702_182.jpg"
  
  # Test with full path
  python test_image_search.py --image "/path/to/image.jpg"
  
  # Get more results
  python test_image_search.py --top-k 20
        """
    )
    
    parser.add_argument(
        '--image', '-i',
        type=str,
        help='Path to query image (filename or full path). If not provided, a random image will be selected.'
    )
    
    parser.add_argument(
        '--top-k', '-k',
        type=int,
        default=TOP_K,
        help=f'Number of results to return (default: {TOP_K})'
    )
    
    parser.add_argument(
        '--random', '-r',
        action='store_true',
        help='Always use a random image (overrides --image if provided)'
    )
    
    args = parser.parse_args()
    
    # Determine which image to use
    if args.random or args.image is None:
        print("Selecting a random image...")
        query_image_path = select_random_image(IMAGE_DIR)
        print(f"Selected: {os.path.basename(query_image_path)}\n")
    else:
        # Check if it's a filename or full path
        if os.path.isabs(args.image):
            query_image_path = args.image
        else:
            # Try as filename in the image directory
            query_image_path = os.path.join(IMAGE_DIR, args.image)
        
        if not os.path.exists(query_image_path):
            print(f"Error: Image not found: {query_image_path}")
            print(f"\nAvailable images in directory:")
            image_files = get_image_files(IMAGE_DIR)
            print(f"  Total: {len(image_files)} images")
            print(f"  Example: {image_files[0]}")
            sys.exit(1)
    
    # Verify it's a valid image
    try:
        img = Image.open(query_image_path)
        print(f"Loaded image: {os.path.basename(query_image_path)} ({img.size[0]}x{img.size[1]})")
    except Exception as e:
        print(f"Error: Could not open image: {e}")
        sys.exit(1)
    
    # Perform the search
    print(f"\nSearching Pinecone index '{INDEX_NAME}'...")
    print(f"Requesting top {args.top_k} results...\n")
    
    try:
        results = search_by_image(query_image_path, top_k=args.top_k)
    except Exception as e:
        print(f"Error during search: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Display results
    display_results(query_image_path, results, top_k=args.top_k)


if __name__ == "__main__":
    main()

