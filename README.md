# Bikhari (v1.3.0)

**Bikhari** is an automated, vault-aware, multi-modal AI pipeline that converts lecture audio (`.mp3`), mixed-media Apple Notes (`.pdf`), and miscellaneous text scraps (`.txt`, `.md`) into structured, interconnected Obsidian Markdown vaults.

---

## 🚀 Release History & Changelog

### v1.3.0 — Recursive Vault Hierarchy & File Stream Lifecycle Fixes
- **Recursive Subfolder Indexing:** Scans the entire directory tree inside `Medical Wiki/` using `os.walk`. Organizes notes into arbitrary nested folders (e.g., `Medical Wiki/Biology/`, `Medical Wiki/Chemistry/`) without breaking global link resolution or scrap routing.
- **Nested Append Routing:** Scraps matching an existing topic placed inside subfolders are identified from a global manifest map and appended directly to their nested file path.
- **Stream Lifecycle Management:** Implemented context manager scoping (`with pymupdf.open(...)`) to eliminate Windows OS file locks (`WinError 32`) when archiving processed documents.
- **Dual-Layer PDF Extraction:** Slices and dispatches digital text directly to avoid image-payload limits on multi-page files, reserving Vision AI purely for image scans and diagrams.

### v1.2.0 — Vault-Aware Routing & Smart Auto-Merge
- **Live Vault Indexing:** The router runs a pre-flight scan of `Medical Wiki/` on startup, compiling all existing note titles into a lightweight manifest.
- **Intelligent Auto-Merge:** Miscellaneous scraps, quick voice memos, and notes are semantically classified against existing topics. If a scrap belongs to an existing subject, Groq formats and appends it directly under an addendum header.
- **Standalone Topic Fallback:** If a snippet does not match any existing topic, the router automatically generates a clean, standalone note.
- **Expanded Ingestion:** Added native support for `.txt` and `.md` scrap ingestion alongside `.pdf` and `.mp3`.
- **Automated Archiving:** Processed files are automatically relocated from `Inbox/` to `Archive/` to maintain a clean queue.

### v1.1.0 — Vision AI & Mixed-Media Apple Notes
- **Vision AI Ingestion:** Integrated PyMuPDF rendering to slice Apple Notes PDFs into high-resolution images for Groq Vision models.
- **Academic Expansion Schema:** Detects missing biochemical mechanisms and incomplete thoughts, autocompletes reactions, and appends cited standard clinical values.
- **Multi-Modal Inbox Router:** Replaced single-script audio processing with an automated file-type routing engine.

### v1.0.0 — Initial Release
- Two-stage decoupled pipeline using Deepgram Nova-3 for speech extraction and Groq LPUs for rapid Markdown structuring.

---

## 🎯 Core Use Cases

### 1. Flexible Vault Hierarchy (v1.3.0)
Organize your Obsidian vault however you want. Move notes into categorized folders like `Medical Wiki/Biology/` or `Medical Wiki/Biochemistry/`. The pipeline traverses all nested folders, maintains knowledge graph connectivity, and routes additions directly to the nested files.

### 2. The Miscellaneous Scrap Sorter
Drop a `.txt`, `.md`, or short voice memo into `Inbox/`. Bikhari indexes the entire vault, identifies the parent topic regardless of subfolder location, formats the insight with `[[Wikilinks]]`, and appends it to the matching note.

### 3. The Incomplete Notes Expander
Export messy Apple Notes containing text, blanks, and screenshot diagrams as a `.pdf` into `Inbox/`. Bikhari extracts the text, decodes diagrams, fills in missing blanks, and synthesizes a unified study guide.

### 4. The Post-Class Brain Dump
Drop raw lecture recordings (`.mp3`) into `Inbox/`. Deepgram transcribes the audio, and Groq formats it with extracted learning objectives, bolded terms, and Obsidian links.

---

## ⚙️ Usage

1. Place your incoming files (`.mp3`, `.pdf`, `.txt`, `.md`) into `Inbox/`.
2. Run your compiler:
   - **Developer Tier:** `python wiki_compiler_pro.py`
   - **Free Tier:** `python wiki_compiler_free.py`
3. Completed notes will appear or update inside `Medical Wiki/` (including subfolders), and original input files are moved to `Archive/`.
