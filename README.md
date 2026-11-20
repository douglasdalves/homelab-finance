# Homelab Finance

A self-hosted finance dashboard for tracking monthly cash flow, housing costs,
investment activity, and fixed-income snapshots. The application is designed for
private homelab deployment and keeps financial records in local SQLite and JSON
storage.

## Features

- Dashboard for income, expenses, balances, housing costs, and yearly summaries.
- Manual entry screens backed by a local SQLite database.
- Investment imports from spreadsheet and CSV files.
- Fixed-income history imported from consolidated PDF reports.
- Demonstration mode with synthetic dashboard values.

## Architecture

```text
Browser
  ├── Dashboard pages and styles (web/)
  └── Same-origin /api requests
            │
            ▼
       Nginx (deploy/nginx/)
            │ /api/
            ▼
 Finance API (src/finance_app/)
      ├── SQLite database
      └── Private investment JSON files
```

The web server should expose only the contents of `web/`. Configuration and
financial data must remain outside the web document root. Keep the deployment
on a trusted network or behind an authenticated reverse proxy.

## Example interaction

1. Open the dashboard and review monthly income and expenses.
2. Add a transaction in the entry page; the browser sends it to the finance API.
3. The API validates the entry and persists it in SQLite.
4. The dashboard reloads the updated data through the same-origin API.

See [docs/PROJECT.md](docs/PROJECT.md) for setup, deployment, and validation
instructions in Portuguese.
