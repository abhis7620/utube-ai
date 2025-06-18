import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from dotenv import load_dotenv
import openai
import google.generativeai as genai
import os
import re

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini 1.5 Flash Model
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Streamlit app config
st.set_page_config(page_title="YouTube AI Assistant", layout="centered")
st.title("🎬 YouTube Transcript Summary + Q&A")

# Helper: Extract YouTube Video ID
def extract_video_id(url_or_id):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url_or_id)
    return match.group(1) if match else url_or_id.strip()

youtube_input = st.text_input("📺 Enter YouTube URL or Video ID:")

if youtube_input:
    video_id = extract_video_id(youtube_input)
    st.write(f"🔍 Video ID Detected: `{video_id}`")

    # Display the video thumbnail
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    st.image(thumbnail_url, caption="🎞️ Video Thumbnail", use_column_width=True)


    try:
        # Get transcript using YouTubeTranscriptAPI
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        transcript = " ".join(chunk["text"] for chunk in transcript_list)

        # Save transcript to file (no display)
        with open("transcription.txt", "w", encoding="utf-8") as f:
            f.write(transcript)
        st.success("✅ Transcript saved successfully!")

        # Summarize using Gemini
        if st.button("🧠 Summarize using Gemini 1.5 Flash"):
            with st.spinner("Generating summary..."):
                with open("transcription.txt", "r", encoding="utf-8") as f:
                    content = f.read()

                prompt = (
                    "Summarize the following YouTube transcript in about 300 to 350 words as bullet points:\n\n"
                    + content
                )
                response = gemini_model.generate_content(prompt)
                st.subheader("📄 Summary (in Points):")
                st.markdown(response.text)

        # Ask a Question about the transcript
        st.subheader("💬 Ask a Question about the Video:")
        user_question = st.text_input("Type your question:")

        if user_question:
            with open("transcription.txt", "r", encoding="utf-8") as f:
                context = f.read()

            chat_prompt = (
                f"Answer the question based only on the following YouTube transcript:\n\n{context}\n\n"
                f"Question: {user_question}\n\nAnswer:"
            )

            with st.spinner("Thinking..."):
                qa_response = gemini_model.generate_content(chat_prompt)
                st.markdown("🧠 **Answer:**")
                st.markdown(qa_response.text)

    except TranscriptsDisabled:
        st.error("❌ Captions are disabled for this video.")
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
