# LearnLens Backend (Flask, deployed on Render)

## Endpoints
- GET /health — health check
- POST /process — multipart form: image (file), voice (file, optional), gradeLevel, language
  Returns: { explanation: string, audio_base64: string }

## Environment variables (set in Render dashboard)
- SAMBANOVA_API_KEY
- HF_TOKEN

## Deploy on Render
1. New → Web Service → connect this repo
2. Root directory: backend
3. Build command: pip install -r requirements.txt
4. Start command: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120
5. Instance type: Free
6. Add env vars: SAMBANOVA_API_KEY, HF_TOKEN