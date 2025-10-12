import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import geopandas as gpd
from dotenv import load_dotenv, find_dotenv
from pyogrio import read_dataframe
from tqdm import tqdm

# Find and load .env from root directory
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    raise FileNotFoundError("No .env file found in root directory")

# Get API key
key = os.getenv("MAPS_API_KEY")
if not key:
    raise ValueError("MAPS_API_KEY not found in .env file")

scrape_type = 0
samples_per_country = 5
pano = True
num_workers = 8  # M1 Pro optimal
image_list = []
# Cache to store loaded GeoDataFrames to prevent reloading
gdf_cache = {}

# Load only Region 1 countries
regions_to_countries_dict = {
    "Region 1": ["United States of America", "Canada"]
}

# Dictionary to map regions to shapefiles
region_shp_paths = {
    "Region 1": './GRIP4/GRIP4_Region1_vector_shp/GRIP4_region1.shp'
}

def check_existing_images(save_dir):
    """
    Returns set of existing image coordinates to avoid duplicates.
    """
    existing_coords = set()
    if os.path.exists(save_dir):
        for filename in os.listdir(save_dir):
            if filename.endswith('.jpg'):
                # Extract coordinates from filename
                parts = filename.replace('.jpg', '').split('_')
                if len(parts) >= 2:
                    try:
                        lat, lon = float(parts[0]), float(parts[1])
                        existing_coords.add((lat, lon))
                    except ValueError:
                        continue
    return existing_coords

def generate_ll_systematic(gdf, n2d=200, spacing_meters=100):
    """
    Generates coordinates with systematic sampling every X meters along roads.
    """
    ll_list = []
    n_roads = int(n2d / 2)
    
    # Sample roads systematically
    roads = gdf.sample(n=n_roads) if len(gdf) > n_roads else gdf
    
    for road in roads['geometry']:
        if road.geom_type == 'LineString':
            # Sample points along the entire road at regular intervals
            road_length = road.length
            num_points = max(1, int(road_length / spacing_meters))
            
            for i in range(num_points):
                # Interpolate point along the road
                point = road.interpolate(i * road_length / num_points)
                lat, lon = point.y, point.x
                
                # Add all 4 directions
                ll_list.extend([
                    (lat, lon, 2),   # North
                    (lat, lon, 92), # East  
                    (lat, lon, 182), # South
                    (lat, lon, 272)  # West
                ])
    
    return ll_list

def load_shapefile_for_country(country):
    """
    Loads the shapefile for Region 1 (US and Canada only).
    """
    # Check if country is in Region 1
    if country in regions_to_countries_dict["Region 1"]:
        # If region is cached, use the cached GeoDataFrame
        if "Region 1" in gdf_cache:
            print(f"Using cached GeoDataFrame for Region 1")
            return gdf_cache["Region 1"]
        else:
            # Load the shapefile for Region 1 and cache it
            shapefile_path = region_shp_paths["Region 1"]
            print(f"Loading shapefile for Region 1: {shapefile_path}")
            gdf = read_dataframe(shapefile_path)
            gdf_cache["Region 1"] = gdf
            return gdf
    else:
        raise ValueError(f"{country} not found in Region 1. Only US and Canada are supported.")


# The following function is adapted from Street_View_API_scraping https://github.com/BLorenzoF/Street_View_API_scraping.git
def MetaParse(MetaUrl):
    """
    Fetches and parses the metadata from the Google Street View API.

    Parameters:
        MetaUrl (str): The URL to request metadata from the Google Street View API.

    Returns:
        tuple: A tuple containing the date, panorama ID, latitude, and longitude if successful, otherwise None.
    """
    try:
        # Send a request to the provided metadata URL
        response = urllib.request.urlopen(MetaUrl)
        jsonRaw = response.read()
        jsonData = json.loads(jsonRaw)

        # Check if the response contains valid data and extract metadata
        if jsonData['status'] == "OK":
            return (jsonData.get('date', None), jsonData['pano_id'], jsonData['location']['lat'], jsonData['location']['lng'])
        else:
            return None
    except Exception as e:
        # Catch and print any errors that occur during the metadata fetch
        print(f"Error fetching metadata: {e}")
        return None


