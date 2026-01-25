from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os, random, base64, requests

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_USER = os.getenv("GITHUB_USERNAME")
REPO = os.getenv("REPO")
BRANCH = "main"

otp_store = {}

# ---------- LOGIN ----------
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/")
def login(user: str = Form(...), password: str = Form(...)):
    if user == ADMIN_USER and password == ADMIN_PASS:
        otp = str(random.randint(100000, 999999))
        otp_store[user] = otp
        print("OTP:", otp)
        return RedirectResponse("/otp", status_code=302)
    return "Invalid Login"

# ---------- OTP ----------
@app.get("/otp", response_class=HTMLResponse)
def otp_page(request: Request):
    return templates.TemplateResponse("otp.html", {"request": request})

@app.post("/otp")
def verify_otp(otp: str = Form(...)):
    if otp in otp_store.values():
        return RedirectResponse("/upload", status_code=302)
    return "Wrong OTP"

# ---------- UPLOAD PAGE ----------
@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# ---------- UPLOAD HANDLER ----------
@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    content = base64.b64encode(file.file.read()).decode()

    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents/{file.filename}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    data = {
        "message": "upload from secure site",
        "content": content,
        "branch": BRANCH
    }

    r = requests.put(url, json=data, headers=headers)

    print("Status:", r.status_code)
    print("Response:", r.text)

    return "Uploaded Successfully 🎉" if r.status_code in [200,201] else "Upload Failed ❌"
