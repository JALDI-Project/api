from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
import psycopg


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
database_url = os.getenv("DATABASE_URL")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/all")
async def all():
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM hazards;")
            data = cur.fetchall()

    result = []
    for i in range(len(data)):
        result.append({"hazard_id": data[i][0],
                     "user_id": data[i][1],
                     "title": data[i][2],
                     "description": data[i][3],
                     "latitude": data[i][4],
                     "longitude": data[i][5],
                     "time": data[i][6]})
    
    return {"data": result}


@app.get("/hazards/recent")
async def get_recent_hazards(time: int = 2):
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM hazards WHERE CURRENT_TIMESTAMP - make_interval(hours => %s) < reported_at;", (time, ))
            data = cur.fetchall()

    result = []
    for i in range(len(data)):
        result.append({"hazard_id": data[i][0],
                     "user_id": data[i][1],
                     "title": data[i][2],
                     "description": data[i][3],
                     "latitude": data[i][4],
                     "longitude": data[i][5],
                     "time": data[i][6]})
    
    return {"data": result}


@app.get("/hazards/{hazard_id}")
async def get_hazard(hazard_id: int):
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM hazards WHERE hazard_id=%s;", (hazard_id, ))
            data = cur.fetchone()
    
    if data == []:
        return {"data": []}
    
    result = {
        "hazard_id": data[0],
        "user_id": data[1],
        "title": data[2],
        "description": data[3],
        "latitude": data[4],
        "longitude": data[5],
        "time": data[6]
    }

    return {"data": result}
