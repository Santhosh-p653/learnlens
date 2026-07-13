from flask import Flask, request, jsonify
import requests
import os
import asyncio
import tempfile
import base64
import edge_tts
from huggingface_hub import InferenceClient

app = Flask(__name__)

# ---- Config ----
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "https://api.sambanova.ai/v1/chat/completions"
SAMBANOVA_MODEL = "Meta-Llama-3.1-70B-Instruct"

HF_TOKEN = os.environ.get("HF_TOKEN")
hf_client = InferenceClient(token=HF_TOKEN)

TTS_VOICE_MAP = {
    "English": "en-US-AriaNeural",
    "Hindi": "hi-IN-SwaraNeural",
    "Tamil": "ta-IN-PallaviNeural",
    "Spanish": "es-ES-ElviraNeural",
    "French": "fr-FR-DeniseNeural",
}


def caption_image(image_bytes: bytes) -> str:
    result = hf_client.image_to_text(image_bytes, model="Salesforce/blip2-opt-2.7b")
    if isinstance(result, dict) and "generated_text" in result:
        return result["generated_text"]
    return str(result)


def transcribe_audio(audio_bytes: bytes) -> str:
    result = hf_client.automatic_speech_recognition(audio_bytes, model="openai/whisper-large-v3")
    if isinstance(result, dict) and "text" in result:
        return result["text"]
    return str(result)


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


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/process", methods=["POST"])
def process():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files["image"]
    image_bytes = image_file.read()

    grade_level = request.form.get("gradeLevel", "Middle school")
    language = request.form.get("language", "English")

    question_text = ""
    if "voice" in request.files:
        voice_file = request.files["voice"]
        voice_bytes = voice_file.read()
        try:
            question_text = transcribe_audio(voice_bytes)
        except Exception:
            question_text = ""

    try:
        caption = caption_image(image_bytes)
        explanation = explain_with_sambanova(caption, question_text, grade_level, language)
        audio_path = text_to_speech(explanation, language)

        with open(audio_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")

        return jsonify({
            "explanation": explanation,
            "audio_base64": audio_b64,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)