from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from typing import List
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Define the brand model
class Brand(BaseModel):
    name: str
    domain: str
    logo: str

# Brandfetch API configuration
BRANDFETCH_API_KEY = os.getenv("BRANDFETCH_API_KEY")
BRANDFETCH_BASE_URL = "https://api.brandfetch.io/v2"

# create the api endpoint
@app.get("/search_brands", response_model=List[Brand])
async def search_brands(query: str):
    # Don't search if query is too short
    if len(query) < 1:
        return []

    if not BRANDFETCH_API_KEY:
        raise HTTPException(status_code=500, detail="Brandfetch API key not configured")

    async with httpx.AsyncClient() as client:
        try:
            # Search for brands
            search_response = await client.get(
                f"{BRANDFETCH_BASE_URL}/search/{query}",
                headers={"Authorization": f"Bearer {BRANDFETCH_API_KEY}"}
            )
            search_response.raise_for_status()
            search_results = search_response.json()

            # Get detailed information for each brand
            brands = []
            for result in search_results:
                try:
                    # Get brand details
                    brand_response = await client.get(
                        f"{BRANDFETCH_BASE_URL}/brands/{result['domain']}",
                        headers={"Authorization": f"Bearer {BRANDFETCH_API_KEY}"}
                    )
                    brand_response.raise_for_status()
                    brand_data = brand_response.json()

                    # Extract logo URL (using the first logo if available)
                    logo_url = brand_data.get('logos', [{}])[0].get('formats', [{}])[0].get('src', '')
                    
                    brands.append(Brand(
                        name=brand_data.get('name', ''),
                        domain=brand_data.get('domain', ''),
                        logo=logo_url
                    ))
                except httpx.HTTPError:
                    continue  # Skip brands that fail to fetch details

            return brands

        except httpx.HTTPError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Error fetching from Brandfetch API")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
