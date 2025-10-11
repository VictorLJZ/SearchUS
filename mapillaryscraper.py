import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
token = os.getenv("MAPILLARY_TOKEN")

#test API calls

url = "https://graph.mapillary.com/images"
params = {
    "access_token": token,
    "bbox": "-73.989,40.756,-73.985,40.759", #times square
    "fields": "id,thumb_1024_url",
    "limit": 3
}

response = requests.get(url, params=params)
print(response.status_code)
data = response.json()
print(len(data.get("data",[])))

if data.get("data"):
    first_image = data["data"][0]
    img_url = first_image["thumb_1024_url"]
    img_id = first_image["id"]
    
    img_response = requests.get(img_url)
    with open(f"{img_id}.jpg", "wb") as f:
        f.write(img_response.content)
    print(f"Downloaded {img_id}.jpg")