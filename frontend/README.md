# RAG UI (React + Vite + Tailwind)

A simple, modern frontend for your RAG FastAPI backend, featuring:

- Drag-and-drop PDF upload with progress
- Chat interface to ask questions about uploaded document
- Tailwind CSS styling

## Prerequisites
- Node.js 18+

## Setup
```bash
cd frontend/rag-ui
npm install
cp .env.example .env # optional: adjust backend URL if not localhost:8000
```

## Run
```bash
npm run dev
```
Open the URL shown (default http://localhost:5173) in your browser.

## Build
```bash
npm run build
npm run preview
```

## Config
- API base URL: set `VITE_API_BASE_URL` in `.env`
- Tailwind is configured via `tailwind.config.js` and imported in `src/styles/index.css`
