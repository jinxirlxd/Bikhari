# Bikhari

**Bikhari** is an automated, two-step AI agent designed to convert long-form lecture audio (`.mp3`) into structured, translated, and hyperlinked Obsidian Markdown notes.

## 🎯 Core Use Cases

### 1. The Post-Class Brain Dump
You just got back from a dense 90-minute lecture. Instead of spending hours re-listening to the recording and manually typing outlines, you just drop the `.mp3` from your phone or wearable recorder into the `Raw Transcripts` folder. By the time you make a coffee, Bikhari has converted the entire lecture into a beautifully structured, hyperlinked Obsidian wiki, complete with learning objectives and bolded key terms.

### 2. The Language Bridge (Automated Translation)
You are trying to learn a highly technical, difficult subject, but the best resources and lectures are only available in English. By adjusting a single line in the system prompt, Bikhari will transcribe the English audio and output the structured Obsidian notes entirely in your native language, preserving all the critical clinical and technical parameters accurately.

### 3. The Zero-Budget Scholar
You don't have the money to access expensive study materials, premium question banks, or elite tutoring. Bikhari levels the playing field by turning any free or recorded audio lecture into elite-tier study guides. It relies entirely on free or hyper-cheap API tiers so your budget never dictates your access to knowledge.

---

## 📖 The Lore & Mission
Global medical education is heavily gatekept. Between institutional nepotism, exorbitant costs, and structural violence, the barriers facing international medical students are immense. **Bikhari** was built to bypass these impasses.

By automating the transcription, translation, and structuring of raw academic audio, this tool ensures that institutional access and language barriers no longer dictate who gets to learn. We decouple the heavy processing to ensure the pipeline remains accessible to anyone, anywhere, regardless of their financial background.

---

## 🧠 The Architecture: Why Deepgram + Groq?
Passing 45-minute raw audio files directly to standard multimodal LLMs (like OpenAI, Google Gemini, or Claude) frequently results in `503 Server Busy` errors, instant rate-limit blocks, and massive API costs.

Bikhari bypasses audio compute bottlenecks and paywalls by decoupling the pipeline into two highly optimized, cost-effective steps:

1. **Extraction (Deepgram Nova-3):** Deepgram is an industry leader in ultra-fast, highly accurate speech-to-text, perfectly handling complex medical jargon. More importantly, **Deepgram provides `$200` in free API credits** upon sign-up, meaning you can transcribe hundreds of hours of audio without paying a dime.
2. **Structuring & Translation (Groq LPU):** The lightweight plain text transcript is then passed to Groq. Groq runs open-source models (like Llama 3.3) on LPUs (Language Processing Units) that generate text instantly. **Groq offers a massive free tier**, making the heavy formatting and translation step completely free. Even for batch processing entire semesters of classes, their developer tier costs literal fractions of a cent.

This two-step decoupled architecture is the absolute cheapest, fastest, and most reliable way to process massive audio files without relying on expensive monthly AI subscriptions.

---

## 🚀 Setup & Installation

1. **Clone the repository and install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure API Keys:**
   * Rename `.env.example` to `.env`.
   * Paste in your [Deepgram](https://console.deepgram.com/) and [Groq](https://console.groq.com/) API keys.
3. **Drop your `.mp3` lecture files into the `Raw Transcripts` folder.**

---

## ⚙️ Which Script Should I Run?

This repository provides two distinct scripts depending on your Groq account tier:

### 1. `wiki_compiler_free.py` (For Groq Free Tier)
Groq's free tier restricts tokens per minute (TPM). This script automatically splits massive transcripts into ~15,000-character chunks and paces requests with built-in cooldown timers to completely prevent rate limits.
```bash
python wiki_compiler_free.py
```

### 2. `wiki_compiler_pro.py` (For Groq Developer/Paid Tier)
If you have a developer tier or payment method attached to Groq, you have massive rate limits. This script sends entire 100,000+ character transcripts in a single shot for instant, un-chunked structuring.
```bash
python wiki_compiler_pro.py
```
