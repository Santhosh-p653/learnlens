import gradio as gr
import requests
import os
import asyncio
import tempfile
import edge_tts
import spaces

# ---- Config ----
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "https://api.sambanova.ai/v1/chat/completions"
SAMBANOVA_MODEL = "Meta-Llama-3.1-70B-Instruct"  # swap to your preferred SambaNova model

HF_TOKEN = os.environ.get("HF_TOKEN")
CAPTION_MODEL_URL = "https://api-inference.huggingface.co/models/Salesforce/blip2-opt-2.7b"
WHISPER_MODEL_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"

TTS_VOICE_MAP = {
    "English": "en-US-AriaNeural",
    "Hindi": "hi-IN-SwaraNeural",
    "Tamil": "ta-IN-PallaviNeural",
    "Spanish": "es-ES-ElviraNeural",
    "French": "fr-FR-DeniseNeural",
}


def caption_image(image_bytes: bytes) -> str:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    resp = requests.post(CAPTION_MODEL_URL, headers=headers, data=image_bytes, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    return str(result)


def transcribe_audio(audio_path: str) -> str:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    with open(audio_path, "rb") as f:
        data = f.read()
    resp = requests.post(WHISPER_MODEL_URL, headers=headers, data=data, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    return result.get("text", "")


def explain_with_sambanova(caption: str, question: str, grade_level: str, language: str) -> str:
    system_prompt = (
        f"You are a friendly tutor. Explain the following textbook content at a "
        f"{grade_level} reading level. If a student question is provided, answer it directly. "
        f"Respond in {language}. Keep it concise, clear, and encouraging."
    )
    user_content = f"Textbook content (from image): {caption}"
    if question.strip():
        user_content += f"\n\nStudent question: {question}"

    headers = {
        "Authorization": f"Bearer {SAMBANOVA_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": SAMBANOVA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.4,
    }
    resp = requests.post(SAMBANOVA_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


async def _tts(text: str, voice: str, out_path: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)


def text_to_speech(text: str, language: str) -> str:
    voice = TTS_VOICE_MAP.get(language, "en-US-AriaNeural")
    out_path = tempfile.mktemp(suffix=".mp3")
    asyncio.run(_tts(text, voice, out_path))
    return out_path


@spaces.GPU(duration=30)
def process(image, voice_question, grade_level, language):
    if image is None:
        return "Please upload a photo of the textbook page or diagram.", None

    with open(image, "rb") as f:
        image_bytes = f.read()
    caption = caption_image(image_bytes)

    question_text = ""
    if voice_question is not None:
        question_text = transcribe_audio(voice_question)

    explanation = explain_with_sambanova(caption, question_text, grade_level, language)
    audio_path = text_to_speech(explanation, language)

    return explanation, audio_path


with gr.Blocks(title="LearnLens") as demo:
    gr.Markdown("# 📚 LearnLens — Learning Made Accessible")
    gr.Markdown("Upload a photo of any textbook page or diagram. Ask a question by voice (optional). Get a simplified explanation, read aloud in your language.")

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="filepath", label="Textbook Page / Diagram Photo")
            voice_input = gr.Audio(type="filepath", label="Ask a question (optional, voice)")
            grade_level = gr.Dropdown(
                ["Simple (age 8-10)", "Middle school", "High school", "College"],
                value="Middle school", label="Explanation Level"
            )
            language = gr.Dropdown(
                list(TTS_VOICE_MAP.keys()), value="English", label="Language"
            )
            submit_btn = gr.Button("Explain This", variant="primary")

        with gr.Column():
            explanation_output = gr.Textbox(label="Simplified Explanation", lines=10)
            audio_output = gr.Audio(label="Listen")

    submit_btn.click(
        fn=process,
        inputs=[image_input, voice_input, grade_level, language],
        outputs=[explanation_output, audio_output],
    )

demo.launch()