# YouTube Video Summarizer

A Streamlit app that fetches a YouTube video's transcript and summarizes it using an
open-source LLM (Llama 3.3 70B) served free via [Groq](https://groq.com).

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Get a free API key from [console.groq.com/keys](https://console.groq.com/keys).
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in your key:
   ```toml
   [general]
   GroqAPIKey = "your-groq-api-key-here"
   ```
4. Run the app:
   ```
   streamlit run app.py
   ```

`.streamlit/secrets.toml` is gitignored — never commit real API keys.

## Deploying for free

Vercel doesn't host long-running Streamlit servers, but these free hosts do:

- **[Streamlit Community Cloud](https://share.streamlit.io/)** — connect your GitHub repo,
  set `GroqAPIKey` under app settings > Secrets in the same TOML format as above, deploy.
- **[Hugging Face Spaces](https://huggingface.co/spaces)** — create a Space with the
  Streamlit SDK, push this repo to it, and add `GroqAPIKey` as a Space secret.
