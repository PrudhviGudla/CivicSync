from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, HTTPException, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from passlib.context import CryptContext
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY", "") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
MONGO_URI = os.environ.get("MONGO_URI", "")
CLOUDINARY_UPLOAD_URL = os.environ.get("CLOUDINARY_UPLOAD_URL", "")
CLOUDINARY_UPLOAD_PRESET = os.environ.get("CLOUDINARY_UPLOAD_PRESET", "")  

# Initialize FastAPI app and MongoDB client
app = FastAPI()
client = MongoClient(MONGO_URI)
db = client.civicsync
users = db.users
issues = db.issues

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def hash_password(password): return pwd_context.hash(password)
def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token: return None
    payload = decode_token(token)
    if not payload: return None
    user = users.find_one({"_id": ObjectId(payload["user_id"])})
    if not user: return None
    user["id"] = str(user["_id"])
    return user

def require_user(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def geocode_location(location_text):
    # Use OpenCage or Nominatim for free geocoding
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": location_text, "format": "json", "limit": 1},
            headers={"User-Agent": "CivicSync/1.0"}
        )
        data = resp.json()
        if data:
            return [float(data[0]["lat"]), float(data[0]["lon"])]
    except Exception:
        pass
    return None

# Home / Feed
@app.get("/", response_class=HTMLResponse)
def home(request: Request, q: str = "", category: str = "", status_: str = "", sort: str = "newest", page: int = 1):
    query = {}
    if q: query["title"] = {"$regex": q, "$options": "i"}
    if category: query["category"] = category
    if status_: query["status"] = status_
    sort_by = [("created_at", DESCENDING)] if sort == "newest" else [("votes", DESCENDING)]
    per_page = 5
    total = issues.count_documents(query)
    cursor = issues.find(query).sort(sort_by).skip((page-1)*per_page).limit(per_page)
    issues_list = list(cursor)
    for i in issues_list:
        i["id"] = str(i["_id"])
        i["mine"] = False
    user = get_current_user(request)
    if user:
        for i in issues_list:
            if i["user_id"] == user["id"]:
                i["mine"] = True
    return templates.TemplateResponse("feed.html", {
        "request": request, "issues": issues_list, "user": user,
        "q": q, "category": category, "status_": status_, "sort": sort,
        "page": page, "total": total, "per_page": per_page
    })

# Register
@app.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_post(request: Request, email: str = Form(...), password: str = Form(...)):
    if users.find_one({"email": email}):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email already exists"})
    hashed = hash_password(password)
    user_id = users.insert_one({"email": email, "hashed_password": hashed}).inserted_id
    token = create_access_token({"user_id": str(user_id)})
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie("access_token", token, httponly=True)
    return resp

