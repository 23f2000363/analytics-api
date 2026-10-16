# Stateless FastAPI Analytics API

`POST /analytics` authenticates with `X-API-Key`, aggregates every batch at request time, and stores no event data.

## Response aggregation

- `total_events`: number of events in the request.
- `unique_users`: number of distinct `user` strings.
- `revenue`: sum of `amount` values strictly greater than zero.
- `top_user`: user with the largest total of strictly positive amounts; `null` when no positive amounts exist.
- `email`: `23f2000363@ds.study.iitm.ac.in`.

CORS uses `Access-Control-Allow-Origin: *`, which is suitable because the endpoint does not use browser cookies or credentialed requests.

## Deploy on Vercel

1. Create a public or private Git repository and upload the contents of this folder to the repository root (especially `main.py` and `requirements.txt`).
2. Import the repository at https://vercel.com/new. Vercel detects FastAPI from the `app = FastAPI()` object in `main.py`.
3. In Project Settings → Environment Variables, add:
   - Name: `ANALYTICS_API_KEY`
   - Value: the assigned exam API key shown in the challenge instructions.
   - Environment: Production (and Preview if you plan to test preview deployments).
4. Redeploy after adding the environment variable.
5. Submit `https://<your-project>.vercel.app/analytics`.

Keep the assigned key in deployment environment settings rather than committing it into source code.

## Local testing

Python 3.12+

```bash
python -m venv .venv
# Linux / macOS / WSL:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
export ANALYTICS_API_KEY='paste-your-assigned-key-here' # PowerShell: $env:ANALYTICS_API_KEY='paste-your-assigned-key-here'
uvicorn main:app --reload --port 8000
```

Run tests:

```bash
pytest -q
```

Try it with curl (replace the value with your assigned key):

```bash
curl -X POST http://localhost:8000/analytics \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: paste-your-assigned-key-here' \
  -d '{"events":[{"user":"alice","amount":42.5,"ts":1700000000},{"user":"bob","amount":-3,"ts":1700000001}]}'
```
