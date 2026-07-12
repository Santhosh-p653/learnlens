---
title: LearnLens
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
---

# LearnLens

LearnLens is an AI-powered learning accessibility tool that helps students understand textbook content more easily.

## Features

- 📷 Upload a textbook page or diagram
- 🎙️ Ask questions using your voice
- 🧠 AI-generated simplified explanations
- 🌍 Multiple language support
- 🔊 Text-to-speech output

## Required Secrets

Add the following secrets in your Hugging Face Space:

- `SAMBANOVA_API_KEY`
- `HF_TOKEN`

## Deployment

This project is designed for **Hugging Face Spaces (Gradio + ZeroGPU)**.

The app entry point is:

```
app.py
```

After deployment, your Space will be available at:

```
https://<your-username>-learnlens.hf.space
```