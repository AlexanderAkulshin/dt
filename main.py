from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import json
import psycopg2
import requests
import time

pload = {
    "client_id": "9d9416a4-8be0-4c19-b517-075e6c3cb67d",
    "client_secret": "3bc657e0-1e35-4045-9cc1-ed8faa003e64",
    "grant_type": "client_credentials",
}

tokenRequest = requests.post("https://frost.met.no/auth/accessToken", data=pload)
auth = tokenRequest.json()
token = auth["access_token"]

db = "test-db"
user = "postgres"
password = "mysecretpassword"
host = "0.0.0.0"

conn = psycopg2.connect(
    dbname=db,
    user=user,
    password=password,
    host=host,
    application_name="python-server-app",
)

app = FastAPI()


def stationToStr(station):
    id = station["id"]
    name = station["name"]
    validFrom = station["validFrom"]
    return f"('{id}', '{name}', '{validFrom}')"


@app.on_event("shutdown")
async def shutdown_event():
    print("close connection")
    await conn.close()


@app.get("/updateData")
def get_stations():
    cursor = conn.cursor()
    stationsRequest = requests.get(
        "https://frost.met.no/sources/v0.jsonld",
        params={
            "types": "SensorSystem",
            "elements": "wind_from_direction",
            "country": "Norge",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    stationsResponseJson = stationsRequest.json()
    stations = stationsResponseJson["data"]

    cursor = conn.cursor()
    cursor.execute(
        f"""
        INSERT INTO stations (id, name, validFrom) VALUES {
            ', '.join(list(map(stationToStr, stations)))
        }
    """
    )
    conn.commit()
    cursor.close()
    return None


@app.get("/")
def put_item():
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM stations
        ORDER BY validFrom
        LIMIT 10 
    """
    )
    result = cursor.fetchall()
    print(len(result))
    cursor.close()
    return result