# Bhikhari (v2) — Autonomous Knowledge Base Ingestion Engine

Bhikhari is an automated ingestion pipeline that continuously monitors multi-format documents, processes them via multimodal vision models, and compiles them into a structured, modular Obsidian knowledge base. It eliminates manual note-taking by decomposing composite documents into discrete, atomic notes and synthesizing them into a clean, searchable wiki.

---

## What's New in v2

* **Atomic Note Decomposition (`===FILE===` Splitting):**
  * Breaks composite documents, multi-topic articles, and long chapters into standalone, modular Markdown files based on conceptual boundaries and titles rather than raw page dumps.
* **AI Smart Merge Engine:**
  * Prevents file collisions and duplicate notes (`Topic (1).md`). When an incoming concept matches an existing note, the LLM reads the current note and seamlessly integrates new points, definitions, and figures without overwriting prior content.
* **Automated Worksheet & Form Sanitation:**
  * Strips out pre-filled handwriting, checked boxes, and annotations from forms, recreating pristine blank fields, checkboxes, and tables for repeated interactive study and reuse.
* **Multimodal Extraction & Diagram Linking:**
  * Uses lightweight visual chunking (100 DPI rendering) paired with Groq Vision models to capture embedded figures, schemas, tables, and notations.
  * Extracted figure assets are cataloged and routed to an archive repository to keep primary vault folders uncluttered.
* **Dynamic Categorization & Routing:**
  * Categorizes incoming content dynamically into designated knowledge directories and assigns frontmatter metadata (`tags`, `source`, `date_compiled`).
* **Real-Time Directory Watcher:**
  * Operates on an event-driven `watchdog` daemon that processes files immediately upon landing in the ingestion queue.
* **Environment-Isolated Secrets:**
  * Authentication keys and tokens are loaded strictly via `.env` to prevent credential exposure in source control.

---

## Directory Architecture

```text
AJMHN/
├── Inbox/                  # Drop incoming files and documents here
├── Medical Wiki/           # Primary Knowledge Vault root
│   ├── Biology/            # Domain directory
│   ├── Chemistry/          # Domain directory
│   ├── Psychology/         # Domain directory
│   └── EMT/                # Domain directory
├── Archive/
│   ├── Attachments/        # Extracted diagrams, figures, and images
│   └── *.pdf               # Archived source documents post-compilation
├── unified_compiler.py     # Ingestion engine and compilation logic
├── .env                    # Environment keys (ignored by git)
└── README.md