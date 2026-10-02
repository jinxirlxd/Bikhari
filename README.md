# Bikhari (v1.1.0)

**Bikhari** is an automated, multi-modal AI pipeline that converts long-form lecture audio (\.mp3\) and mixed-media Apple Notes (\.pdf\) into structured, hyperlinked Obsidian Markdown vaults.

---

## 🚀 What's New in v1.1.0
- **Multi-Modal Routing Engine:** Automated triage based on file extension dropped into \Inbox/\.
- **Apple Notes & Vision AI:** Slices exported note PDFs into high-res images and feeds them to Groq Vision models to interpret handwritten/screenshot diagrams.
- **Academic Expansion Schema:** Detects incomplete thoughts in biology and chemistry notes, fills in mechanisms, and appends cited standard clinical values.
- **Decoupled Architecture:** Routes audio through Deepgram Nova-3 and Vision/Text through Groq LPUs for near-zero cost processing.

---

## 🎯 Core Use Cases
1. **The Post-Class Brain Dump:** Drop lecture \.mp3\ recordings into \Inbox/\ for automatic transcription, summarization, and Obsidian linking.
2. **The Incomplete Notes Expander:** Export messy Apple Notes with screenshots as \.pdf\ into \Inbox/\. The Vision AI interprets diagrams, fills in reaction blanks, and creates a unified study guide.
3. **The Language Bridge:** Translate dense English medical and scientific lectures into your native language via injectable schema prompts while retaining clinical accuracy.
4. **The Zero-Budget Scholar:** Built entirely around generous free tiers (Deepgram's \ credit and Groq's free LPU access) to eliminate expensive monthly subscription walls.

---

## ⚙️ Usage
1. Place audio (\.mp3\) or exported Apple Notes (\.pdf\) into \Inbox/\.
2. Run your tier's compiler:
   - **Free Tier:** \python wiki_compiler_free.py\
   - **Developer Tier:** \python wiki_compiler_pro.py\
3. Collect your finished notes from \Medical Wiki/\.
