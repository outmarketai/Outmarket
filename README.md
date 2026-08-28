# Gym Outreach Console — Run Guide

Ye ek poori app hai: Python backend (FastAPI) + professional dashboard frontend,
dono seedha Supabase se live data lete hain. Sirf ek command se dono chal jate hain.

## Kya Milega Dashboard Mein

- **KPI cards:** Total Leads, Reply Rate, Bookings, Booking Rate, Avg Reply Time
- **Line chart:** Leads aur Bookings time ke sath (trend)
- **Top 5 Leaderboard:** Leads / Bookings / Reply Rate ke hisaab se, dropdown se switch karo
- **Gym selector:** "All Gyms" ya koi specific gym select karo
- **Date filter:** 7 din / 30 din / 90 din / All time
- Specific gym select karne pe neeche **poora detail table** aa jata hai (sab leads +
  bookings, filter ke sath)

---

## Step 1 — Folder Setup

Is `dashboard-app` folder ko apne computer pe rakho. Ismein already ye hai:
```
dashboard-app/
  main.py
  requirements.txt
  .env.example
  static/
    index.html
```

## Step 2 — Python Environment Banao

Terminal mein `dashboard-app` folder ke andar jao:

```bash
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## Step 3 — .env File Banao

1. `.env.example` ko copy karke naam do `.env`
2. `SUPABASE_SERVICE_KEY` mein apni **service_role** key daalo
   (Supabase Dashboard → Project Settings → API → Legacy anon, service_role keys)
3. `SUPABASE_URL` already fill hai — agar project change ho jaye to update kar lena

## Step 4 — App Chalao

```bash
uvicorn main:app --reload --port 8000
```

Terminal mein "Application startup complete" dikhega.

## Step 5 — Dashboard Dekho

Browser mein kholo:

```
http://localhost:8000
```

Bas! Poora dashboard yahan live data ke sath khul jayega — koi alag frontend server
chalane ki zaroorat nahi, FastAPI khud dashboard bhi serve kar raha hai.

---

## Baad Mein Online Deploy Karna Ho To

- Render.com / Railway.app pe ye poora folder deploy ho sakta hai (dono backend +
  frontend saath, kyunki FastAPI hi dono serve kar raha hai)
- Sirf Environment Variables mein `.env` wali values daalni hongi wahan ke settings mein
- Jab ready ho, bata dena — deploy steps bhi guide kar dunga
