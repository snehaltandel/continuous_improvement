# AI4CI Gamified Escape Room

Reference implementation of the AI4CI gamified escape-room campaign described in the attached PRD.

## Stack

- Frontend: React + TypeScript + Vite
- Backend: Django REST Framework + SQLite

## What is implemented

- Config-driven campaign model with weeks, steps, criteria, submissions, scores, badges, and leaderboard
- Seeded Week 1-4 campaign configuration, with Week 1 matching the PRD's three-step flow
- Draft -> AI assist -> human review enforcement for final submissions
- Dashboard, challenge room UI, leaderboard, badge display, and week resume behavior
- Deterministic local AI/stub scoring services so the product works before an external LLM is wired in

## Backend

```bash
cd /Users/snehalbhaitandel/Projects/Continuous_Improvement
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
.venv/bin/python backend/manage.py migrate
.venv/bin/python backend/manage.py runserver 127.0.0.1:8000
```

Use the `X-User` header for MVP identity. The frontend defaults to `learner1`.

## Frontend

```bash
cd /Users/snehalbhaitandel/Projects/Continuous_Improvement/frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`, so the Django server must be running while the frontend is open.

If your backend is on a different host or port, create `frontend/.env.local` with:

```bash
VITE_API_BASE=http://your-host:your-port/api
```

## Notes

- `POST /api/ai/.../assist` currently uses a deterministic local refiner instead of an external LLM.
- Replace the demo identity flow with real authentication before production deployment.
- The Django admin can become the campaign configuration surface after migrations are created.
