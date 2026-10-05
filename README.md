# FinAnalyst — AI-Powered Financial Analyst Assistant

A full-stack Flask web application that delivers real-time stock data, portfolio management, and AI-generated investment insights powered by Google Gemini. Combines live market data with natural language generation to make financial analysis accessible and conversational.

---

## Features

- **Live stock dashboard** — fetches real-time price, P/E ratio, beta, sector, and 30-day OHLCV history for 50+ popular tickers via `yfinance`
- **AI-generated insights** — uses Google Gemini (`gemini-1.5-flash`) to produce concise investment analyses covering price action, fundamentals, risk, and recommended investment horizon
- **Graceful fallback** — if the Gemini API is unavailable or over quota, a heuristic rule-based summary is returned automatically instead of an error
- **Portfolio tracker** — add, update, and delete holdings; see live per-holding valuations and total portfolio value
- **Analysis history** — every AI analysis is persisted to SQLite and browsable in a paginated history view (last 50 entries)
- **PDF report generation** — download a formatted portfolio report (ticker, quantity, price, value, total) via ReportLab
- **Markdown rendering** — AI insight text is rendered as rich HTML in the browser

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask, Flask-SQLAlchemy |
| Database | SQLite (default) / any SQLAlchemy-compatible DB |
| AI | Google Gemini (`google-generativeai`, `gemini-1.5-flash`) |
| Market data | `yfinance` |
| PDF generation | ReportLab |
| Markdown | `markdown` (Python) |
| Frontend | Bootstrap 5, Vanilla JS |
| Environment | `python-dotenv` |

---

## Project Structure

```
finanalyst/
├── app.py                    # Flask app — routes, API endpoints, PDF generation
├── ai_module.py              # Gemini API integration and heuristic fallback logic
├── models.py                 # SQLAlchemy models: Holding, AnalysisHistory
├── extensions.py             # Shared SQLAlchemy instance (avoids circular imports)
├── utils.py                  # yfinance data fetching and DataFrame helpers
├── templates/
│   ├── base.html             # Shared navbar and Bootstrap layout
│   ├── index.html            # Home page: stock table + analysis form
│   ├── portfolio.html        # Portfolio manager
│   ├── analysis.html         # Analysis history table
│   └── insight_summary.html  # Full AI insight view
├── .env                      # Environment variables (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/aAnmol2010/AI-powered-financial-analyst-assistant.git
cd AI-powered-financial-analyst-assistant
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=<YOUR_OPENAI_KEY>
SECRET_KEY=your_random_secret_key_here
DATABASE_URL=sqlite:///finance.db
FLASK_ENV=development
PORT=5000
```

> **Getting a Gemini API key:** Visit [aistudio.google.com](https://aistudio.google.com) → **Get API key** → **Create API key**.
>
> **Generating a SECRET_KEY:** Run `python -c "import secrets; print(secrets.token_hex(32))"` and paste the output.

### 5. Run the application

```bash
python app.py
```

Open your browser at `http://localhost:5000`.

---

## Usage Guide

### Analyze a stock
1. On the home page, type any ticker symbol (e.g. `AAPL`, `TSLA`, `NVDA`) into the search bar.
2. Click **Analyze**.
3. The app fetches live data, sends it to Gemini, and redirects you to the full AI insight summary page.

### Manage your portfolio
1. Navigate to **Portfolio** in the navbar.
2. Enter a ticker and quantity, then click **Add / Update**. Holdings accumulate if the ticker already exists.
3. Click **Delete** to remove a holding.

### Download a PDF report
Click **Download PDF** in the navbar to download a formatted portfolio report with live prices and total value.

### View analysis history
Navigate to **Analysis History** to browse the 50 most recent AI-generated analyses with UTC timestamps.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Home page with default stock table |
| `GET` | `/portfolio` | Portfolio manager page |
| `GET` | `/history` | Analysis history page |
| `GET` | `/insight_summary` | Full AI insight view (session-based) |
| `POST` | `/api/analyze` | Fetch stock data + generate AI insight |
| `POST` | `/api/portfolio` | Add or update a holding |
| `POST` | `/api/portfolio/delete` | Delete a holding |
| `GET` | `/report/portfolio.pdf` | Download portfolio PDF report |

### `POST /api/analyze`

**Request body:**
```json
{ "ticker": "AAPL" }
```

**Response:**
```json
{
  "status": "ok",
  "stock": {
    "ticker": "AAPL",
    "company": "Apple Inc.",
    "price": 189.45,
    "change_pct": 1.23,
    "pe_ratio": 28.5,
    "beta": 1.21,
    "sector": "Technology"
  },
  "insight": "...(AI-generated analysis)...",
  "history_preview": [ "...last 30 rows of OHLCV data..." ]
}
```

### `POST /api/portfolio`

**Request body:**
```json
{ "ticker": "MSFT", "quantity": 10 }
```

### `POST /api/portfolio/delete`

**Request body:**
```json
{ "ticker": "MSFT" }
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | Google Gemini API key for AI insights |
| `SECRET_KEY` | Yes | `CHANGE_THIS_TO_A_RANDOM_VALUE` | Flask session secret key |
| `DATABASE_URL` | No | `sqlite:///finance.db` | SQLAlchemy database URI |
| `FLASK_ENV` | No | — | Set to `development` to enable debug mode |
| `PORT` | No | `5000` | Port to run the Flask server on |

---

## Database Models

### `Holding`
| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-incremented primary key |
| `ticker` | String(16) | Stock ticker symbol (unique) |
| `quantity` | Float | Number of shares held |

### `AnalysisHistory`
| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-incremented primary key |
| `ticker` | String(16) | Stock ticker symbol |
| `analysis` | Text | Full AI-generated analysis text |
| `created_at` | DateTime | UTC timestamp of the analysis |

---

## Notes and Limitations

- **Home page load time:** The home page fetches 50 tickers on every load. This can be slow or rate-limited by Yahoo Finance. Consider adding server-side caching (e.g. Flask-Caching) in production.
- **Session-based insight routing:** The AI insight is passed to `/insight_summary` via Flask's server-side session. If the session expires or the browser is refreshed before the redirect, the page will show an error prompting you to analyze a stock first.
- **SQLite in production:** SQLite works well for local development. For production deployments, set `DATABASE_URL` to a PostgreSQL or MySQL URI.
- **Gemini fallback:** If `GEMINI_API_KEY` is not set or the Gemini API is over quota, the app automatically returns a heuristic analysis based on P/E, beta, and price change — it will never crash or return a blank response.

---

## License

MIT License. See `LICENSE` for details.