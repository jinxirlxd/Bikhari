import os
import time
import shutil
import base64
import re
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from groq import Groq
import pymupdf
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Silence internal C-level warnings
pymupdf.TOOLS.mupdf_display_errors(False)

# Initialize Groq client securely using the loaded .env key
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BASE_DIR = Path("C:/Users/Hari/Desktop/AJMHN")
INBOX_DIR = BASE_DIR / "Inbox"
WIKI_DIR = BASE_DIR / "Medical Wiki"
ARCHIVE_DIR = BASE_DIR / "Archive"

EMT_DIR = WIKI_DIR / "EMT"
PSYCH_DIR = WIKI_DIR / "Psychology"
BIO_DIR = WIKI_DIR / "Biology"
CHEM_DIR = WIKI_DIR / "Chemistry"

ATTACHMENTS_DIR = ARCHIVE_DIR / "Attachments"

for d in [INBOX_DIR, WIKI_DIR, ARCHIVE_DIR, EMT_DIR, PSYCH_DIR, BIO_DIR, CHEM_DIR, ATTACHMENTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

PAGE_PROMPT = """You are transcribing a page of a medical/educational document.
Read all visual elements, printed text, diagrams, and handwriting.
Instructions:
- If this page is an interactive worksheet, exercise, or questionnaire: OMIT ALL PRE-FILLED ANSWERS. Recreate blank fields.
- Transcribe all clinical concepts, definitions, articles, and guides accurately.
Output only the transcribed markdown content for this single page."""

MASTER_SYNTHESIS_PROMPT = """You are a clinical knowledge architect structuring notes for an Obsidian vault.
You will receive transcribed content from multiple pages of a document and a list of extracted figure attachments.

Rules for Organization & Atomic Splitting:
1. ATOMIC SPLIT BY CONCEPT & TITLE: 
   - For Biology and Chemistry: Split the text into separate notes by specific SCIENTIFIC CONCEPT (e.g., separate "Photosynthesis" from "Cellular Respiration" into two distinct notes, even if they are in the same chapter). Do not name files "Chapter 1".
   - For Psychology and EMT: Split the text strictly by the TITLE of the article, worksheet, or tool (e.g., if "I Feel Statements" and "Conflict Resolution" are in the same document, split them into two distinct notes).
2. FILE DELIMITER: For EACH separate note, you MUST begin with this exact header format:
   ===FILE: <Specific Concept or Article Title>===
   CATEGORY: <Must be exactly one of: EMT, Psychology, Biology, or Chemistry>

3. CONTENT FORMAT:
   - Begin the body with a clean `# Title`.
   - Embed relevant figures using `![[filename.png]]` where they belong.
   - For Worksheets: keep questions blank for reuse.

Example format:
===FILE: Conflict Resolution Strategies===
CATEGORY: Psychology
# Conflict Resolution Strategies
...

===FILE: Glycolysis Phase 1===
CATEGORY: Biology
# Glycolysis Phase 1
..."""

def clean_markdown_blocks(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"): lines = lines[1:]
        if lines and lines[-1].startswith("```"): lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text

def extract_figures_and_pages(pdf_path, note_slug):
    doc = pymupdf.open(str(pdf_path))
    page_images_b64 = []
    saved_figures = []
    fig_idx = 1

    for page_num in range(len(doc)):
        page = doc[page_num]
        try:
            image_list = page.get_images(full=True)
            for img in image_list:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                ext = base_image["ext"]

                if len(image_bytes) > 6000 and base_image.get("width", 0) > 100:
                    fig_name = f"{note_slug}_fig{fig_idx}.{ext}"
                    out_path = ATTACHMENTS_DIR / fig_name
                    with open(out_path, "wb") as f:
                        f.write(image_bytes)
                    saved_figures.append(fig_name)
                    fig_idx += 1
        except Exception:
            pass

        pix = page.get_pixmap(dpi=100)
        jpeg_bytes = pix.tobytes("jpeg", jpg_quality=75)
        b64 = base64.b64encode(jpeg_bytes).decode("utf-8")
        page_images_b64.append(b64)

    doc.close()
    return page_images_b64, saved_figures

def merge_with_existing_note(existing_text, new_text):
    """Sends the old note and new content to Groq to intelligently stitch them together."""
    merge_prompt = """You are a clinical knowledge editor. You are given an EXISTING Obsidian note and NEW CONTENT. 
    Your job is to seamlessly integrate the NEW CONTENT into the EXISTING note. 
    - Do NOT delete any existing information. 
    - Keep the frontmatter (the YAML block at the top between the --- lines) exactly intact.
    - Avoid duplicating headers or concepts; weave the new details into the existing sections where they make sense, or add new sections if needed.
    - Output ONLY the finalized markdown. Do not wrap in ```markdown code blocks."""
    
    response = groq_client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {"role": "system", "content": merge_prompt},
            {"role": "user", "content": f"EXISTING NOTE:\n{existing_text}\n\nNEW CONTENT:\n{new_text}"}
        ],
        temperature=0.1,
        max_tokens=8192
    )
    return clean_markdown_blocks(response.choices[0].message.content)

