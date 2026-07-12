---
title: LearnLens
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.29.0
app_file: app.py
pinned: false
---

# LearnLens Backend

Gradio Space powering LearnLens — photo-to-explanation learning assistant.

## Secrets required (Space settings → Variables and secrets)
- SAMBANOVA_API_KEY
- HF_TOKEN (needs read access to Inference API)

## API endpoint
Once deployed, callable via gradio_client at:
https://<your-username>-learnlens.hf.space