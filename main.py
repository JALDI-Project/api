from dotenv import load_dotenv
from fastapi import FastAPI
import os
import psycopg

app = FastAPI()
load_dotenv()
database_url = os.getenv("DATABASE_URL")


@app.get("/all")
async def root():
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM hazards;")
            data = cur.fetchall()

    return {"data": data}
