# Commented by: Akshat Trivedi 
# TimeStamp: 20/09/2025 
# Purpose: Creation of Python API for TMS Integration with Github

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_credentials=True,
    allow_methods=["*"],         
    allow_headers=["*"],         
)

# Request body schema
class Ticket(BaseModel):
    title: str
    description: str
    labels: list[str] = []
    assignees: list[str] = []

@app.get("/")
def home():
    return "Hello"

@app.post("/create-issue")
def create_issue(ticket: Ticket):
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/issues"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    try:

        # 1. Search existing issues

        search_url = f"{url}?state=all&per_page=100"            #endpoint to fetch all the issues (open & closed) first 100 issues
        response = requests.get(search_url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())

        issues = response.json()

        # 2. Check if ticket_id already exists in title
        existing_issue = next((issue for issue in issues if ticket.title in issue["title"]), None)

        if existing_issue:
            # 3. Update existing issue (PATCH)
            issue_number = existing_issue["number"]
            update_url = f"{url}/{issue_number}"
            payload = {
                "title": ticket.title,
                "body": ticket.description,
                "labels": ticket.labels,
                "assignees": ticket.assignees,
                "state": "closed"  # for closing the issue
            }

            update_resp = requests.patch(update_url, headers=headers, json=payload)
            if update_resp.status_code == 200:
                return {"message": "Issue updated & closed", "issue": update_resp.json()}
            else:
                raise HTTPException(status_code=update_resp.status_code, detail=update_resp.json())

        else:
            # 4. Create new issue
            payload = {
                "title": ticket.title,
                "body": ticket.description,
                "labels": ticket.labels,
                "assignees": ticket.assignees,
            }
            create_resp = requests.post(url, headers=headers, json=payload)
            if create_resp.status_code == 201:
                return {"message": "Issue created", "issue": create_resp.json()}
            else:
                raise HTTPException(status_code=create_resp.status_code, detail=create_resp.json())

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="GitHub API request timed out")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="Failed to connect to GitHub API")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
