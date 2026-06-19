# AcquiSight AI

> **AI-Powered Deal Screening & Investment Intelligence**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript)](https://typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

AcquiSight AI is a full-stack private equity deal screening platform that helps analysts rapidly evaluate acquisition targets, generate investment attractiveness scores, assess risks, benchmark comparable companies, and produce professional investment memos — all powered by OpenAI.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Deal Screening Engine** | Enter 8 financial inputs; get instant investment scoring |
| **Investment Attractiveness Score** | 0–100 composite with 5 dimension breakdown |
| **Risk Assessment** | Multi-factor risk scoring with severity-labelled risk factors |
| **Comparable Company Analysis** | Industry-benchmarked comps table with bear/base/bull EV range |
| **AI Investment Memo** | GPT-powered 7-section PE-style investment memorandum |
| **Score Visualisations** | Radar chart + horizontal bar breakdown via Recharts |
| **Export** | Download investment memo as Markdown |
| **Dark Dashboard UI** | Bloomberg/PitchBook-inspired dark theme |
| **Docker Ready** | One-command `docker compose up` deployment |

---

## 🛠 Tech Stack

**Frontend:** React 18 · TypeScript 5 · Tailwind CSS · Recharts · Lucide Icons  
**Backend:** Python 3.12 · FastAPI · Pydantic v2 · SQLAlchemy  
**Database:** PostgreSQL 16  
**AI:** OpenAI API (`gpt-4o-mini` default, configurable)  
**DevOps:** Docker · Docker Compose · Nginx  

---

## 📁 Project Structure

```
acquisight-ai/
├── backend/
│   ├── main.py            # FastAPI app & routes
│   ├── scoring.py         # Investment attractiveness scoring
│   ├── valuation.py       # Enterprise value & financial ratios
│   ├── risk.py            # Risk score calculation
│   ├── comps.py           # Comparable company benchmarking
│   ├── memo_generator.py  # OpenAI memo generation
│   ├── database.py        # SQLAlchemy models & session
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   ├── types.ts
│   │   ├── utils.ts
│   │   └── components/
│   │       ├── Logo.tsx
│   │       ├── ScreeningForm.tsx
│   │       ├── ScoreCard.tsx
│   │       ├── ScoreGauge.tsx
│   │       ├── FinancialMetrics.tsx
│   │       ├── CompsTable.tsx
│   │       ├── RiskPanel.tsx
│   │       ├── MemoPanel.tsx
│   │       └── ScoreChart.tsx
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Option A — Docker (Recommended)

```bash
git clone https://github.com/Aayushij2810/AcquiSight-AI.git
cd AcquiSight-AI
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
docker compose up --build
```

| Service  | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend  | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

### Option B — Local Development

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
cp ../.env.example .env   # add your OPENAI_API_KEY
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
cp .env.example .env.local
npm install
npm start
```

---

## 📊 Scoring Methodology

### Investment Attractiveness Score (0–100)

| Dimension | Weight | Driver |
|---|---|---|
| Growth Score | 25 % | YoY revenue growth vs. industry benchmarks |
| Profitability Score | 25 % | EBITDA margin vs. sector median |
| Leverage Score | 20 % | Debt/EBITDA penalty curve |
| Revenue Quality | 15 % | Absolute revenue scale |
| Financial Health | 15 % | Cash buffer & coverage ratios |

### Recommendations

| Score Band | Risk Band | Label |
|---|---|---|
| ≥ 75 | Low/Medium | **Strong Buyout Candidate** |
| ≥ 60 | Any | **Attractive Growth Investment** |
| ≥ 45 | Medium | **Requires Further Due Diligence** |
| ≥ 30 | High | **High Risk Opportunity** |
| < 30 | Any | **Reject** |

---

## 🔮 Future Improvements

- [ ] PDF export with charts embedded via Puppeteer / WeasyPrint
- [ ] Persistent deal pipeline with PostgreSQL (models ready in `database.py`)
- [ ] Live comparable data via Bloomberg / Refinitiv API integration
- [ ] DCF valuation module
- [ ] User authentication & deal sharing
- [ ] LBO model builder
- [ ] Sector-specific scoring weights
- [ ] Excel export of full financial model

---

## ⚠️ Disclaimer

AcquiSight AI is a portfolio / educational project. Scores and memos are **not** investment advice. Always conduct thorough due diligence before making investment decisions.

---

## 📄 License

MIT — see [LICENSE](./LICENSE)
