import re

import streamlit as st
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_TRANSCRIPT_CHARS = 60_000  # keeps well within the free-tier token budget

VIDEO_ID_PATTERNS = [
    r"(?:v=|\/shorts\/|\/embed\/|youtu\.be\/)([A-Za-z0-9_-]{11})",
]


def extract_video_id(url: str) -> str | None:
    for pattern in VIDEO_ID_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


@st.cache_data(show_spinner=False)
def fetch_transcript(video_id: str) -> str:
    ytt_api = YouTubeTranscriptApi()
    fetched = ytt_api.fetch(video_id)
    return " ".join(snippet.text for snippet in fetched)


def summarize_text(client: Groq, text: str) -> str:
    if len(text) > MAX_TRANSCRIPT_CHARS:
        text = text[:MAX_TRANSCRIPT_CHARS]
    prompt = (
        "Summarize the following YouTube video transcript. "
        "Use a short paragraph followed by bullet points for the key takeaways:\n\n"
        f"{text}"
    )
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content


st.title("YouTube Video Summarizer")
st.write("Enter a YouTube video URL to get an AI-generated summary of its transcript.")

api_key = st.secrets.get("general", {}).get("GroqAPIKey")
if not api_key:
    st.error("No Groq API key found. Add one to .streamlit/secrets.toml (see secrets.toml.example).")
    st.stop()
client = Groq(api_key=api_key)

video_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")

if video_url:
    video_id = extract_video_id(video_url)

    if not video_id:
        st.error("Couldn't find a video ID in that URL. Paste a standard YouTube link.")
    else:
        st.video(f"https://www.youtube.com/watch?v={video_id}")

        try:
            with st.spinner("Fetching transcript..."):
                transcript_text = fetch_transcript(video_id)
        except TranscriptsDisabled:
            st.error("Transcripts are disabled for this video.")
        except NoTranscriptFound:
            st.error("No transcript is available for this video.")
        except VideoUnavailable:
            st.error("This video is unavailable.")
        except Exception as e:
            st.error(f"Error fetching transcript: {e}")
        else:
            with st.spinner("Generating summary..."):
                try:
                    summary = summarize_text(client, transcript_text)
                except Exception as e:
                    st.error(f"Error generating summary: {e}")
                else:
                    st.subheader("Summary")
                    st.write(summary)

                    with st.expander("Full transcript"):
                        st.write(transcript_text)
