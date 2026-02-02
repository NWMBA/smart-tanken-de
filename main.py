"""
Smart-Tanken DE API
Author: Nathan Williams <hello@hinwise.com>
Description: High-performance fuel intelligence wrapper for the German market.
License: MIT
"""

import os
import math
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# --- INITIALIZATION ---
load_dotenv()
TANKER_API_KEY = os.getenv("TANKER_API_KEY")

app = FastAPI(
    title="Smart-Tanken DE API",
    description="Intelligence-driven fuel pricing and logistics benchmarking for Germany.",
    version="1.0.0",
    contact={
        "name": "NW Hinwise Solutions",
        "url": "https://www.hinwise.com", # Optional
        "email": "hello@hinwise.com",
    },
    license_info={
        "name": "MIT License",
    }
)
# --- 1. THE TOP PRIORITY ROUTE ---
# Define this before ANY middleware or other routes
@app.get("/health")
async def health_check():
    return {"status": "online", "message": "Smart-Tanken DE is operational"}

# --- 2. THE SECURITY MIDDLEWARE ---
@app.middleware("http")
async def verify_rapidapi_proxy(request: Request, call_next):
    # Normalize path: remove trailing slashes and dots
    path = request.url.path.rstrip("./ ") 
    
    # VIP Pass: Let these through without a secret
    # Added '/' to the list so your base URL also works for health checks
    if path in ["", "/health", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Check for Proxy Secret
    proxy_secret = request.headers.get("X-RapidAPI-Proxy-Secret")
    expected_secret = os.getenv("RAPIDAPI_PROXY_SECRET")
    
    if not proxy_secret or proxy_secret != expected_secret:
        return JSONResponse(
            status_code=403, 
            content={"detail": "Access denied. Use RapidAPI to access this resource."}
        )
    
    return await call_next(request)



# --- DATA LOADING ---
BASE_DIR = Path(__file__).resolve().parent
JSON_PATH = BASE_DIR / "plz_data.json"

def load_plz_data():
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as file:
            raw_list = json.load(file)
            # Standardize keys as 5-digit strings for reliable lookup
            return {str(item["plz"]).zfill(5): item for item in raw_list}
    except Exception as e:
        print(f"❌ Error loading PLZ database: {e}")
        return {}

PLZ_DATABASE = load_plz_data()

# --- UTILITY FUNCTIONS ---
def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula to calculate distance in km."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def get_daily_trend():
    """Predicts trend based on German intraday price waves."""
    hour = datetime.now().hour
    if 6 <= hour <= 10:
        return "RISING (Morning Peak)"
    elif 12 <= hour <= 15:
        return "FALLING (Lunch Wave)"
    elif 18 <= hour <= 21:
        return "LOW (Evening Minimum)"
    else:
        return "STABLE"

# --- DEPENDENCY / GATEKEEPER ---
def validate_location(
    plz: Optional[str] = Query(None, description="5-digit German Zip Code"),
    lat: Optional[float] = Query(None, description="Latitude coordinate"),
    lng: Optional[float] = Query(None, description="Longitude coordinate")
):
    """Ensures either a valid PLZ or Coords are provided."""
    if lat is not None and lng is not None:
        return {"lat": lat, "lng": lng, "type": "coords"}
    
    if plz:
        clean_plz = str(plz).zfill(5)
        geo = PLZ_DATABASE.get(clean_plz)
        if not geo:
            raise HTTPException(status_code=404, detail=f"PLZ {clean_plz} not found.")
        return {"lat": geo['lat'], "lng": geo['lng'], "type": "plz", "clean_plz": clean_plz}
    
    raise HTTPException(
        status_code=400, 
        detail="You must provide either 'plz' OR both 'lat' and 'lng'."
    )

# --- MAIN ENDPOINT ---
@app.get("/smart-fuel")
async def get_smart_fuel(
    location: dict = Depends(validate_location),
    fuel_type: str = Query("e5", enum=["e5", "e10", "diesel"]),
    radius: int = Query(5, ge=1, le=25, description="Search radius in km")
):
    start_lat = location['lat']
    start_lng = location['lng']

    # Creative Commons API Endpoint (Radius Search)
    url = f"https://creativecommons.tankerkoenig.de/json/list.php?lat={start_lat}&lng={start_lng}&rad={radius}&sort=dist&type=all&apikey={TANKER_API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data.get("ok"):
            return {"error": "Provider Error", "message": data.get("message")}

        stations = data.get("stations", [])
        
        # Filter for stations that have the requested fuel price
        valid_stations = []
        for s in stations:
            price = s.get(fuel_type)
            if price and price > 0:
                # If searching via PLZ center, we use the API distance.
                # If searching via custom Lat/Lng, we recalculate for precision.
                if location['type'] == 'coords':
                    s['dist'] = calculate_distance(start_lat, start_lng, s['lat'], s['lng'])
                valid_stations.append(s)

        if not valid_stations:
            return {"message": "No stations found with this fuel type in the selected range."}

        # Sort by Price (Primary) and Distance (Secondary)
        valid_stations.sort(key=lambda x: (x[fuel_type], x['dist']))
        
        # Statistics for the Hassle Score
        prices = [s[fuel_type] for s in valid_stations]
        avg_price = sum(prices) / len(prices)
        trend = get_daily_trend()

        # Build Top 3 Results
        top_deals = []
        for s in valid_stations[:3]:
            # Hassle Score: (Distance Penalty) - (Savings Reward)
            # Lower score is better.
            savings_vs_avg = avg_price - s[fuel_type]
            score = round((s['dist'] * 1.5) - (savings_vs_avg * 25), 2)
            
            top_deals.append({
                "name": s['name'],
                "brand": s['brand'],
                "price": s[fuel_type],
                "distance_km": s['dist'],
                "hassle_score": score,
                "verdict": "GO" if score < 1.0 else "MAYBE" if score < 3.0 else "TOO FAR"
            })

        return {
            "metadata": {
                "search_origin": "Coordinates" if location['type'] == 'coords' else f"PLZ {location.get('clean_plz')}",
                "regional_avg": round(avg_price, 3),
                "trend": trend,
                "timestamp": datetime.now().isoformat()
            },
            "best_deals": top_deals
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# --- ROOT ---
@app.get("/")
async def root():
    return {
        "app": "Smart-Tanken DE API",
        "status": "Live",
        "documentation": "/docs"
    }
    
 
@app.get("/diesel-index")
async def get_diesel_index(
    location: dict = Depends(validate_location),
    radius: int = Query(15, ge=5, le=50)
):
    start_lat = location['lat']
    start_lng = location['lng']

    # Note: When type is NOT 'all', Tankerkoenig returns the value in a 'price' field
    url = f"https://creativecommons.tankerkoenig.de/json/list.php?lat={start_lat}&lng={start_lng}&rad={radius}&sort=dist&type=diesel&apikey={TANKER_API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        stations = data.get("stations", [])
        
        # FIX: Look for 'price' since we requested 'type=diesel'
        prices = [s['price'] for s in stations if s.get('price') and s['price'] > 0]
        
        if not prices:
            # Fallback check: Sometimes they still use the fuel name even with type filter
            prices = [s['diesel'] for s in stations if s.get('diesel') and s['diesel'] > 0]

        if not prices:
            return {
                "error": "No diesel data available.",
                "debug": f"Found {len(stations)} stations, but no prices in 'price' or 'diesel' fields."
            }

        avg_price = sum(prices) / len(prices)
        
        # ... (keep the rest of your calculations: min, max, surcharge) ...
        return {
            "index_metadata": {
                "region": location.get('clean_plz') if location['type'] == 'plz' else "Coords",
                "stations_scanned": len(prices)
            },
            "market_rates": {
                "average_index": round(avg_price, 3),
                "low": min(prices),
                "high": max(prices)
            },
            "logistics_tools": {
                "suggested_surcharge_pct": max(0, round(((avg_price - 1.50) / 0.10) * 1.5, 2))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))