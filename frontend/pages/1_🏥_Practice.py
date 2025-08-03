import streamlit as st
from datetime import datetime
from frontend.utils.api_client import APIClient
from frontend.components.scenario_display import display_scenario
from frontend.components.feedback_display import display_feedback

st.title("🏥 Practice Healthcare Communication")

api = APIClient()

# Scenario selection
st.markdown("### Select a Practice Scenario")
scenarios = api.get_scenarios()

if not scenarios:
    st.error("No scenarios available. Please check if the backend is running and scenarios are loaded.")
    st.stop()

# Create scenario options
scenario_options = {f"{s['title']} ({s['difficulty'].title()})": s['id'] for s in scenarios}
selected_title = st.selectbox(
    "Choose a scenario:",
    options=list(scenario_options.keys())
)
scenario_id = scenario_options[selected_title]

# Get and display scenario
if scenario_id:
    scenario = api.get_scenario(scenario_id)
    if scenario:
        display_scenario(scenario)
        
        # Response input
        st.markdown("### Your Response")
        user_response = st.text_area(
            "How would you respond to this patient?",
            height=200,
            placeholder="Type your response here... Consider the patient's needs, use appropriate language, and address all key points mentioned above.",
            help="Write your response as if you were speaking directly to the patient. Focus on clarity, empathy, and completeness."
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_clicked = st.button("🔍 Analyze Response", type="primary", disabled=not user_response.strip())
        
        if submit_clicked and user_response.strip():
            with st.spinner("🤖 AI is analyzing your response... This may take a moment."):
                feedback = api.submit_practice(
                    scenario_id=scenario_id,
                    user_response=user_response,
                    input_type="text"
                )
                
                if feedback:
                    # Store in session state
                    st.session_state.attempt_history.append({
                        'timestamp': datetime.now(),
                        'scenario': scenario['title'],
                        'scenario_id': scenario_id,
                        'user_response': user_response,
                        'feedback': feedback
                    })
                    
                    st.markdown("---")
                    st.markdown("### 📊 AI Feedback Analysis")
                    
                    # Display feedback
                    display_feedback(feedback)
                    
                    # Option to try another scenario
                    st.markdown("---")
                    if st.button("🔄 Try Another Scenario"):
                        st.rerun()
                else:
                    st.error("Failed to get feedback. Please try again.")
    else:
        st.error("Failed to load scenario details.")

# Sidebar with tips
with st.sidebar:
    st.markdown("### 💡 Communication Tips")
    st.markdown("""
    **Before responding:**
    - Read the scenario carefully
    - Note the patient type and context
    - Consider cultural sensitivity
    
    **In your response:**
    - Use simple, clear language
    - Show empathy and understanding
    - Address all key points
    - Ask appropriate questions
    
    **Remember:**
    - Avoid medical jargon
    - Be patient and reassuring
    - Maintain professional boundaries
    """)
    
    if st.session_state.attempt_history:
        st.markdown("### 📈 Recent Attempts")
        for i, attempt in enumerate(st.session_state.attempt_history[-3:], 1):
            score = attempt['feedback']['overall_score']
            st.metric(f"Attempt {len(st.session_state.attempt_history) - 3 + i}", f"{score:.1f}/100")