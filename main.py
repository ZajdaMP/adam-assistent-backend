from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import os
from urllib.parse import urlencode

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/oauth2callback")
TOKEN_FILE = "google_tokens.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/contacts.readonly"
]

@app.get("/")
def root():
    return {"message": "Adam Assistant Backend is running"}

@app.get("/auth")
def authorize():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent"
    }
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")

@app.get("/oauth2callback")
def oauth2callback(code: str):
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post("https://oauth2.googleapis.com/token", data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Token exchange failed")

    tokens = response.json()
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)

    return {"message": "Authorization successful"}

@app.get("/emails")
def get_emails():
    if not os.path.exists(TOKEN_FILE):
        raise HTTPException(status_code=401, detail="Not authorized")

    with open(TOKEN_FILE) as f:
        tokens = json.load(f)

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    r = requests.get("https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=5", headers=headers)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail="Failed to get emails")

    return r.json()

# Vynucené přepsání main.py - oprava /auth endpointu
Oprava: odstranění neplatného znaku – místo pomlčky


