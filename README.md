# Bikhari 

**Bikhari** is an automated, two-step AI agent designed to convert long-form lecture audio (.mp3) into structured, translated, and hyperlinked Obsidian Markdown notes. 

## 📖 The Lore & Mission
Global medical education is heavily gatekept. Between institutional nepotism, exorbitant costs, and structural violence, the barriers facing international medical students are immense. **Bikhari** was built to bypass these impasses. 

By automating the transcription, translation, and structuring of raw academic audio, this tool ensures that institutional access and language barriers no longer dictate who gets to learn. Any English medical lecture can be instantly transcribed, translated into a native language, and output as a clean, highly readable PKM (Personal Knowledge Management) vault.

## 🧠 The Architecture
1. **Extraction (Deepgram Nova-3):** A specialized speech-to-text model extracts the audio into a .txt file in seconds.
2. **Structuring & Translation (Groq LPU):** The lightweight plain text is passed to Groq to instantly generate Obsidian-ready markdown, handling complex medical terminology and translation with zero capacity issues.

## 🚀 Setup & Installation
1. Clone the repository and run: pip install -r requirements.txt
2. Rename .env.example to .env and paste your Deepgram and Groq API keys.
3. Drop your .mp3 lecture files into the Raw Transcripts folder.
4. Run python wiki_compiler_pro.py (Developer/Paid Tier) OR python wiki_compiler_free.py (Free Tier).
