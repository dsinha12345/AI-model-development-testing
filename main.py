from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Matri Matcher Running"}

from database import conn, cursor
from astrology import get_lat_lon

@app.post("/add-user")
def add_user(name: str, dob: str, tob: str, place: str):
    lat, lon = get_lat_lon(place)

    cursor.execute(
        "INSERT INTO users (name, dob, tob, place, lat, lon) VALUES (?, ?, ?, ?, ?, ?)",
        (name, dob, tob, place, lat, lon)
    )
    conn.commit()

    return {"status": "user added"}    

from matcher import match_users

@app.get("/matches")
def get_matches():
    return match_users()    