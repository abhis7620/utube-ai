import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from dotenv import load_dotenv
import openai
import google.generativeai as genai
import os
import re

# Load API keys from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini Flash Model
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Streamlit setup
st.set_page_config(page_title="YouTube Transcript & Gemini Summary", layout="centered")
st.title("🎬 YouTube Summary Generator")

# Helper: Extract YouTube video ID
def extract_video_id(url_or_id):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url_or_id)
    return match.group(1) if match else url_or_id.strip()

# Input field
youtube_input = st.text_input("📺 Enter YouTube URL or ID:")

if youtube_input:
    video_id = extract_video_id(youtube_input)
    st.write(f"🔍 Video ID Detected: `{video_id}`")

    try:
        # Get transcript using YouTubeTranscriptAPI
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        transcript = " ".join(chunk["text"] for chunk in transcript_list)

        # Save transcript to file (not shown in UI)
        with open("transcription.txt", "w", encoding="utf-8") as f:
            f.write(transcript)
        st.success("✅ Transcript saved to `transcription.txt`")

        # Button to summarize with Gemini
        if st.button("🧠 Summarize using Gemini 1.5 Flash"):
            with st.spinner("Summarizing transcript using Gemini..."):
                try:
                    with open("transcription.txt", "r", encoding="utf-8") as f:
                        content = f.read()

                    prompt = (
                        "Summarize the following YouTube transcript in approximately 300 to 350 words. "
                        "Present the summary as clear and concise bullet points:\n\n" + content
                    )

                    gemini_response = gemini_model.generate_content(prompt)
                    st.subheader("📄 Summary (in Points):")
                    st.markdown(gemini_response.text)  # renders bullets properly
                except Exception as e:
                    st.error(f"⚠️ Gemini Error: {e}")

    except TranscriptsDisabled:
        st.error("❌ No captions available for this video.")
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
