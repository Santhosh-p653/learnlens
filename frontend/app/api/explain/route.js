const BACKEND_URL = process.env.BACKEND_URL || "https://learnlens.onrender.com";

export async function POST(req) {
  try {
    const formData = await req.formData();
    const image = formData.get("image");
    const voice = formData.get("voice");
    const gradeLevel = formData.get("gradeLevel") || "Middle school";
    const language = formData.get("language") || "English";

    const backendForm = new FormData();
    backendForm.append("image", image);
    if (voice) backendForm.append("voice", voice);
    backendForm.append("gradeLevel", gradeLevel);
    backendForm.append("language", language);

    const res = await fetch(`${BACKEND_URL}/process`, {
      method: "POST",
      body: backendForm,
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText);
    }

    const data = await res.json();

    return Response.json({
      explanation: data.explanation,
      audioUrl: `data:audio/mpeg;base64,${data.audio_base64}`,
    });
  } catch (err) {
    console.error("LearnLens API error:", err);
    return Response.json(
      { explanation: "Backend error — check Render service status.", audioUrl: null },
      { status: 500 }
    );
  }
}