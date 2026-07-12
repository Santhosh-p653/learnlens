import { Client } from "@gradio/client";

const SPACE_URL = process.env.HF_SPACE_URL || "your-username/learnlens";

export async function POST(req) {
  try {
    const formData = await req.formData();
    const image = formData.get("image");
    const voice = formData.get("voice"); // may be null
    const gradeLevel = formData.get("gradeLevel") || "Middle school";
    const language = formData.get("language") || "English";

    const client = await Client.connect(SPACE_URL, {
      hf_token: process.env.HF_TOKEN, // only needed if Space is private
    });

    const result = await client.predict("/process", [
      image,
      voice || null,
      gradeLevel,
      language,
    ]);

    const [explanation, audio] = result.data;

    return Response.json({
      explanation,
      audioUrl: audio?.url || null,
    });
  } catch (err) {
    console.error("LearnLens API error:", err);
    return Response.json(
      { explanation: "Backend error — check Space status.", audioUrl: null },
      { status: 500 }
    );
  }
}