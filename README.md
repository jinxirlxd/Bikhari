# Bikhari (v1.2.0)

**Bikhari** is an automated, vault-aware, multi-modal AI pipeline that converts lecture audio (`.mp3`), mixed-media Apple Notes (`.pdf`), and miscellaneous text scraps (`.txt`, `.md`) into structured, interconnected Obsidian Markdown vaults.

---

## 🚀 Release History & Changelog

### v1.2.0 - Vault-Aware Routing & Smart Auto-Merge
- **Live Vault Indexing:** The router runs a pre-flight scan of `Medical Wiki/` on startup, compiling all existing note titles into a lightweight manifest.
- **Intelligent Auto-Merge:** Miscellaneous scraps, quick voice memos, and notes are semantically classified against your existing topics. If a scrap belongs to an existing subject (e.g., enzyme kinetics or renal clearance), Groq formats and appends it directly under an addendum header instead of creating redundant orphan notes.
- **Standalone Topic Fallback:** If a snippet does not match any existing topic, the router automatically generates a clean, standalone note.
- **Expanded Ingestion:** Added native support for `.txt` and `.md` scrap ingestion alongside `.pdf` and `.mp3`.
- **Automated Archiving:** Processed files are automatically relocated from `Inbox/` to `Archive/` to keep your intake queue clean and prevent duplicate runs.

### v1.1.0 - Vision AI & Mixed-Media Apple Notes
- **Vision AI Ingestion:** Integrated PyMuPDF rendering to slice Apple Notes PDFs into high-resolution images for Groq Vision models (`llama-3.2-90b-vision-preview`).
- **Academic Expansion Schema:** Detects missing biochemical mechanisms and incomplete thoughts, autocompletes reactions, and appends cited standard clinical values.
- **Multi-Modal Inbox Router:** Replaced single-script audio processing with an automated file-type routing engine.

### v1.0.0 - Initial Release
- Two-stage decoupled pipeline using Deepgram Nova-3 for speech extraction and Groq LPUs for rapid Markdown structuring.

---

## 🎯 Core Use Cases

### 1. The Miscellaneous Scrap Sorter (v1.2.0)
You have a quick 2-sentence note, a lab value reference, or a brief clinical pearl. Instead of figuring out where to file it, drop the `.txt`, `.md`, or short voice memo into `Inbox/`. Bikhari scans your existing vault, locates the matching parent topic, formats the insight with `[[Wikilinks]]`, and appends it to the bottom of the existing note.

### 2. The Incomplete Notes Expander (Vision AI)
Export messy Apple Notes containing text, blanks, and screenshot diagrams as a `.pdf` into `Inbox/`. The Vision AI reads the images, decodes molecular pathways, fills in missing blanks, and synthesizes a unified study guide.

### 3. The Post-Class Brain Dump
Drop raw lecture recordings (`.mp3`) into `Inbox/`. Deepgram transcribes the audio, and Groq formats it with extracted learning objectives, bolded terms, and Obsidian links.

### 4. The Language Bridge
Translate complex English scientific lectures into your target language on the fly by customizing the schema prompt while preserving global clinical nomenclature.

### 5. The Zero-Budget Scholar
Decoupled architecture built around Deepgram's $200 free credit and Groq's high-speed free tier, avoiding expensive AI subscriptions.

---

## ⚙️ Usage

1. Place your files (`.mp3`, `.pdf`, `.txt`, `.md`) into `Inbox/`.
2. Run your compiler:
   - **Developer Tier:** `python wiki_compiler_pro.py`
   - **Free Tier:** `python wiki_compiler_free.py`
3. Formatted notes appear in `Medical Wiki/`, and processed originals are moved to `Archive/`.