def process_file_with_groq(file_path):
    note_slug = re.sub(r"[^\w\-_\. ]", "_", file_path.stem)
    print(f"[*] Parsing {file_path.name} into chunks...")

    page_b64_list, figures = extract_figures_and_pages(file_path, note_slug)
    print(f"[+] Extracted {len(page_b64_list)} page chunk(s) and {len(figures)} figure(s).")

    transcribed_pages = []
    for idx, img_b64 in enumerate(page_b64_list, start=1):
        print(f"[*] Transcribing page {idx}/{len(page_b64_list)} via Groq Vision...")
        response = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": PAGE_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]}
            ],
            temperature=0.1,
            max_tokens=2048
        )
        transcribed_pages.append(f"--- PAGE {idx} ---\n" + response.choices[0].message.content)
        time.sleep(1)

    full_transcription = "\n\n".join(transcribed_pages)
    figures_manifest = "\n".join(f"- {f}" for f in figures) if figures else "None"

    print(f"[*] Synthesizing atomic Obsidian notes via Groq...")
    synthesis_input = (
        f"EXTRACTED ATTACHMENTS:\n{figures_manifest}\n\n"
        f"DOCUMENT TRANSCRIPTION:\n{full_transcription}"
    )

    synthesis_response = groq_client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {"role": "system", "content": MASTER_SYNTHESIS_PROMPT},
            {"role": "user", "content": synthesis_input}
        ],
        temperature=0.1,
        max_tokens=8192
    )

    content = clean_markdown_blocks(synthesis_response.choices[0].message.content)
    file_chunks = re.split(r"===FILE:\s*", content)
    generated_notes = []

    for chunk in file_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        
        lines = chunk.splitlines()
        filename = lines[0].strip()
        filename = re.sub(r'[\\/*?:"<>|]', "", filename)
        
        category = "Psychology" # default
        body_lines = []
        for line in lines[1:]:
            if re.match(r"^CATEGORY:", line, re.IGNORECASE):
                cat_text = line.split(":", 1)[1].strip().lower()
                if "emt" in cat_text: category = "EMT"
                elif "psych" in cat_text: category = "Psychology"
                elif "bio" in cat_text: category = "Biology"
                elif "chem" in cat_text: category = "Chemistry"
            else:
                body_lines.append(line)

        generated_notes.append({
            "title": filename,
            "category": category,
            "markdown": "\n".join(body_lines).strip()
        })

    return generated_notes

def process_file(file_path):
    file_path = Path(file_path)
    if not file_path.exists() or file_path.name.startswith("."):
        return

    print(f"\n[>] Processing: {file_path.name}")
    try:
        time.sleep(1)
        if file_path.suffix.lower() != ".pdf":
            return

        notes = process_file_with_groq(file_path)

        for note in notes:
            cat = note["category"]
            title = note["title"]
            body = note["markdown"]

            if cat == "EMT": target_dir = EMT_DIR
            elif cat == "Biology": target_dir = BIO_DIR
            elif cat == "Chemistry": target_dir = CHEM_DIR
            else: target_dir = PSYCH_DIR

            out_note = target_dir / f"{title}.md"
            date_str = time.strftime("%Y-%m-%d")

            # SMART MERGE CHECK
            if out_note.exists():
                print(f"    [~] '{title}.md' already exists! Running AI Smart Merge...")
                with open(out_note, "r", encoding="utf-8") as f:
                    existing_content = f.read()
                
                final_body = merge_with_existing_note(existing_content, body)
                
                with open(out_note, "w", encoding="utf-8") as f:
                    f.write(final_body + "\n")
                print(f"    [+] Successfully updated: {target_dir.name}/{out_note.name}")
            else:
                metadata_header = (
                    f"---\n"
                    f"type: {cat.lower()}\n"
                    f"source: \"{file_path.name}\"\n"
                    f"date_compiled: {date_str}\n"
                    f"tags: [{cat.lower()}]\n"
                    f"---\n\n"
                )

                with open(out_note, "w", encoding="utf-8") as f:
                    f.write(metadata_header + body + "\n")

                print(f"    [+] Created new note: {target_dir.name}/{out_note.name}")

        shutil.move(str(file_path), str(ARCHIVE_DIR / file_path.name))
        print(f"[+] Moved {file_path.name} to Archive")

    except Exception as e:
        print(f"[!] Error processing {file_path.name}: {e}")

class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            process_file(event.src_path)

if __name__ == "__main__":
    print(f"Groq Visual Chunking Compiler active. Watching {INBOX_DIR}...")
    existing = sorted(list(INBOX_DIR.glob("*.pdf")))
    if existing:
        print(f"Found {len(existing)} backlogged file(s). Processing batch queue now...")
        for pdf in existing:
            process_file(pdf)

    observer = Observer()
    observer.schedule(InboxHandler(), str(INBOX_DIR), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()