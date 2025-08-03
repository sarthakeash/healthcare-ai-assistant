import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from frontend.utils.api_client import APIClient

st.title("📊 Progress & Results")

api = APIClient()

# Get data
feedback_data = api.get_all_feedback()
attempts_data = api.get_all_attempts()

if not feedback_data:
    st.info("No practice data available yet. Complete some practice scenarios to see your progress here!")
    st.stop()

# Convert to DataFrame for analysis
df_feedback = pd.DataFrame(feedback_data)
df_attempts = pd.DataFrame(attempts_data)

# Parse timestamps
df_feedback['timestamp'] = pd.to_datetime(df_feedback['timestamp'])
df_attempts['timestamp'] = pd.to_datetime(df_attempts['timestamp'])

# Overview metrics
st.markdown("### 📈 Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_attempts = len(df_attempts)
    st.metric("Total Attempts", total_attempts)

with col2:
    avg_score = df_feedback['overall_score'].mean()
    st.metric("Average Score", f"{avg_score:.1f}")

with col3:
    recent_attempts = len(df_attempts[df_attempts['timestamp'] > datetime.now() - timedelta(days=7)])
    st.metric("This Week", recent_attempts)

with col4:
    best_score = df_feedback['overall_score'].max()
    st.metric("Best Score", f"{best_score:.1f}")

st.markdown("---")

# Progress over time
st.markdown("### 📈 Progress Over Time")
if len(df_feedback) > 1:
    fig_progress = px.line(
        df_feedback.sort_values('timestamp'), 
        x='timestamp', 
        y='overall_score',
        title='Overall Score Progression',
        labels={'overall_score': 'Score', 'timestamp': 'Date'}
    )
    fig_progress.update_traces(mode='markers+lines')
    fig_progress.update_layout(showlegend=False)
    st.plotly_chart(fig_progress, use_container_width=True)
else:
    st.info("Complete more attempts to see progress trends.")

# Score breakdown
st.markdown("### 🎯 Performance Breakdown")
col1, col2 = st.columns(2)

with col1:
    # Average scores by category
    categories = ['medical_accuracy', 'communication_clarity', 'empathy_tone', 'completeness']
    avg_scores = []
    
    for category in categories:
        scores = [item['score'] for item in df_feedback[category] if isinstance(item, dict)]
        avg_scores.append(sum(scores) / len(scores) if scores else 0)
    
    category_names = ['Medical Accuracy', 'Communication Clarity', 'Empathy & Tone', 'Completeness']
    
    fig_categories = px.bar(
        x=category_names,
        y=avg_scores,
        title='Average Scores by Category',
        labels={'x': 'Category', 'y': 'Average Score'},
        color=avg_scores,
        color_continuous_scale='RdYlGn'
    )
    fig_categories.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig_categories, use_container_width=True)

with col2:
    # Score distribution
    fig_dist = px.histogram(
        df_feedback,
        x='overall_score',
        nbins=10,
        title='Score Distribution',
        labels={'overall_score': 'Overall Score', 'count': 'Frequency'}
    )
    st.plotly_chart(fig_dist, use_container_width=True)

# Recent attempts table
st.markdown("### 📋 Recent Attempts")
if len(df_feedback) > 0:
    # Prepare data for display
    recent_data = df_feedback.head(10).copy()
    recent_data['Date'] = recent_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    recent_data['Score'] = recent_data['overall_score'].round(1)
    
    # Get scenario titles
    scenarios = api.get_scenarios()
    scenario_map = {s['id']: s['title'] for s in scenarios}
    recent_data['Scenario'] = recent_data['scenario_id'].map(scenario_map)
    
    display_df = recent_data[['Date', 'Scenario', 'Score']].copy()
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

# Detailed feedback viewer
st.markdown("### 🔍 Detailed Feedback Review")
if len(df_feedback) > 0:
    # Select attempt to review
    attempt_options = {}
    for _, row in df_feedback.iterrows():
        scenario_title = scenario_map.get(row['scenario_id'], 'Unknown Scenario')
        date_str = row['timestamp'].strftime('%Y-%m-%d %H:%M')
        score = row['overall_score']
        attempt_options[f"{scenario_title} - {date_str} (Score: {score:.1f})"] = row['attempt_id']
    
    selected_attempt = st.selectbox(
        "Select an attempt to review:",
        options=list(attempt_options.keys())
    )
    
    if selected_attempt:
        attempt_id = attempt_options[selected_attempt]
        
        # Find the feedback data
        feedback_row = df_feedback[df_feedback['attempt_id'] == attempt_id].iloc[0]
        
        # Find the attempt data
        attempt_row = df_attempts[df_attempts['id'] == attempt_id]
        
        if len(attempt_row) > 0:
            attempt_row = attempt_row.iloc[0]
            
            # Display the attempt
            st.markdown("**Your Response:**")
            st.info(attempt_row['user_response'])
            
            # Display detailed feedback using the feedback component
            st.markdown("**AI Feedback:**")
            from frontend.components.feedback_display import display_feedback
            
            # Convert the row back to dictionary format
            feedback_dict = {
                'overall_score': feedback_row['overall_score'],
                'general_feedback': feedback_row['general_feedback'],
                'medical_accuracy': feedback_row['medical_accuracy'],
                'communication_clarity': feedback_row['communication_clarity'],
                'empathy_tone': feedback_row['empathy_tone'],
                'completeness': feedback_row['completeness']
            }
            
            display_feedback(feedback_dict)

# Sidebar with insights
with st.sidebar:
    st.markdown("### 📊 Quick Insights")
    
    if len(df_feedback) > 0:
        # Best performing category
        avg_scores_dict = dict(zip(category_names, avg_scores))
        best_category = max(avg_scores_dict.items(), key=lambda x: x[1])
        worst_category = min(avg_scores_dict.items(), key=lambda x: x[1])
        
        st.success(f"**Strongest Area:**\n{best_category[0]} ({best_category[1]:.1f})")
        st.warning(f"**Focus Area:**\n{worst_category[0]} ({worst_category[1]:.1f})")
        
        # Progress indicator
        if len(df_feedback) >= 2:
            recent_avg = df_feedback.head(5)['overall_score'].mean()
            older_avg = df_feedback.tail(5)['overall_score'].mean()
            improvement = recent_avg - older_avg
            
            if improvement > 2:
                st.success(f"📈 Improving! (+{improvement:.1f} points)")
            elif improvement < -2:
                st.warning(f"📉 Declining ({improvement:.1f} points)")
            else:
                st.info("📊 Stable performance")
    
    st.markdown("### 🎯 Recommendations")
    st.markdown("""
    - Practice regularly for consistent improvement
    - Focus on your weakest scoring category
    - Try scenarios of varying difficulty
    - Review detailed feedback for specific tips
    """)