# AcquiSight AI

> **AI-Powered Deal Screening & Investment Intelligence**

![AcquiSight AI Banner](docs/screenshots/banner.png)

AcquiSight AI is a production-grade private equity deal screening platform that helps analysts rapidly evaluate acquisition targets, generate investment attractiveness scores, assess risks, benchmark comparable companies, and produce professional investment memos — all powered by OpenAI.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Deal Screener** | Enter company financials and get instant scoring across 6 dimensions |
| 🧮 **Valuation Engine** | EV, EBITDA multiples, DCF range — computed automatically |
| ⚡ **Risk Analyser** | Leverage, liquidity, growth, and market risk scores |
| 🏢 **Comparable Companies** | Industry-specific comps with EV/EBITDA benchmarking |
| 🤖 **AI Memo Generator** | GPT-4o-powered investment memo in PE analyst style |
| 📄 **PDF Export** | One-click professional memo export |
| 🌙 **Dark Dashboard** | Bloomberg/PitchBook-inspired dark analytics UI |

---

## 🖥️ Tech Stack

**Frontend**
- React 18 + TypeScript
- Tailwind CSS v3
- Recharts
- React-PDF / html2canvas for export

**Backend**
- Python 3.11
- FastAPI
- Pydantic v2
- OpenAI Python SDK

**Database**
- PostgreSQL 15

**Infrastructure**
- Docker + Docker Compose
- Environment variable management via `.env`

---

## 📁 Folder Structure

```
acquisight-ai/
├── frontend/                   # React + TypeScript SPA
│   ├── src/
│   │   ├── components/         # Dashboard, ScoreGauge, CompsTable, MemoViewer …
│   │   ├── pages/              # DealScreener, Portfolio, Settings
│   │   ├── hooks/              # useScreenDeal, useMemo
│   │   ├── types/              # TypeScript interfaces
│   │   └── utils/              # formatCurrency, formatPercent
│   ├── public/
│   ├── package.json
│   └── tailwind.config.ts
├── backend/
│   ├── main.py                 # FastAPI app entrypoint
│   ├── scoring.py              # Investment scoring engine
│   ├── valuation.py            # EV & multiple calculations
│   ├── risk.py                 # Risk scoring module
│   ├── comps.py                # Comparable company analysis
│   ├── memo_generator.py       # OpenAI memo generation
│   ├── models.py               # Pydantic request/response models
│   ├── database.py             # PostgreSQL connection & ORM
│   └── routers/
│       ├── screen.py           # POST /api/screen
│       ├── memo.py             # POST /api/memo
│       └── history.py          # GET /api/history
├── docs/
│   ├── screenshots/
│   └── sample_memo.md
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── LICENSE
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### 1. Clone the repo
```bash
git clone https://github.com/Aayushij2810/acquisight-ai.git
cd acquisight-ai
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env — add your OPENAI_API_KEY and DB credentials
```

### 3. Run with Docker
```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

### 4. Manual local setup (no Docker)

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r ../requirements.txt
uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

---

## 🔌 API Reference

### `POST /api/screen`
Screens a company and returns investment scores.

**Request body:**
```json
{
  "company_name": "Acme Corp",
  "industry": "SaaS",
  "revenue": 50000000,
  "ebitda": 12000000,
  "growth_rate": 28,
  "debt": 15000000,
  "cash": 8000000,
  "country": "United States"
}
```

**Response:**
```json
{
  "ebitda_margin": 24.0,
  "debt_to_ebitda": 1.25,
  "enterprise_value": 132000000,
  "investment_score": 84,
  "risk_score": 31,
  "recommendation": "Strong Buyout Candidate",
  "scores": { "growth": 88, "profitability": 79, "leverage": 85, "revenue_quality": 82, "financial_health": 81 },
  "comps": [ ... ]
}
```

### `POST /api/memo`
Generates an AI-powered investment memo via GPT-4o.

### `GET /api/history`
Returns previously screened deals from PostgreSQL.

---

## 📊 Scoring Methodology

| Score | Weight | Formula |
|---|---|---|
| Growth Score | 25% | Sigmoid curve on revenue growth rate vs industry median |
| Profitability Score | 25% | EBITDA margin benchmarked against sector quartiles |
| Leverage Score | 20% | Debt/EBITDA inverted scale (0× = 100, 6×+ = 0) |
| Revenue Quality Score | 15% | Recurring vs non-recurring revenue proxy |
| Financial Health Score | 15% | Net debt / cash position ratio |
| **Investment Attractiveness Score** | **100%** | Weighted composite of all five dimensions |

**Recommendation thresholds:**

| Score | Recommendation |
|---|---|
| 80–100 | 🟢 Strong Buyout Candidate |
| 65–79 | 🔵 Attractive Growth Investment |
| 50–64 | 🟡 Requires Further Due Diligence |
| 35–49 | 🟠 High Risk Opportunity |
| 0–34 | 🔴 Reject |

---

## 🔮 Future Improvements

- [ ] Live data integration (Refinitiv / Bloomberg API)
- [ ] Portfolio tracker with IRR and MOIC calculations
- [ ] LBO model builder
- [ ] ESG scoring module
- [ ] Multi-user authentication with deal team collaboration
- [ ] CRM integration (Salesforce / HubSpot)
- [ ] Natural language deal search ("Find SaaS companies with >30% growth and <3x leverage")

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

## 👤 Author

**Aayushi Jain** — [github.com/Aayushij2810](https://github.com/Aayushij2810)

*MSISS @ Trinity College Dublin · Business Analytics · Product Strategy · AI*
