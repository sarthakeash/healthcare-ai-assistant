import streamlit as st
from datetime import datetime
from utils.api_client import APIClient
from components.scenario_display import display_scenario
from components.feedback_display import display_feedback
from streamlit_mic_recorder import mic_recorder

st.title("🏥 Practice Healthcare Communication")

# Initialize API client and session state variables
api = APIClient()
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'is_submitting' not in st.session_state:
    st.session_state.is_submitting = False

# --- Scenario Selection ---
st.markdown("### Select a Practice Scenario")
scenarios = api.get_scenarios()
if not scenarios:
    st.error("Could not load scenarios. Please ensure the backend is running.")
    st.stop()

scenario_options = {f"{s['title']} ({s['difficulty'].title()})": s['id'] for s in scenarios}
selected_title = st.selectbox("Choose a scenario:", options=list(scenario_options.keys()))
scenario_id = scenario_options[selected_title]

scenario = api.get_scenario(scenario_id)
if not scenario:
    st.error("Failed to load scenario details.")
    st.stop()

if not st.session_state.feedback:
    display_scenario(scenario)

    st.markdown("### Your Response")
    st.write("You can either type your response or record it using your microphone.")

    # --- Text Input ---
    user_response_text = st.text_area(
        "Type your response here:",
        height=120,
        placeholder="Consider the patient's needs, use clear language, and address all key points."
    )
    submit_text_clicked = st.button(
        "Analyze Text Response",
        type="primary",
        disabled=st.session_state.is_submitting or not user_response_text.strip(),
    )

    # --- Voice Input ---
    st.divider()
    st.write("Or record your voice:")
    audio_info = mic_recorder(
        start_prompt="Record your response 🎙️",
        stop_prompt="Stop recording ⏹️",
        just_once=False,
        use_container_width=False,
        callback=None,
        args=(),
        kwargs={},
        key=None
    )
    
    submit_voice_clicked = False
    if audio_info:
        st.audio(audio_info['bytes'])
        submit_voice_clicked = st.button(
            "Analyze Voice Response",
            disabled=st.session_state.is_submitting
        )

    # --- Submission Logic ---
    if submit_text_clicked:
        st.session_state.is_submitting = True
        with st.spinner("🤖 AI is analyzing your response..."):
            feedback = api.submit_practice(
                scenario_id=scenario_id,
                user_response=user_response_text,
                user_id="default_user",
                input_type="text"
            )
            st.session_state.feedback = feedback
        st.session_state.is_submitting = False
        st.rerun()

    if submit_voice_clicked:
        st.session_state.is_submitting = True
        with st.spinner("🎙️ Transcribing and analyzing your voice..."):
            feedback = api.submit_practice_voice(
                scenario_id=scenario_id,
                user_id="default_user",
                audio_bytes=audio_info['bytes']
            )
            st.session_state.feedback = feedback
        st.session_state.is_submitting = False
        st.rerun()

if st.session_state.feedback:
    st.markdown("---")
    st.markdown("### 📊 AI Feedback Analysis")
    display_feedback(st.session_state.feedback)
    st.markdown("---")
    if st.button("🔄 Practice Another Scenario"):
        # Clear the feedback to show the main page again
        st.session_state.feedback = None
        st.rerun()

with st.sidebar:
    st.markdown("### 💡 Communication Tips")
    st.markdown("""
    - Read the scenario carefully.
    - Use simple, clear language.
    - Show empathy and understanding.
    - Address all key points.
    """)