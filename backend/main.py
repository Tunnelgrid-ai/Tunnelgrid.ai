from dotenv import load_dotenv
import os
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
from supabase import create_client, Client
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()  # take environment variables from .env.

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
LOGODEV_SECRET_KEY = os.getenv("LOGODEV_SECRET_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


app = FastAPI()

# (Optional) Allow CORS for your frontend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

class BrandInsert(BaseModel):
    brand_name: str
    domain: str | None = None
    brand_description: str | None = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/test-supabase")
def test_supabase():
    data = supabase.table("Test_Table").select("*").execute()
    return data.data

@app.get("/api/brand-search")
async def brand_search(q: str = Query(..., min_length=1)):
    if not LOGODEV_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Logo.dev secret key not configured.")
    url = f"https://api.logo.dev/search?q={q}"
    headers = {"Authorization": f"Bearer: {LOGODEV_SECRET_KEY}"}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
        except httpx.HTTPStatusError as e:
            return JSONResponse(content={"error": str(e)}, status_code=resp.status_code)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/insert-brand")
async def insert_brand(brand: BrandInsert):
    result = supabase.table("brand").insert({
        "brand_name": brand.brand_name,
        "domain": brand.domain,
        "brand_description": brand.brand_description,
    }).execute()
    # Check for error in the raw JSON response
    raw = result.json()
    if "error" in raw and raw["error"]:
        raise HTTPException(status_code=400, detail=f"Insert failed: {raw['error']['message']}")
    if not result.data:
        raise HTTPException(status_code=400, detail="Insert failed: No data returned")
    return {"success": True, "data": result.data}

@app.post("/api/brand-llama")
async def brand_llama(request: Request):
    data = await request.json()
    brand_name = data.get("brand_name")
    domain = data.get("domain")
    if not brand_name or not domain:
        raise HTTPException(status_code=400, detail="brand_name and domain required")

    # Strict system prompt for JSON-only output
    system_prompt = (
        "You are a helpful assistant. Given a brand name and domain, "
        "return a JSON object with two keys: "
        "\"description\" (a concise brand description, max 500 chars) and "
        "\"product\" (an array of up to 5 product names). "
        "No extra keys, no preamble, no postamble, just pure JSON. "
        "Use up-to-date knowledge as of May 2025. "
        "The description should summarize the company's offerings, services, or core focus clearly and professionally. "
        "The \"product\" list should highlight the most prominent product lines, services, or categories associated with the brand. "
        "If uncertain, make an informed generalization, but never fabricate specific product names. "
        "Output must always be valid JSON."
    )

    user_prompt = f"Brand: {brand_name}\nDomain: {domain}"

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        groq_resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        if groq_resp.status_code != 200:
            raise HTTPException(status_code=groq_resp.status_code, detail=groq_resp.text)
        result = groq_resp.json()
        # The model's response is in result['choices'][0]['message']['content']
        try:
            content = result["choices"][0]["message"]["content"]
            import json
            parsed = json.loads(content)
            if not isinstance(parsed, dict) or "description" not in parsed or "product" not in parsed:
                raise ValueError("Invalid response structure")
            if not isinstance(parsed["product"], list):
                raise ValueError("product must be a list")
            parsed["product"] = parsed["product"][:5]
            return parsed
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse Groq response: {e}")

@app.post("/api/update-brand-product")
async def update_brand_product(request: Request):
    data = await request.json()
    brand_name = data.get("brand_name")
    brand_description = data.get("brand_description")
    product = data.get("product", [])

    if not brand_name or not brand_description or not isinstance(product, list):
        raise HTTPException(status_code=400, detail="brand_name, brand_description, and product required")

    # 1. Find the brand row
    brand_resp = supabase.table("brand").select("brand_id").eq("brand_name", brand_name).limit(1).execute()
    if not brand_resp.data or len(brand_resp.data) == 0:
        raise HTTPException(status_code=404, detail="Brand not found")
    brand_id = brand_resp.data[0]["brand_id"]

    # 2. Update brand_description
    supabase.table("brand").update({"brand_description": brand_description}).eq("brand_id", brand_id).execute()

    # 3. Insert product (avoid duplicates)
    for prod in product[:5]:
        if not prod:
            continue
        supabase.table("product").insert({
            "brand_id": brand_id,
            "product_name": prod
        }).execute()

    return {"success": True}
