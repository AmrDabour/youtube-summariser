import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from transformers import pipeline

def extract_video_id(url_or_id: str) -> str:
    if url_or_id.startswith("http"):
        parsed = urlparse(url_or_id)
        qs = parse_qs(parsed.query)
        video_ids = qs.get('v')
        if video_ids:
            return video_ids[0]
        if 'youtu.be' in parsed.netloc:
            return parsed.path.lstrip('/')
    return url_or_id

def split_text_into_chunks(text: str, chunk_size: int):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

st.title("YouTube Summariser")
url = st.text_input("YouTube URL or video id")
if st.button("Summarize") and url:
    vid = extract_video_id(url)
    try:
        fetched = YouTubeTranscriptApi.get_transcript(vid, languages=['en'])
        text = " ".join(item['text'] for item in fetched)
        chunks = split_text_into_chunks(text, chunk_size=2000)
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summaries = []
        for chunk in chunks:
            summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        final_summary = "\n\n".join(summaries)
        st.subheader("Summary")
        st.write(final_summary)
        with st.expander("Transcript"):
            st.write(text)
    except Exception as e:
        st.error(f"Error: {e}")
