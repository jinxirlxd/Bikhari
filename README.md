# Bhikhari (v2) — Autonomous Knowledge Base Ingestion Engine

Bhikhari is an automated document processing pipeline that converts unstructured study materials, textbooks, handouts, and medical notes into an interconnected Obsidian knowledge base. Utilizing multimodal vision models, the system autonomously extracts diagrams, standardizes handwritten or pre-filled worksheets into clean templates, and organizes notes into atomic Markdown files.

---

## Executive Summary & Architecture

Modern study and technical workflows generate significant unstructured document clutter. Bhikhari monitors incoming queues, applies visual extraction models, and synthesizes content directly into an organized personal wiki.

### Core Capabilities

* **Atomic Note Decomposition:** Breaks monolithic, multi-topic PDFs into discrete Markdown notes divided by topic or article title rather than arbitrarily by page count.
* **AI Smart Merge Engine:** Compares incoming material against existing vault files. New definitions, diagrams, and bullet points are woven into existing notes without creating duplicates (`Topic (1).md`) or overwriting prior entries.
* **Worksheet & Form Sanitation:** Strips out handwriting, checked checkboxes, and completed answers from scanned assignments, generating clean templates with blank inputs and tables for active recall study.
* **Multimodal Extraction & Diagram Linking:** Extracts raw figures, schemas, and diagrams into a structured archive directory and embeds them directly within relevant Obsidian notes (`![[filename.png]]`).
* **Dynamic Domain Routing:** Automatically sorts synthesized material into designated root folders: `Biology/`, `Chemistry/`, `Psychology/`, and `EMT/`.
* **Zero-Credential Codebase:** System credentials and API keys are isolated via local `.env` variables to prevent exposure in version control.

---

## Technical Workflow

1. **Queue Ingestion:** The `watchdog` daemon detects incoming files inside the `Inbox/` directory.
2. **Visual Chunking:** PyMuPDF renders pages at 100 DPI to remain well within vision model token limits while isolating embedded diagrams.
3. **Multimodal Transcription:** Groq vision endpoints (`qwen/qwen3.8-27b`) transcribe printed text, structural diagrams, and handwritten notes.
4. **Synthesis & Delimitation:** A master prompt parses transcriptions into standardized note boundaries tagged with `===FILE: Title===` and folder targets.
5. **Vault Integration:** Notes are created new or merged into existing files before source PDFs are moved to `Archive/`.

---

## Quickstart

1. **Install Dependencies:**
   ```powershell
   pip install pymupdf watchdog groq python-dotenv
   ```

2. **Configure Environment:**
   Add your API key to `.env` in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Start the Engine:**
   ```powershell
   python unified_compiler.py
   ```

---

## Philosophy & Origin: Why Bhikhari?

In Hindi (**भिखारी**) and Urdu (**بھکاری**), the word *Bhikhari* translates directly to a **beggar**—an individual possessing minimal personal resources, surviving on whatever materials they can gather.

Academic competition has steadily shifted into a pay-to-win model. Proprietary question banks, expensive tutoring services, commercial test-prep ecosystems, and clean digital study materials tilt competitive advantages toward well-funded students. Those working with second-hand handouts, poorly scanned PDFs, or low-cost equipment are left at a structural disadvantage.

**Bhikhari was built to eliminate that gap.**

The philosophy behind this engine is absolute accessibility. A student with nothing more than basic computer access and low-spec hardware can ingest scattered, messy, or low-yield documents and produce an interconnected, world-class personal knowledge engine.

Whether applied by a primary school student building early study habits, an undergraduate tackling complex pre-med STEM prerequisites, or an adult learner training for EMT certification, Bhikhari automates the labor of note synthesis—ensuring every student can build an elite academic knowledge base regardless of socioeconomic background.

---

## Directory Layout

```text
AJMHN/
├── Inbox/                  # Document ingestion queue
├── Medical Wiki/           # Obsidian Vault root
│   ├── Biology/            # Atomic biological concept notes
│   ├── Chemistry/          # Atomic chemical concept notes
│   ├── Psychology/         # Clinical psychology guides & worksheets
│   └── EMT/                # Emergency Medical Technician protocols
├── Archive/
│   ├── Attachments/        # Extracted diagrams and figures
│   └── *.pdf               # Archived source PDFs post-compilation
├── unified_compiler.py     # Ingestion engine and compilation logic
├── .env                    # Environment keys (ignored by git)
└── README.md
```