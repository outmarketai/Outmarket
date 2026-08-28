"""
Gym Outreach Dashboard — Backend
"""
#D:\dashboard-app\main.py
import os
import time
from datetime import datetime
from collections import defaultdict

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Gym Outreach Dashboard API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def is_test_row(gym_name, lead_name):
    g = (gym_name or "").strip().lower()
    l = (lead_name or "").strip().lower()
    if g in ("test test", "test"): return True
    if l in ("test", "test test"): return True
    if l.startswith("<test"): return True
    return False


def parse_ts(value):
    if not value: return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def safe_execute(query, retries=3):
    """Runs a Supabase query with retries — the connection to Supabase can
    occasionally drop mid-request, this retries a couple of times before failing."""
    last_error = None
    for attempt in range(retries):
        try:
            return query.execute().data
        except Exception as e:
            last_error = e
            time.sleep(0.6 * (attempt + 1))
    raise last_error


def fetch_replies(gym=None, start=None, end=None):
    q = supabase.table("replies").select("*")
    if gym and gym != "all": q = q.eq("gym_name", gym)
    if start: q = q.gte("initial_sent_date", start)
    if end: q = q.lte("initial_sent_date", end)
    rows = safe_execute(q)
    return [r for r in rows if not is_test_row(r.get("gym_name"), r.get("lead_name"))]


def fetch_bookings(gym=None, start=None, end=None):
    q = supabase.table("bookings").select("*")
    if gym and gym != "all": q = q.eq("gym_name", gym)
    if start: q = q.gte("booking_date", start)
    if end: q = q.lte("booking_date", end)
    rows = safe_execute(q)
    return [r for r in rows if not is_test_row(r.get("gym_name"), r.get("lead_name"))]


@app.get("/api/gyms")
def list_gyms():
    replies = fetch_replies()
    bookings = fetch_bookings()
    names = sorted({r["gym_name"] for r in replies} | {b["gym_name"] for b in bookings})
    return names


@app.get("/api/kpis")
def kpis(gym: str = Query("all"), start: str = None, end: str = None):
    replies = fetch_replies(gym, start, end)
    bookings = fetch_bookings(gym, start, end)

    total_leads = len(replies)
    total_replied = sum(1 for r in replies if r.get("replied"))
    reply_rate = round(total_replied / total_leads * 100, 1) if total_leads else 0
    total_bookings = len(bookings)
    booking_rate = round(total_bookings / total_leads * 100, 1) if total_leads else 0

    reply_times = []
    for r in replies:
        if r.get("replied") and r.get("initial_sent_date") and r.get("reply_date"):
            a, b = parse_ts(r["initial_sent_date"]), parse_ts(r["reply_date"])
            if a and b:
                reply_times.append((b - a).total_seconds() / 3600)
    avg_reply_hours = round(sum(reply_times) / len(reply_times), 1) if reply_times else None

    return {
        "total_leads": total_leads, "total_replied": total_replied, "reply_rate": reply_rate,
        "total_bookings": total_bookings, "booking_rate": booking_rate, "avg_reply_hours": avg_reply_hours,
    }


@app.get("/api/leaderboard")
def leaderboard(metric: str = "leads", limit: int = 5, order: str = "desc",
                 min_leads: int = 0, start: str = None, end: str = None):
    replies = fetch_replies(None, start, end)
    bookings = fetch_bookings(None, start, end)

    gym_map = defaultdict(lambda: {"leads": 0, "replied": 0, "bookings": 0})
    for r in replies:
        g = gym_map[r["gym_name"]]
        g["leads"] += 1
        if r.get("replied"): g["replied"] += 1
    for b in bookings:
        gym_map[b["gym_name"]]["bookings"] += 1

    out = []
    for name, v in gym_map.items():
        if v["leads"] < min_leads:
            continue
        rate = round(v["replied"] / v["leads"] * 100, 1) if v["leads"] else 0
        out.append({"gym_name": name, "leads": v["leads"], "replied": v["replied"],
                     "reply_rate": rate, "bookings": v["bookings"]})

    key = {"leads": "leads", "bookings": "bookings", "reply_rate": "reply_rate"}.get(metric, "leads")
    out.sort(key=lambda x: x[key], reverse=(order == "desc"))
    return out[:limit]


@app.get("/api/gym-detail")
def gym_detail(gym: str, start: str = None, end: str = None):
    replies = fetch_replies(gym, start, end)
    bookings = fetch_bookings(gym, start, end)
    replies.sort(key=lambda r: r.get("initial_sent_date") or "", reverse=True)
    bookings.sort(key=lambda b: b.get("booking_date") or "", reverse=True)

    total_leads = len(replies)
    total_replied = sum(1 for r in replies if r.get("replied"))
    reply_rate = round(total_replied / total_leads * 100, 1) if total_leads else 0

    return {
        "summary": {"total_leads": total_leads, "total_replied": total_replied,
                     "reply_rate": reply_rate, "total_bookings": len(bookings)},
        "leads": replies, "bookings": bookings,
    }


@app.get("/api/timeseries")
def timeseries(gym: str = Query("all"), start: str = None, end: str = None):
    replies = fetch_replies(gym, start, end)
    bookings = fetch_bookings(gym, start, end)

    by_day = defaultdict(lambda: {"leads": 0, "bookings": 0})
    for r in replies:
        d = parse_ts(r.get("initial_sent_date"))
        if d: by_day[d.date().isoformat()]["leads"] += 1
    for b in bookings:
        d = parse_ts(b.get("booking_date"))
        if d: by_day[d.date().isoformat()]["bookings"] += 1

    days = sorted(by_day.keys())
    return [{"date": d, **by_day[d]} for d in days]


STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))