from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import os
import psycopg

app = FastAPI()
load_dotenv()
database_url = os.getenv("DATABASE_URL")


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/all")
async def all():
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM hazards;")
            data = cur.fetchall()

    return {"data": data}


@app.get("/hazards/recent")
async def get_recent_hazards(time: int = 2):
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM hazards WHERE CURRENT_TIMESTAMP - make_interval(hours => %s) < reported_at;", (time, ))
            data = cur.fetchall()
            
    return {"data": data}


@app.get("/hazards/{hazard_id}")
async def get_hazard(hazard_id: int):
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM hazards WHERE hazard_id=%s;", (hazard_id, ))
            data = cur.fetchone()
    
    return {"data": data}