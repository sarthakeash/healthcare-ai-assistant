import streamlit as st

st.set_page_config(
    page_title="Healthcare Communication Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏥 Healthcare Communication Assistant")
st.markdown("""
Welcome to the Healthcare Communication Assistant! This tool helps healthcare 
professionals practice patient interactions and receive AI-powered feedback.

### How to use:
1. 📝 Go to **Practice** to start a scenario
2. 🎤 Submit your response (text input)
3. 📊 Receive detailed AI feedback
4. 📈 Track your progress in **Results**

Select a page from the sidebar to begin!
""")

# Initialize session state
if 'attempt_history' not in st.session_state:
    st.session_state.attempt_history = []

# API connection status
with st.expander("🔧 API Connection Status"):
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Backend API is running")
        else:
            st.error("❌ Backend API is not responding correctly")
    except:
        st.error("❌ Backend API is not running. Please start the FastAPI server first.")
        st.code("cd backend && uvicorn main:app --reload --port 8000")

st.markdown("---")
st.markdown("**🎯 Quick Start:**")
col1, col2 = st.columns(2)
with col1:
    st.info("**New User?** Start with a beginner scenario to get familiar with the interface.")
with col2:
    st.info("**Experienced?** Try intermediate or advanced scenarios for more challenge.")