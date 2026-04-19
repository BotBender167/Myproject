# Delivery Predictor v2

> Production-ready monorepo for AI-powered delivery risk prediction.
>
> **Stack**: FastAPI · SQLModel · SQLite · React · Vite · TypeScript · Tailwind CSS · Shadcn/UI

```
Myproject/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt
│   └── app/
│       ├── models.py            # SQLModel schemas (DB + API)
│       ├── core/db.py           # Engine, session, DB init
│       ├── api/endpoints.py     # APIRouter: /health /predict /stops
│       └── services/ml.py       # Risk score calculation
└── frontend/
    ├── index.html
    ├── vite.config.ts
    └── src/
        ├── types/index.ts       # Shared TS interfaces
        ├── components/
        │   ├── Dashboard.tsx    # Main layout + side-nav
        │   └── ui/              # Button, Card, Badge, Table
        └── lib/utils.ts         # cn() utility
```

---

## Backend Setup

**Prerequisites**: Python 3.10+

```bash
# 1. Navigate to backend
cd backend

# 2. Create and activate virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the development server
uvicorn main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Liveness probe |
| `/api/predict` | POST | Delivery risk prediction |
| `/api/stops` | GET | All delivery stops |

### Example: Risk Prediction

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"weather_score": 0.8, "traffic_score": 0.6, "history_score": 0.4}'
```

Response:
```json
{"risk_score": 0.66, "risk_label": "Medium"}
```

---

## Frontend Setup

**Prerequisites**: Node.js 18+

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start the Vite dev server
npm run dev
```

The app will be available at **http://localhost:5173**

> **Proxy**: The Vite dev server automatically proxies `/api/*` requests to
> `http://localhost:8000`, so you don't need to handle CORS manually in
> development.

### Build for Production

```bash
npm run build      # Outputs to frontend/dist/
npm run preview    # Preview the production build locally
```

---

## Notes

- The SQLite database file `delivery.db` is auto-created in the `/backend`
  directory on first startup and is excluded from version control.
- All frontend TypeScript interfaces in `src/types/index.ts` mirror the
  backend SQLModel schemas — keep them in sync when adding new fields.
- ML weights: Weather 40%, Traffic 35%, Historical 25%.
