# ⬡ CognitiveMesh — Multi-Agent AI Debate System

> Built by **Sai Rushitha Bhimavarapu** · [github.com/sairushitha](https://github.com/sairushitha)

4 AI agents (Scientist, Critic, Ethicist, Optimizer) debate any topic in real time using the free Groq API (Llama 3.3 70B), then reach a consensus. Every debate is saved to a database. Responses stream live, word by word.

**Stack:** FastAPI (Python) · Groq API (free Llama 3.3 70B) · SQLite (local) / PostgreSQL (production) · Server-Sent Events · Vanilla JS frontend

---

# 🖥️ RUN IT ON YOUR COMPUTER — Step by Step

Follow these exactly. Total time: ~10 minutes.

## ✅ Before you start — install these

1. **Python 3.10 or newer** — check by running:
   ```bash
   python --version
   ```
   If you don't have it: download from [python.org/downloads](https://www.python.org/downloads/)

2. **A Groq API key** — completely FREE, no credit card needed:
   - Go to [console.groq.com/keys](https://console.groq.com/keys)
   - Sign up (Google/GitHub login works) → Create API Key → copy it (starts with `gsk_`)
   - Free tier: ~30 requests/min, ~14,400 requests/day — plenty for a portfolio

---

## 📁 STEP 1 — Get the files onto your computer

Unzip the project. You should see this structure:
```
cognitivemesh/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── db/
│   ├── models/
│   ├── routers/
│   └── services/
└── frontend/
    └── index.html
```

Open a terminal and navigate into the project:
```bash
cd path/to/cognitivemesh
```

---

## 🐍 STEP 2 — Set up the backend

### 2a. Go into the backend folder
```bash
cd backend
```

### 2b. Create a virtual environment (keeps dependencies isolated)

**On Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You'll know it worked when you see `(venv)` at the start of your terminal line.

### 2c. Install the dependencies
```bash
pip install -r requirements.txt
```
This installs FastAPI, the Groq SDK, the database libraries, etc. Takes ~1 minute.

### 2d. Add your API key

Copy the example env file:

**Mac/Linux:**
```bash
cp .env.example .env
```
**Windows:**
```bash
copy .env.example .env
```

Now open the new `.env` file in any text editor and paste your key:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
```
Leave `DATABASE_URL` commented out — it will automatically use a local SQLite file. No database install needed.

### 2e. Start the backend server
```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

✅ **Backend is now running!** Leave this terminal open.

Test it: open [http://localhost:8000/health](http://localhost:8000/health) in your browser — you should see `{"status":"healthy"}`.

You can also see the auto-generated API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🌐 STEP 3 — Open the frontend

The frontend is a single HTML file. You have two easy options:

### Option A — Just open the file (simplest)
Double-click `frontend/index.html` — it opens in your browser. Done.

### Option B — Serve it properly (recommended, avoids browser quirks)
Open a **second terminal**, then:
```bash
cd path/to/cognitivemesh/frontend
python -m http.server 3000
```
Now open [http://localhost:3000](http://localhost:3000)

---

## 🎉 STEP 4 — Run a debate!

1. At the top of the page, the status should say **"Backend connected"** (green dot).
   - If it says offline, click **Test** — make sure the URL is `http://localhost:8000`
2. Type a debate topic (or click a preset like "AGI legal rights")
3. Click **Start Live AI Debate**
4. Watch all 4 agents respond in real time, streaming word by word
5. Check the **History** tab to see saved debates

---

# 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `Backend offline` in UI | Make sure `uvicorn` is still running in terminal 1 |
| `GROQ_API_KEY is not set` | Check your `.env` file has the key, restart uvicorn |
| `command not found: uvicorn` | Activate the venv first (`source venv/bin/activate`) |
| `pip not found` | Use `pip3` instead of `pip` |
| Browser shows CORS error | Use Option B (serve frontend on port 3000) instead of opening the file directly |
| Debate starts but no text | Check terminal 1 for errors — usually an invalid/expired API key |
| `port 8000 already in use` | Use a different port: `uvicorn main:app --reload --port 8001` and update the URL in the frontend |

---

# 🚀 Deploy to the Internet (optional)

### Backend → Railway
1. Push this repo to GitHub
2. [railway.app](https://railway.app) → New Project → Deploy from GitHub → pick repo, set root directory to `backend`
3. Add the **PostgreSQL** plugin (one click)
4. In Variables, add `GROQ_API_KEY` (Railway auto-adds `DATABASE_URL`)
5. Railway gives you a URL like `https://cognitivemesh-production.up.railway.app`

### Frontend → Vercel
1. [vercel.com](https://vercel.com) → New Project → import repo → set root directory to `frontend`
2. Deploy → you get `https://cognitivemesh.vercel.app`
3. Open it → paste your Railway URL in the config bar → Save

---

# 💰 Cost
- Local: **100% free** (Groq free tier covers it)
- Railway: ~$5/month · Vercel: free · Groq: free tier

---
Made with 🧠 by Sai Rushitha Bhimavarapu
