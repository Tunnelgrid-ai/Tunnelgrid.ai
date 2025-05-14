from dotenv import load_dotenv
import os
from fastapi import FastAPI
from supabase import create_client, Client

load_dotenv()  # take environment variables from .env.

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

app = FastAPI()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/test-supabase")
def test_supabase():
    data = supabase.table("Test_Table").select("*").execute()
    return data.data
