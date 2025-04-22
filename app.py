import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# Configure Google Generative AI API Key
api_key = st.secrets["APIKey"]  # Make sure to add the API key in Streamlit secrets
genai.configure(api_key=api_key)

# Function to fetch YouTube transcript
def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        st.error(f"Error fetching transcript: {str(e)}")
        return None

# Function to generate a summary using Google Generative AI
def summarize_text(text):
    try:
        response = genai.generate_text(
            model="gemini",  # Use the Gemini model for summarization
            prompt=f"Summarize the following text:\n\n{text}",
            max_output_tokens=300  # Adjust for the summary length
        )
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

# Streamlit UI
st.title("YouTube Video Summarizer")
st.write("Enter a YouTube video URL to get a summarized transcript.")

video_url = st.text_input("Enter YouTube Video URL")

if video_url:
    # Extracting video ID from the URL
    try:
        video_id = video_url.split("v=")[1].split("&")[0]
    except IndexError:
        st.error("Invalid URL format. Please ensure it's a valid YouTube video URL.")
        video_id = None

    if video_id:
        # Fetch transcript of the YouTube video
        transcript = get_youtube_transcript(video_id)

        if transcript:
            # Convert transcript into a single text block
            transcript_text = " ".join([item['text'] for item in transcript])

            # Generate the summary using Google Generative AI
            summary = summarize_text(transcript_text)

            if summary:
                st.subheader("Video Summary")
                st.write(summary)
            else:
                st.write("Could not generate a summary.")
        else:
            st.write("Could not retrieve transcript.")
