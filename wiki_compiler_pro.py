import os
from dotenv import load_dotenv
from deepgram import DeepgramClient
from groq import Groq

# Load secure API keys from the .env file
load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not DEEPGRAM_API_KEY or not GROQ_API_KEY:
    raise ValueError("Missing API keys. Please check your .env file.")

dg_client = DeepgramClient(api_key=DEEPGRAM_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

RAW_FOLDER = "./Raw Transcripts"
TRANSCRIPT_FOLDER = "./Transcripts"
WIKI_FOLDER = "./Medical Wiki"

schema_instructions = """
You are an expert transcriptionist and education assistant. Your task is to convert raw lecture transcripts into structured, clean Markdown notes optimized for Obsidian. 

Follow these formatting rules strictly:
1. Learning Objectives: If the text states specific learning objectives, create a dedicated `## Learning Objectives` section at the very top of the note. 
2. Headings: Use `##` for main topics and `###` for sub-topics.
3. Wikilinks: Wrap all core terms, concepts, legal acts, and distinct entities in double brackets (e.g., `[[Term]]`). 
4. Lists & Bolding: Use bullet points for key details and bold the key terms at the start of each bullet point.
5. No Citations: Do not include inline citations.
6. Comprehensiveness: Retain all critical definitions, clinical parameters, and technical values from the source material.
"""

def compile_wikis():
    for folder in [RAW_FOLDER, TRANSCRIPT_FOLDER, WIKI_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    files = sorted([f for f in os.listdir(RAW_FOLDER) if f.lower().endswith(".mp3")])
    print(f"Found {len(files)} total MP3 file(s).")

    for idx, filename in enumerate(files, 1):
        base_name = os.path.splitext(filename)[0]
        transcript_path = os.path.join(TRANSCRIPT_FOLDER, f"{base_name}.txt")
        wiki_path = os.path.join(WIKI_FOLDER, f"{base_name}.md")

        if os.path.exists(wiki_path):
            print(f"[{idx}/{len(files)}] Skipping '{base_name}' — note already exists.")
            continue

        # --- STEP 1: DEEPGRAM TRANSCRIPTION ---
        if os.path.exists(transcript_path):
            print(f"[{idx}/{len(files)}] Loaded cached transcript: {base_name}.txt")
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript = f.read()
        else:
            print(f"\n[{idx}/{len(files)}] Transcribing audio with Deepgram...")
            try:
                mp3_path = os.path.join(RAW_FOLDER, filename)
                with open(mp3_path, "rb") as audio:
                    response = dg_client.listen.v1.media.transcribe_file(
                        request=audio.read(), model="nova-3", smart_format=True
                    )
                try:
                    transcript = response.results.channels[0].alternatives[0].transcript
                except (AttributeError, TypeError):
                    transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]

                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(transcript)
                print(f"-> Saved transcript ({len(transcript):,} characters).")
            except Exception as e:
                print(f"[!] Deepgram transcription failed: {e}")
                continue

        # --- STEP 2: GROQ STRUCTURING (SINGLE PASS) ---
        print(f"[{idx}/{len(files)}] Formatting full {len(transcript):,}-character note with Groq...")
        try:
            completion = groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": schema_instructions},
                    {"role": "user", "content": f"Format this entire lecture transcript strictly according to the instructions:\n\n{transcript}"},
                ],
                temperature=0.3,
            )
            with open(wiki_path, "w", encoding="utf-8") as f:
                f.write(completion.choices[0].message.content)
            print(f"-> Successfully generated note: {wiki_path}")

        except Exception as e:
            print(f"[!] Groq formatting failed: {e}")

if __name__ == "__main__":
    compile_wikis()