# The following function is adapted from Street_View_API_scraping https://github.com/BLorenzoF/Street_View_API_scraping.git
def GetStreetLL(Lat, Lon, Head, SaveLoc, existing_coords, retries=3):
    """
    Downloads a Street View image from the given latitude, longitude, and heading.

    Parameters:
        Lat (float): The latitude of the location.
        Lon (float): The longitude of the location.
        Head (int): The heading in degrees (N, E, S, W).
        SaveLoc (str): The directory where the image will be saved.
        existing_coords (set): Set of existing coordinates to avoid duplicates.
        retries (int): Number of retry attempts for downloading the image (default is 3).

    Returns:
        tuple: A tuple containing metadata and the success flag (1 for success, 0 for failure).
    """
    # Check if we already have images at this location
    if (Lat, Lon) in existing_coords:
        return None, 0  # Skip duplicate location
    
    # Construct the base URL for fetching the Street View image
    base = r"https://maps.googleapis.com/maps/api/streetview"
    size = r"?size=640x640&fov=90&pitch=0&location="  # Improved settings
    end = f"{Lat},{Lon}&heading={Head}&key={key}"
    MyUrl = base + size + end
    MetaUrl = base + r"/metadata" + size + end

    for attempt in range(retries):
        try:
            # Fetch metadata for the location
            met_data = MetaParse(MetaUrl)
            if met_data:
                date, pano_id, lat, lon = met_data
                if pano_id:
                    # Construct the filename and save the image
                    filename = f"{lat}_{lon}_{int(Head)}.jpg"
                    urllib.request.urlretrieve(MyUrl, os.path.join(SaveLoc, filename))
                    return [(date, pano_id, lat, lon, filename), 1]
        except urllib.error.HTTPError as e:
            # Handle HTTP errors and retry after a delay
            print(f"HTTPError: {e}, retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            # Handle other exceptions and print the error message
            print(f"Error downloading image: {e}")
            return None, 0

    # If all retry attempts fail, return failure
    return None, 0


def download_images_from_country(country_name, total_images_to_download, save_dir):
    """
    Downloads images from Google Street View for a given country.

    Parameters:
        country_name (str): The name of the country to scrape images from.
        total_images_to_download (int): The total number of images to download for the country.
        save_dir (str): The directory where the images will be saved.

    Returns:
        None
    """
    # Check existing images to avoid duplicates
    existing_coords = check_existing_images(save_dir)
    print(f"Found {len(existing_coords)} existing locations, skipping duplicates...")
    
    # Load the shapefile containing the road geometries for the country
    gdf = load_shapefile_for_country(country_name)
    images_downloaded = 0

    # Continue downloading images until the required number of images is reached
    while images_downloaded < total_images_to_download * 4:
        n2d = total_images_to_download - int(images_downloaded / 4)
        data_list = generate_ll_systematic(gdf, n2d, spacing_meters=50)  # 50m spacing for better coverage

        if not data_list:
            print("No points generated, exiting.")
            break

        # Use a thread pool to download images concurrently
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(GetStreetLL, i[0], i[1], i[2], save_dir, existing_coords)
                for i in data_list
            ]

            # Process the results from the threads
            for future in tqdm(as_completed(futures), total=len(futures),
                               desc=f'Downloading Images from {country_name}'):
                try:
                    result = future.result()
                    if result:
                        image_metadata, images_downloaded_in_current_iteration = result
                        images_downloaded += images_downloaded_in_current_iteration

                        if image_metadata:
                            image_list.append(image_metadata)
                except Exception as e:
                    print(f"Error downloading image: {e}")

    print(f"Downloaded {images_downloaded} images from {country_name}.")

def main():
    """
    Main function that starts the scraping process for US/Canada only.
    """
    global image_list
    image_list = []
    DownLoc = "./Downloads"

    # Scrape an individual country (US or Canada)
    country_name = input("What country would you like to scrape (United States of America or Canada): ")
    
    if country_name not in ["United States of America", "Canada"]:
        print("Error: Only United States of America and Canada are supported.")
        return
        
    print(f"Starting scrape for {country_name}")
    country_dir = os.path.join(DownLoc, country_name)
    if not os.path.exists(country_dir):
        os.mkdir(country_dir)
        print(f'Created dir: {country_dir}\n')

    try:
        download_images_from_country(country_name, total_images_to_download=samples_per_country, save_dir=country_dir)
    except Exception as e:
        print(f"Error scraping images: {e}")
    print(f"Scrape completed for {country_name}\n")

    # Save metadata to CSV
    if image_list:
        import pandas as pd
        df = pd.DataFrame(image_list, columns=['date', 'pano_id', 'lat', 'lon', 'filename'])
        metadata_path = os.path.join(country_dir, 'metadata.csv')
        df.to_csv(metadata_path, index=False)
        print(f"Metadata saved to: {metadata_path}")

# Direct execution
if key:
    print("*** Starting Scrape ***")
    main()
else:
    print("Error: API key not found")