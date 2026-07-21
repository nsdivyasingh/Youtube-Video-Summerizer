import re
import shutil
import tempfile
from pathlib import Path

import streamlit as st
from faster_whisper import WhisperModel
from openai import OpenAI
from yt_dlp.utils import download_range_func

DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MAX_TRANSCRIPT_CHARS = 60_000
# Keep downloads short enough for local Whisper on CPU
MAX_AUDIO_SECONDS = 15 * 60
WHISPER_MODEL_SIZE = "base"

VIDEO_ID_PATTERNS = [
    r"(?:v=|\/shorts\/|\/embed\/|youtu\.be\/)([A-Za-z0-9_-]{11})",
]


def extract_video_id(url: str) -> str | None:
    for pattern in VIDEO_ID_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


@st.cache_resource(show_spinner=False)
def load_whisper(model_size: str = WHISPER_MODEL_SIZE) -> WhisperModel:
    return WhisperModel(model_size, device="cpu", compute_type="int8")


def download_audio(watch_url: str, out_dir: Path) -> Path:
    """Download audio from YouTube as mp3 (truncated to MAX_AUDIO_SECONDS)."""
    import yt_dlp

    out_tmpl = str(out_dir / "%(id)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_tmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "64",
            }
        ],
        # Limit length so Whisper stays fast on CPU
        "download_ranges": download_range_func(None, [(0, MAX_AUDIO_SECONDS)]),
        "force_keyframes_at_cuts": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(watch_url, download=True)
        video_id = info["id"]

    mp3_path = out_dir / f"{video_id}.mp3"
    if not mp3_path.exists():
        # Fallback: pick any audio file yt-dlp wrote
        candidates = list(out_dir.glob(f"{video_id}.*"))
        if not candidates:
            raise FileNotFoundError("Audio download failed — no file was written.")
        mp3_path = candidates[0]
    return mp3_path


def transcribe_audio(audio_path: Path) -> tuple[str, str]:
    """Return (transcript_text, detected_language) using local Whisper."""
    model = load_whisper()
    segments, info = model.transcribe(str(audio_path), beam_size=1)
    text = " ".join(segment.text.strip() for segment in segments).strip()
    return text, info.language or "unknown"


def summarize_text(client: OpenAI, model: str, text: str) -> str:
    if len(text) > MAX_TRANSCRIPT_CHARS:
        text = text[:MAX_TRANSCRIPT_CHARS]
    prompt = (
        "Summarize the following YouTube video transcript. "
        "Use a short paragraph followed by bullet points for the key takeaways:\n\n"
        f"{text}"
    )
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content


st.title("YouTube Video Summarizer")
st.write(
    "Paste a YouTube URL. Audio is transcribed locally (Whisper), then summarized "
    "with your OpenRouter model — no YouTube captions required."
)

with st.sidebar:
    st.header("Settings")
    secret_key = st.secrets.get("general", {}).get("OpenRouterAPIKey", "")
    if secret_key and secret_key != "your-openrouter-api-key-here":
        api_key = secret_key
        st.caption("API key loaded from secrets.")
    else:
        api_key = st.text_input(
            "OpenRouter API key",
            type="password",
            help="Get a key at https://openrouter.ai/keys — stored only for this session.",
        )
    model = st.text_input(
        "Summarize model",
        value=st.secrets.get("general", {}).get("OpenRouterModel", DEFAULT_MODEL),
        help="Any OpenRouter text model, e.g. meta-llama/llama-3.3-70b-instruct",
    )
    st.caption(f"Transcription: local Whisper ({WHISPER_MODEL_SIZE})")

if not api_key or api_key == "your-openrouter-api-key-here":
    st.error(
        "Add an OpenRouter API key in the sidebar, or set OpenRouterAPIKey in "
        ".streamlit/secrets.toml (see secrets.toml.example)."
    )
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url=OPENROUTER_BASE_URL,
    default_headers={
        "HTTP-Referer": "https://github.com/navee/Youtube-Video-Summerizer",
        "X-Title": "YouTube Video Summarizer",
    },
)

video_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")

if video_url:
    video_id = extract_video_id(video_url)

    if not video_id:
        st.error("Couldn't find a video ID in that URL. Paste a standard YouTube link.")
    else:
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        st.video(watch_url)

        tmp_dir = Path(tempfile.mkdtemp(prefix="yt_sum_"))
        try:
            with st.spinner("Downloading audio..."):
                audio_path = download_audio(watch_url, tmp_dir)

            with st.spinner("Transcribing with local Whisper (first run downloads the model)..."):
                transcript_text, language_code = transcribe_audio(audio_path)

            if not transcript_text:
                st.error("Whisper produced an empty transcript for this audio.")
            else:
                st.caption(f"Detected language: {language_code}")
                with st.spinner("Generating summary via OpenRouter..."):
                    try:
                        summary = summarize_text(client, model, transcript_text)
                    except Exception as e:
                        st.error(f"Error generating summary: {e}")
                    else:
                        st.subheader("Summary")
                        st.write(summary)
                        with st.expander("Full transcript"):
                            st.write(transcript_text)
        except Exception as e:
            st.error(f"Error processing video: {e}")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
