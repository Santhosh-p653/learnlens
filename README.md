# LearnLens — Setup to Deploy

## 1. Backend (Hugging Face Space, ~5 min)
cd backend
git init
git remote add origin https://huggingface.co/spaces/<your-username>/learnlens
git add .
git commit -m "init"
git push origin main

- Create the Space first at huggingface.co/new-space → SDK: Gradio → name: learnlens
- Space Settings → Variables and secrets → add: SAMBANOVA_API_KEY, HF_TOKEN
- Wait for build. Test at https://<your-username>-learnlens.hf.space

## 2. Frontend (Vercel, ~5 min)
cd frontend
npm install
vercel

- Link/create project on first run
- Vercel dashboard → Settings → Environment Variables: HF_SPACE_URL, HF_TOKEN
- Redeploy: vercel --prod

## 3. Test end to end
- Open Vercel URL, upload photo, optionally record question, hit "Explain This"
- First request may be slow if Space is cold-starting