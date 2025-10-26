import requests
import os

# Create assets folder if it doesn't exist
os.makedirs("frntend/public/assets", exist_ok=True)

# List of stable images
images = [
    # Products (replacements)
    ("smart_iot_monitor.jpg", "https://images.pexels.com/photos/373543/pexels-photo-373543.jpeg?auto=compress&cs=tinysrgb&w=600"),
    ("predictive_dashboard.jpg", "https://images.pexels.com/photos/669610/pexels-photo-669610.jpeg?auto=compress&cs=tinysrgb&w=600"),
    ("ai_maintenance_predictor.jpg", "https://images.pexels.com/photos/3861969/pexels-photo-3861969.jpeg?auto=compress&cs=tinysrgb&w=600"),
    
    # Testimonials
    ("john_smith.jpg", "https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg?auto=compress&cs=tinysrgb&w=600"),
    ("maria_garcia.jpg", "https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=600"),
    
  
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for filename, url in images:
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        with open(f"frontend/public/assets/{filename}", "wb") as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {filename} from {url} -> {e}")
