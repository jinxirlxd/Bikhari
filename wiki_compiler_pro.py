import os
import json
import base64
import fitz  # PyMuPDF
from dotenv import load_dotenv
from deepgram import DeepgramClient
from groq import Groq

load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not DEEPGRAM_API_KEY or not GROQ_API_KEY:
    raise ValueError("Missing API keys in .env file.")

dg_client = DeepgramClient(api_key=DEEPGRAM_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

INBOX_FOLDER = "./Inbox"
WIKI_FOLDER = "./Medical Wiki"
ARCHIVE_FOLDER = "./Archive"
TRANSCRIPT_FOLDER = "./Transcripts"

def get_vault_manifest():
    """Scans existing notes in the Obsidian vault."""
    if not os.path.exists(WIKI_FOLDER):
        os.makedirs(WIKI_FOLDER, exist_ok=True)
    files = [f for f in os.listdir(WIKI_FOLDER) if f.lower().endswith(".md")]
    return [os.path.splitext(f)[0] for f in files]

def encode_pdf_to_base64_images(pdf_path):
    doc = fitz.open(pdf_path)
    base64_images = []
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        base64_images.append(base64.b64encode(img_bytes).decode('utf-8'))
    return base64_images

def route_and_structure(raw_text=None, base64_pages=None):
    vault_topics = get_vault_manifest()
    
    system_prompt = f"""You are an expert pre-med knowledge management agent for Obsidian.
Existing topics in the user's vault: {json.dumps(vault_topics)}

Your Directives:
1. Classification: Decide whether this content is a miscellaneous scrap/detail that belongs inside one of the EXISTING topics, or if it represents a brand NEW standalone topic.
2. If it belongs in an existing topic:
   - "mode": "append"
   - "target_topic": <Exact matching topic name from the list>
   - "markdown": Output a clean addition starting with `### Clinical Addendum: <Brief Title>` or `### Additional Mechanism: <Brief Title>`, followed by structured bullet points, completed mechanism blanks, and cited parameters.
3. If it is a new topic:
   - "mode": "create"
   - "target_topic": <Descriptive note title>
   - "markdown": Output a full structured note with `## Learning Objectives`, headings, and bullet points.
4. Always wrap key clinical/biochemical terms in [[Wikilinks]].

Respond ONLY with valid JSON matching this schema:
{{
  "mode": "append" or "create",
  "target_topic": "Topic Name",
  "markdown": "Structured markdown content..."
}}"""

    if base64_pages:
        content_payload = [{"type": "text", "text": "Analyze these notes/screenshots and sort them according to instructions."}]
        for b64 in base64_pages:
            content_payload.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}})
        
        completion = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content_payload}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
    else:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze and sort this content:\n\n{raw_text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

    return json.loads(completion.choices[0].message.content)

def process_inbox():
    for f in [INBOX_FOLDER, WIKI_FOLDER, ARCHIVE_FOLDER, TRANSCRIPT_FOLDER]:
        os.makedirs(f, exist_ok=True)

    files = sorted([f for f in os.listdir(INBOX_FOLDER) if f.lower().endswith((".mp3", ".pdf", ".txt", ".md"))])
    if not files:
        print("Inbox is empty. Drop files into Inbox/ to process.")
        return

    print(f"Found {len(files)} file(s) in Inbox.")

    for idx, filename in enumerate(files, 1):
        file_path = os.path.join(INBOX_FOLDER, filename)
        base_name = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1].lower()
        wiki_path = os.path.join(WIKI_FOLDER, f"{base_name}.md")
        transcript_path = os.path.join(TRANSCRIPT_FOLDER, f"{base_name}.txt")

        # 1. SKIP CHECK: Note already finished in Medical Wiki
        if os.path.exists(wiki_path):
            print(f"[{idx}/{len(files)}] ⏭️  Skipping '{filename}' — '{base_name}.md' already exists.")
            archive_dest = os.path.join(ARCHIVE_FOLDER, filename)
            os.replace(file_path, archive_dest)
            print(f"    -> Moved '{filename}' to Archive/.")
            continue

        print(f"\n[{idx}/{len(files)}] Processing: {filename}")

        try:
            if ext == ".mp3":
                # 2. CACHE CHECK: Avoid re-calling Deepgram if text transcript exists
                if os.path.exists(transcript_path):
                    print(f"    ⚡ Loaded cached transcript: {base_name}.txt (Deepgram skipped).")
                    with open(transcript_path, "r", encoding="utf-8") as f:
                        transcript = f.read()
                else:
                    print("    🎧 Transcribing audio with Deepgram...")
                    with open(file_path, "rb") as audio:
                        res = dg_client.listen.v1.media.transcribe_file(request=audio.read(), model="nova-3", smart_format=True)
                    try:
                        transcript = res.results.channels[0].alternatives[0].transcript
                    except:
                        transcript = res["results"]["channels"][0]["alternatives"][0]["transcript"]
                    with open(transcript_path, "w", encoding="utf-8") as f:
                        f.write(transcript)

                result = route_and_structure(raw_text=transcript)

            elif ext == ".pdf":
                print("    📝 Slicing PDF for Vision classification...")
                pages = encode_pdf_to_base64_images(file_path)
                result = route_and_structure(base64_pages=pages)

            elif ext in [".txt", ".md"]:
                print("    📄 Reading text scrap...")
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                result = route_and_structure(raw_text=content)

            mode = result.get("mode", "create")
            target = result.get("target_topic", base_name).replace(".md", "").strip()
            markdown = result.get("markdown", "").strip()
            target_path = os.path.join(WIKI_FOLDER, f"{target}.md")

            if mode == "append" and os.path.exists(target_path):
                print(f"    📌 Merging scrap into existing note: {target}.md")
                with open(target_path, "a", encoding="utf-8") as f:
                    f.write(f"\n\n---\n{markdown}\n")
            else:
                print(f"    📄 Creating note: {target}.md")
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(markdown + "\n")

            archive_dest = os.path.join(ARCHIVE_FOLDER, filename)
            os.replace(file_path, archive_dest)
            print(f"    ✅ Finished. Moved {filename} to Archive/.")

        except Exception as e:
            print(f"[!] Failed to process {filename}: {e}")

if __name__ == "__main__":
    process_inbox()
