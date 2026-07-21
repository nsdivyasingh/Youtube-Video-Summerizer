# YouTube Video Summarizer

Paste a YouTube URL → the app downloads the audio, transcribes it with local Whisper,
then summarizes it with any text model on [OpenRouter](https://openrouter.ai).

No YouTube captions required.

**Repo:** [nsdivyasingh/Youtube-Video-Summerizer](https://github.com/nsdivyasingh/Youtube-Video-Summerizer)

---

## Local setup

1. Install [ffmpeg](https://ffmpeg.org/) and put it on your `PATH`.
2. Install Python deps:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy secrets and add your OpenRouter key:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   ```toml
   [general]
   OpenRouterAPIKey = "your-openrouter-api-key-here"
   # Optional
   # OpenRouterModel = "meta-llama/llama-3.3-70b-instruct"
   ```
4. Run:
   ```bash
   streamlit run app.py
   ```

Get a key at [openrouter.ai/keys](https://openrouter.ai/keys). Never commit `.streamlit/secrets.toml`.

---

## Deploy on Streamlit Community Cloud

The in-app **Deploy** button often fails for private repos or OneDrive paths. Deploy from the website instead:

1. Make sure `main` is on GitHub (already pushed to  
   `https://github.com/nsdivyasingh/Youtube-Video-Summerizer`).
2. Open [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
3. Click **New app** and choose:
   - **Repository:** `nsdivyasingh/Youtube-Video-Summerizer`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Under **Advanced settings → Secrets**, paste:
   ```toml
   [general]
   OpenRouterAPIKey = "your-openrouter-api-key-here"
   ```
5. Click **Deploy**.

If the repo does not appear in the list:

- Grant Streamlit access to the repo (GitHub → Settings → Applications → Streamlit), or
- Make the repo **Public** (GitHub → Settings → Danger zone → Change visibility).

`packages.txt` installs `ffmpeg` on Cloud. First run downloads the Whisper model and can take a few minutes.

---

## How it works

1. **yt-dlp** downloads audio (up to 15 minutes)
2. **faster-whisper** (`tiny`) transcribes locally
3. **OpenRouter** returns the summary

---

## Notes

- OpenRouter audio/video models need account credits; this app only uses OpenRouter for text summary.
- Free Cloud apps have limited RAM. If the app is killed during transcription, try a shorter video or run locally with a larger Whisper model.
