# Gym Outreach Console — Run Guide

A complete gym outreach analytics dashboard built with a Python FastAPI backend and a professional dashboard frontend. Both connect directly to Supabase to display live data, and the entire application can be run with a single command.

## Dashboard Features

- **KPI Cards:** Total Leads, Reply Rate, Bookings, Booking Rate, and Average Reply Time
- **Line Chart:** Leads and Bookings over time
- **Top 5 Leaderboard:** Switch between Leads, Bookings, and Reply Rate using the dropdown
- **Gym Selector:** View data for All Gyms or select a specific gym
- **Date Filters:** 7 Days, 30 Days, 90 Days, or All Time
- **Gym Details:** Selecting a specific gym displays a complete detail table containing leads and bookings according to the selected date filter

---

## Step 1 — Folder Setup

Place the `dashboard-app` folder on your computer. It already contains:

```text
dashboard-app/
├── main.py
├── requirements.txt
├── .env.example
└── static/
    └── index.html