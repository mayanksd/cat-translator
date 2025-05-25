# main.py
# Streamlit frontend: captures mic audio, sends to Flask backend, and shows translated output

import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av
import numpy as np
import requests
import tempfile
import wave

# Custom audio processor to capture mic input
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recorded_frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # 🔁 Update session log
        if 'log' not in st.session_state:
            st.session_state.log = []
        st.session_state.log.append("🎙️ Frame received")

        # 📟 Terminal log
        print("📥 Received an audio frame")

        try:
            audio = frame.to_ndarray()
            print(f"✅ Audio shape: {audio.shape}, dtype: {audio.dtype}")
            st.session_state.log.append(f"🎧 Audio received — shape: {audio.shape}, dtype: {audio.dtype}")
            self.recorded_frames.append(audio)
        except Exception as e:
            print(f"❌ Error converting frame: {e}")
            st.session_state.log.append(f"❌ Error: {e}")
            st.error(f"Failed to process audio frame: {e}")

        return frame


    def get_wav_bytes(self, sample_rate=48000):
        if not self.recorded_frames:
            return None
        audio_data = np.concatenate(self.recorded_frames, axis=1)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            with wave.open(tmpfile.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
            return tmpfile.name

# UI setup
st.set_page_config(page_title="Cat Translator", layout="centered")
st.title("🐾 Cat Translator (Live MVP)")
st.markdown("Click 'Start' to let your cat speak!")

# Launch mic stream
ctx = webrtc_streamer(
    key="cat-translator",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=1024,
    media_stream_constraints={"audio": True, "video": False},
    audio_processor_factory=AudioProcessor,
    async_processing=True,
)

# Process after mic is stopped
if ctx.state.playing is False and ctx.audio_receiver:
    st.info("Processing cat's voice...")

    audio_path = ctx.audio_processor.get_wav_bytes()
    if audio_path:
        with open(audio_path, "rb") as f:
            files = {"file": f}
            try:
                response = requests.post("http://localhost:8506/translate", files=files)
                if response.status_code == 200:
                    translation = response.json().get("translation", "No translation found.")
                    st.success(f"🐱 Translation: {translation}")
                else:
                    st.error("Failed to get translation from backend.")
            except Exception as e:
                st.error(f"Request failed: {e}")
    else:
        st.warning("No audio captured.")


# ✅ Persistent debug logs in browser UI
st.markdown("### 🔧 Debug Logs:")
if 'log' in st.session_state:
    for i, msg in enumerate(st.session_state.log[-20:], 1):
        st.write(f"{i}. {msg}")
else:
    st.write("No logs yet.")
