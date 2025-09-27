from dotenv import load_dotenv
from fastapi import FastAPI
import os
import psycopg

app = FastAPI()
load_dotenv()
database_url = os.getenv("DATABASE_URL")


@app.get("/")
async def root():
    var = "Connection failed :("
    with psycopg.connect(database_url) as conn:
        var = "Connection succesful :)"

    return {"message": var}
