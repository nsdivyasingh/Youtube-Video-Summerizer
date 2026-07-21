# YouTube Video Summarizer

A Streamlit app that downloads YouTube audio, **transcribes it locally with Whisper**,
then summarizes the transcript with any text model on [OpenRouter](https://openrouter.ai).
No YouTube captions required (avoids caption API rate limits).

## Setup

1. Install dependencies (needs [ffmpeg](https://ffmpeg.org/) on your PATH for audio extract):
   ```
   pip install -r requirements.txt
   ```
2. Get an API key from [openrouter.ai/keys](https://openrouter.ai/keys).
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill it in:
   ```toml
   [general]
   OpenRouterAPIKey = "your-openrouter-api-key-here"
   # Optional summarize model
   # OpenRouterModel = "meta-llama/llama-3.3-70b-instruct"
   ```
4. Run the app:
   ```
   streamlit run app.py
   ```

The first transcription downloads the Whisper `base` model (~150MB) once.

`.streamlit/secrets.toml` is gitignored — never commit real API keys.

## How it works

1. `yt-dlp` downloads audio (up to 15 minutes)
2. Local **faster-whisper** produces a transcript
3. OpenRouter text model returns the summary

> OpenRouter audio/video models need account credits ($0.50–$1). This app uses local
> transcription so you only need OpenRouter for the text summary.

## Deploying for free

Vercel doesn't host long-running Streamlit servers, but these free hosts do:

- **[Streamlit Community Cloud](https://share.streamlit.io/)** — connect your GitHub repo,
  set `OpenRouterAPIKey` under app settings > Secrets in the same TOML format as above, deploy.
- **[Hugging Face Spaces](https://huggingface.co/spaces)** — create a Space with the
  Streamlit SDK, push this repo to it, and add `OpenRouterAPIKey` as a Space secret.
  (Whisper needs enough RAM; prefer a larger Space hardware tier if available.)
