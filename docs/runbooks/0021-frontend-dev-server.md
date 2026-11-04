# Runbook 0021: Next.js Frontend Development Server

## Objective
Start and configure the local Next.js frontend workspace connecting to the FastAPI backend.

## Prerequisites
- Node.js >= 20.0.0
- FastAPI backend running on `http://localhost:8080`

## Procedure
```bash
cd apps/dashboard
npm install
npm run dev
```
Open `http://localhost:3000` in the browser. Verify backend health pill shows "Postgres/SQLite Live".
