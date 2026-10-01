import os
import base64
import fitz  # PyMuPDF
from dotenv import load_dotenv
from deepgram import DeepgramClient
from groq import Groq

load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not DEEPGRAM_API_KEY or not GROQ_API_KEY:
    raise ValueError("Missing API keys. Please check your .env file.")

dg_client = DeepgramClient(api_key=DEEPGRAM_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

INBOX_FOLDER = "./Inbox"
TRANSCRIPT_FOLDER = "./Transcripts"
WIKI_FOLDER = "./Medical Wiki"

audio_schema = """
You are an expert transcriptionist and education assistant. Your task is to convert raw lecture transcripts into structured, clean Markdown notes optimized for Obsidian. 

Follow these formatting rules strictly:
1. Learning Objectives: If the text states specific learning objectives, create a dedicated `## Learning Objectives` section at the very top of the note. 
2. Headings: Use `##` for main topics and `###` for sub-topics.
3. Wikilinks: Wrap all core terms, concepts, legal acts, and distinct entities in double brackets (e.g., `[[Term]]`). 
4. Lists & Bolding: Use bullet points for key details and bold the key terms at the start of each bullet point.
5. No Citations: Do not include inline citations.
6. Comprehensiveness: Retain all critical definitions, clinical parameters, and technical values from the source material.
"""

notes_expansion_schema = """
You are an expert tutor. The user has provided chemistry and biology notes containing a mix of text and visual screenshots. 

Your task is to interpret the entire context and output a seamless, comprehensive Obsidian study guide.

Strict Directives:
1. Complete the Thought: If the user's notes trail off or contain blanks, seamlessly fill in the missing biochemical mechanisms, formulas, or physiological processes.
2. Expand & Cite: If relevant academic data is missing from the core concepts (e.g., standard clinical values, enzyme cofactors, or reaction catalysts), add it. You MUST append a brief inline citation for any added data (e.g., `(Added Context: standard physiological pH is 7.35-7.45)`).
3. Visual Interpretation: Transcribe and integrate the data found within the screenshots (diagrams, molecular structures) directly into the text flow.
4. Obsidian Formatting: Use `##` for main topics, `###` for sub-topics. Wrap all core concepts, enzymes, and anatomical structures in double brackets (e.g., `[[Krebs Cycle]]`). Do not include conversational filler.
"""

def encode_pdf_to_base64_images(pdf_path):
    doc = fitz.open(pdf_path)
    base64_images = []
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        base64_images.append(base64.b64encode(img_bytes).decode('utf-8'))
    return base64_images

def process_inbox():
    for folder in [INBOX_FOLDER, TRANSCRIPT_FOLDER, WIKI_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    files = sorted([f for f in os.listdir(INBOX_FOLDER) if f.lower().endswith((".mp3", ".pdf"))])
    print(f"Found {len(files)} files in Inbox.")

    for idx, filename in enumerate(files, 1):
        file_path = os.path.join(INBOX_FOLDER, filename)
        base_name = os.path.splitext(filename)[0]
        wiki_path = os.path.join(WIKI_FOLDER, f"{base_name}.md")

        if os.path.exists(wiki_path):
            print(f"[{idx}/{len(files)}] Skipping '{filename}' — note already exists.")
            continue

        if filename.lower().endswith(".mp3"):
            transcript_path = os.path.join(TRANSCRIPT_FOLDER, f"{base_name}.txt")
            if os.path.exists(transcript_path):
                print(f"[{idx}/{len(files)}] Loaded cached transcript: {base_name}.txt")
                with open(transcript_path, "r", encoding="utf-8") as f:
                    transcript = f.read()
            else:
                print(f"[{idx}/{len(files)}] 🎧 Audio detected: {filename}. Transcribing with Deepgram...")
                try:
                    with open(file_path, "rb") as audio:
                        response = dg_client.listen.v1.media.transcribe_file(
                            request=audio.read(), model="nova-3", smart_format=True
                        )
                    try:
                        transcript = response.results.channels[0].alternatives[0].transcript
                    except (AttributeError, TypeError):
                        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
                    with open(transcript_path, "w", encoding="utf-8") as f:
                        f.write(transcript)
                except Exception as e:
                    print(f"[!] Deepgram transcription failed: {e}")
                    continue

            print(f"[{idx}/{len(files)}] -> Structuring lecture with Groq...")
            try:
                completion = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {"role": "system", "content": audio_schema},
                        {"role": "user", "content": f"Format this entire lecture transcript strictly according to the instructions:\n\n{transcript}"},
                    ],
                    temperature=0.3,
                )
                with open(wiki_path, "w", encoding="utf-8") as f:
                    f.write(completion.choices[0].message.content)
                print(f"✅ Successfully generated note: {wiki_path}")
            except Exception as e:
                print(f"[!] Groq formatting failed: {e}")

        elif filename.lower().endswith(".pdf"):
            print(f"[{idx}/{len(files)}] 📝 Mixed media notes detected: {filename}. Slicing PDF for Vision AI...")
            try:
                base64_pages = encode_pdf_to_base64_images(file_path)
                content_payload = [{"type": "text", "text": "Please read these notes and screenshots, fill in the blanks, and compile them into a seamless Obsidian guide."}]
                for b64_img in base64_pages:
                    content_payload.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64_img}"}
                    })

                print(f"[{idx}/{len(files)}] -> Analyzing text and screenshots with Groq Vision...")
                completion = groq_client.chat.completions.create(
                    model="llama-3.2-90b-vision-preview",
                    messages=[
                        {"role": "system", "content": notes_expansion_schema},
                        {"role": "user", "content": content_payload},
                    ],
                    temperature=0.3,
                )
                with open(wiki_path, "w", encoding="utf-8") as f:
                    f.write(completion.choices[0].message.content)
                print(f"✅ Successfully generated note: {wiki_path}")
            except Exception as e:
                print(f"[!] Groq Vision processing failed: {e}")

if __name__ == "__main__":
    process_inbox()
