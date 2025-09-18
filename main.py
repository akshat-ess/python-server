from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")

app = FastAPI()

# Request body schema
class Ticket(BaseModel):
    title: str
    description: str
    labels: list[str] = []
    assignees: list[str] = []
    ticket_id: str

@app.get("/")
def home():
    return "Hello"

@app.post("/create-issue")
def create_issue(ticket: Ticket):
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/issues"

    tms_url = f"https://192.168.5.233:8443/ords/wstms/details/tms-ticket?nu_ticket_id={ticket.ticket_id}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    payload = {
        "title": ticket.title,
        "body": ticket.description,
        "labels": ticket.labels,
        "assignees": ticket.assignees,
        "ticket id": ticket.ticket_id
    }

    response = requests.post(url, headers=headers, json=payload)

    print("request sent")

    if response.status_code == 201:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())