# Login
@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    user = users.find_one({"email": email})
    if not user or not verify_password(password, user["hashed_password"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    token = create_access_token({"user_id": str(user["_id"])})
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie("access_token", token, httponly=True)
    return resp

# Logout
@app.get("/logout")
def logout():
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("access_token")
    return resp

# Report Issue
@app.get("/report", response_class=HTMLResponse)
def report_get(request: Request):
    user = require_user(request)
    return templates.TemplateResponse("report.html", {"request": request, "user": user})

@app.post("/report")
async def report_post(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(None)
):
    user = require_user(request)
    image_url = None
    if image and image.filename:
        image.file.seek(0) 
        r = requests.post(
            CLOUDINARY_UPLOAD_URL,
            files={"file": (image.filename, image.file, image.content_type)},
            data={"upload_preset": CLOUDINARY_UPLOAD_PRESET}
        )
        resp_json = r.json()
        if r.status_code == 200 and 'secure_url' in resp_json:
            image_url = resp_json['secure_url']
        else:
            print('Cloudinary upload failed:', resp_json)
            image_url = None
    coords = geocode_location(location)
    issue = {
        "title": title,
        "description": description,
        "category": category,
        "location": location,
        "coordinates": coords,
        "image_url": image_url,
        "status": "Pending",
        "created_at": datetime.utcnow(),
        "user_id": user["id"],
        "votes": 0,
        "voters": []
    }
    issues.insert_one(issue)
    return RedirectResponse("/", status_code=302)

# My Issues
@app.get("/my-issues", response_class=HTMLResponse)
def my_issues(request: Request):
    user = require_user(request)
    my_issues = list(issues.find({"user_id": user["id"]}))
    for i in my_issues:
        i["id"] = str(i["_id"])
    return templates.TemplateResponse("my_issues.html", {"request": request, "issues": my_issues, "user": user})

# Edit Issue
@app.get("/edit/{issue_id}", response_class=HTMLResponse)
def edit_get(request: Request, issue_id: str):
    user = require_user(request)
    issue = issues.find_one({"_id": ObjectId(issue_id)})
    if not issue or issue["user_id"] != user["id"] or issue["status"] != "Pending":
        return RedirectResponse("/my-issues", status_code=302)
    issue["id"] = str(issue["_id"])
    return templates.TemplateResponse("edit_issue.html", {"request": request, "issue": issue, "user": user})

@app.post("/edit/{issue_id}")
async def edit_post(
    request: Request,
    issue_id: str,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(None)
):
    user = require_user(request)
    issue = issues.find_one({"_id": ObjectId(issue_id)})
    if not issue or issue["user_id"] != user["id"] or issue["status"] != "Pending":
        return RedirectResponse("/my-issues", status_code=302)
    image_url = issue.get("image_url")
    if image and image.filename:
        image.file.seek(0)  # Ensure pointer is at start
        r = requests.post(
            CLOUDINARY_UPLOAD_URL,
            files={"file": (image.filename, image.file, image.content_type)},
            data={"upload_preset": CLOUDINARY_UPLOAD_PRESET}
        )
        resp_json = r.json()
        if r.status_code == 200 and 'secure_url' in resp_json:
            image_url = resp_json['secure_url']
        else:
            print('Cloudinary upload failed:', resp_json)
            image_url = None
    coords = geocode_location(location)
    issues.update_one(
        {"_id": ObjectId(issue_id)},
        {"$set": {
            "title": title,
            "description": description,
            "category": category,
            "location": location,
            "coordinates": coords,
            "image_url": image_url
        }}
    )
    return RedirectResponse("/my-issues", status_code=302)

# Delete Issue
@app.get("/delete/{issue_id}")
def delete_issue(request: Request, issue_id: str):
    user = require_user(request)
    issue = issues.find_one({"_id": ObjectId(issue_id)})
    if not issue or issue["user_id"] != user["id"] or issue["status"] != "Pending":
        return RedirectResponse("/my-issues", status_code=302)
    issues.delete_one({"_id": ObjectId(issue_id)})
    return RedirectResponse("/my-issues", status_code=302)

# Issue Detail
@app.get("/issue/{issue_id}", response_class=HTMLResponse)
def issue_detail(request: Request, issue_id: str):
    issue = issues.find_one({"_id": ObjectId(issue_id)})
    if not issue:
        return RedirectResponse("/", status_code=302)
    issue["id"] = str(issue["_id"])
    user = get_current_user(request)
    voted = False
    if user and user["id"] in issue.get("voters", []):
        voted = True
    mine = user and user["id"] == issue["user_id"]
    return templates.TemplateResponse("issue_detail.html", {
        "request": request, "issue": issue, "user": user, "voted": voted, "mine": mine
    })

# Vote
@app.post("/vote/{issue_id}")
def vote_issue(request: Request, issue_id: str):
    user = require_user(request)
    issue = issues.find_one({"_id": ObjectId(issue_id)})
    if not issue or user["id"] in issue.get("voters", []):
        return RedirectResponse(f"/issue/{issue_id}", status_code=302)
    issues.update_one(
        {"_id": ObjectId(issue_id)},
        {"$inc": {"votes": 1}, "$push": {"voters": user["id"]}}
    )
    return RedirectResponse(f"/issue/{issue_id}", status_code=302)

# Status Update (simulate resolution flow)
@app.get("/status/{issue_id}/{new_status}")
def update_status(request: Request, issue_id: str, new_status: str):
    user = require_user(request)
    issue = issues.find_one({"_id": ObjectId(issue_id)})
    if not issue or issue["user_id"] != user["id"]:
        return RedirectResponse("/my-issues", status_code=302)
    if new_status not in ["Pending", "In Progress", "Resolved"]:
        return RedirectResponse("/my-issues", status_code=302)
    issues.update_one({"_id": ObjectId(issue_id)}, {"$set": {"status": new_status}})
    return RedirectResponse("/my-issues", status_code=302)

# Analytics Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = require_user(request)
    # Category count
    pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}]
    cat_counts = list(issues.aggregate(pipeline))
    # Daily submissions (last 7 days)
    now = datetime.utcnow()
    days = [(now - timedelta(days=i)).date() for i in range(6, -1, -1)]
    daily = []
    for d in days:
        start = datetime.combine(d, datetime.min.time())
        end = datetime.combine(d, datetime.max.time())
        count = issues.count_documents({"created_at": {"$gte": start, "$lte": end}})
        daily.append({"date": d.strftime("%Y-%m-%d"), "count": count})
    # Most voted by category
    pipeline = [
        {"$group": {"_id": "$category", "max_votes": {"$max": "$votes"}}},
        {"$sort": {"max_votes": -1}}
    ]
    most_voted = list(issues.aggregate(pipeline))
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "user": user,
        "cat_counts": cat_counts, "daily": daily, "most_voted": most_voted
    })

# Map View
@app.get("/map", response_class=HTMLResponse)
def map_view(request: Request):
    user = get_current_user(request)
    all_issues = list(issues.find({"coordinates": {"$ne": None}}))
    serializable_issues = []
    for i in all_issues:
        issue = dict(i)
        issue["id"] = str(issue["_id"])
        del issue["_id"]
        # Convert datetime fields to string if present
        if "created_at" in issue and isinstance(issue["created_at"], datetime):
            issue["created_at"] = issue["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        serializable_issues.append(issue)
    return templates.TemplateResponse("map.html", {"request": request, "user": user, "issues": serializable_issues})

@app.get("/api/issues")
def api_issues():
    all_issues = list(issues.find({"coordinates": {"$ne": None}}))
    serializable_issues = []
    for i in all_issues:
        issue = dict(i)
        issue["id"] = str(issue["_id"])
        del issue["_id"]
        if "created_at" in issue and isinstance(issue["created_at"], datetime):
            issue["created_at"] = issue["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        serializable_issues.append({
            "id": issue["id"],
            "title": issue["title"],
            "status": issue["status"],
            "votes": issue["votes"],
            "coordinates": issue["coordinates"]
        })
    return {"issues": serializable_issues}
