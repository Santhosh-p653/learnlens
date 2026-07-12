"use client";

import { useState, useRef } from "react";

const LANGUAGES = ["English", "Hindi", "Tamil", "Spanish", "French"];
const GRADE_LEVELS = ["Simple (age 8-10)", "Middle school", "High school", "College"];

export default function Home() {
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [voiceBlob, setVoiceBlob] = useState(null);
  const [gradeLevel, setGradeLevel] = useState("Middle school");
  const [language, setLanguage] = useState("English");
  const [explanation, setExplanation] = useState("");
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    chunksRef.current = [];
    recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      setVoiceBlob(blob);
      stream.getTracks().forEach((t) => t.stop());
    };
    recorder.start();
    mediaRecorderRef.current = recorder;
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  const handleSubmit = async () => {
    if (!imageFile) return alert("Upload a photo first.");
    setLoading(true);
    setExplanation("");
    setAudioUrl(null);

    const formData = new FormData();
    formData.append("image", imageFile);
    if (voiceBlob) formData.append("voice", voiceBlob, "question.webm");
    formData.append("gradeLevel", gradeLevel);
    formData.append("language", language);

    try {
      const res = await fetch("/api/explain", { method: "POST", body: formData });
      const data = await res.json();
      setExplanation(data.explanation);
      setAudioUrl(data.audioUrl);
    } catch (err) {
      setExplanation("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 640, margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ fontSize: "1.75rem", marginBottom: "0.25rem" }}>📚 LearnLens</h1>
      <p style={{ color: "#94a3b8", marginBottom: "1.5rem" }}>
        Snap a photo of any textbook page or diagram. Ask a question by voice. Get it explained simply, in your language.
      </p>

      <section style={{ marginBottom: "1rem" }}>
        <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600 }}>
          Textbook Page / Diagram
        </label>
        <input type="file" accept="image/*" capture="environment" onChange={handleImageChange} />
        {imagePreview && (
          <img src={imagePreview} alt="preview" style={{ marginTop: "0.75rem", maxWidth: "100%", borderRadius: 8 }} />
        )}
      </section>

      <section style={{ marginBottom: "1rem" }}>
        <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600 }}>
          Ask a Question (optional, voice)
        </label>
        {!recording ? (
          <button onClick={startRecording} style={btnStyle}>🎙️ Start Recording</button>
        ) : (
          <button onClick={stopRecording} style={{ ...btnStyle, background: "#dc2626" }}>⏹ Stop</button>
        )}
        {voiceBlob && <span style={{ marginLeft: "0.75rem", color: "#4ade80" }}>Question recorded ✓</span>}
      </section>

      <section style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
        <div style={{ flex: 1 }}>
          <label style={{ display: "block", marginBottom: "0.25rem", fontWeight: 600 }}>Level</label>
          <select value={gradeLevel} onChange={(e) => setGradeLevel(e.target.value)} style={selectStyle}>
            {GRADE_LEVELS.map((g) => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>
        <div style={{ flex: 1 }}>
          <label style={{ display: "block", marginBottom: "0.25rem", fontWeight: 600 }}>Language</label>
          <select value={language} onChange={(e) => setLanguage(e.target.value)} style={selectStyle}>
            {LANGUAGES.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
      </section>

      <button onClick={handleSubmit} disabled={loading} style={{ ...btnStyle, width: "100%", background: "#4f46e5", padding: "0.75rem" }}>
        {loading ? "Thinking..." : "Explain This"}
      </button>

      {explanation && (
        <section style={{ marginTop: "2rem", background: "#111827", padding: "1.25rem", borderRadius: 10 }}>
          <h3 style={{ marginTop: 0 }}>Explanation</h3>
          <p style={{ lineHeight: 1.6, whiteSpace: "pre-wrap" }}>{explanation}</p>
          {audioUrl && (
            <audio controls src={audioUrl} style={{ width: "100%", marginTop: "0.75rem" }} />
          )}
        </section>
      )}
    </main>
  );
}

const btnStyle = {
  background: "#334155",
  color: "#fff",
  border: "none",
  borderRadius: 8,
  padding: "0.5rem 1rem",
  cursor: "pointer",
  fontSize: "0.95rem",
};

const selectStyle = {
  width: "100%",
  padding: "0.5rem",
  borderRadius: 8,
  background: "#1e293b",
  color: "#fff",
  border: "1px solid #334155",
};