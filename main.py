from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
import psycopg
from pydantic import BaseModel

# Model for a hazard report submitted to the API
class Report(BaseModel):
    reporter: str
    title: str
    description: str
    latitude: float
    longitude: float

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
                     "title": data[i][1],
                     "description": data[i][2],
                     "latitude": data[i][3],
                     "longitude": data[i][4],
                     "time": data[i][5]})
    
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
                     "title": data[i][1],
                     "description": data[i][2],
                     "latitude": data[i][3],
                     "longitude": data[i][4],
                     "time": data[i][5]})
    
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
        "title": data[1],
        "description": data[2],
        "latitude": data[3],
        "longitude": data[4],
        "time": data[5]
    }

    return {"data": result}

@app.post("/submit")
async def create_hazard(item: Report):
    item_dict = item.model_dump()
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO HAZARDS (title, description, latitude, longitude) VALUES (%s, %s, %s, %s);",
                (item.title, item.description, item.latitude, item.longitude)
            )

            conn.commit();

    return 201;
