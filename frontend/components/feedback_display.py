import streamlit as st
from typing import Dict, Any
import plotly.graph_objects as go
import plotly.express as px

def display_feedback(feedback: Dict[str, Any]):
    """Display AI feedback analysis"""
    if not feedback:
        st.error("No feedback data available")
        return
    
    st.success("✅ Analysis Complete!")
    
    # Overall score
    overall_score = feedback.get('overall_score', 0)
    st.metric("Overall Score", f"{overall_score:.1f}/10", 
              delta=None, delta_color="normal")
    
    # Score breakdown chart
    scores = {
        'Medical Accuracy': feedback.get('medical_accuracy', {}).get('score', 0),
        'Communication Clarity': feedback.get('communication_clarity', {}).get('score', 0),
        'Empathy & Tone': feedback.get('empathy_tone', {}).get('score', 0),
        'Completeness': feedback.get('completeness', {}).get('score', 0)
    }
    
    # Create radar chart
    fig = go.Figure()
    
    categories = list(scores.keys())
    values = list(scores.values())
    values += values[:1]  # Close the radar chart
    categories += categories[:1]
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Your Performance'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=False,
        title="Performance Breakdown"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed feedback for each category
    categories_data = [
        ('Medical Accuracy', feedback.get('medical_accuracy', {})),
        ('Communication Clarity', feedback.get('communication_clarity', {})),
        ('Empathy & Tone', feedback.get('empathy_tone', {})),
        ('Completeness', feedback.get('completeness', {}))
    ]
    
    for category_name, category_data in categories_data:
        with st.expander(f"📊 {category_name} - {category_data.get('score', 0):.1f}/10"):
            
            # Explanation
            st.markdown("**Analysis:**")
            st.write(category_data.get('explanation', 'No explanation available'))
            
            # Strengths
            strengths = category_data.get('strengths', [])
            if strengths:
                st.markdown("**✅ Strengths:**")
                for strength in strengths:
                    st.write(f"• {strength}")
            
            # Areas for improvement
            improvements = category_data.get('improvements', [])
            if improvements:
                st.markdown("**🎯 Areas for Improvement:**")
                for improvement in improvements:
                    st.write(f"• {improvement}")
            
            # Examples
            examples = category_data.get('examples', [])
            if examples:
                st.markdown("**💡 Examples:**")
                for example in examples:
                    st.write(f"• {example}")
    
    # General feedback
    general_feedback = feedback.get('general_feedback', '')
    if general_feedback:
        st.markdown("### 📝 General Feedback")
        st.info(general_feedback)
    
    # Next steps
    st.markdown("### 🎯 Recommended Next Steps")
    if overall_score >= 90:
        st.success("Excellent work! Consider trying a more challenging scenario.")
    elif overall_score >= 80:
        st.info("Good performance! Focus on the improvement areas highlighted above.")
    elif overall_score >= 70:
        st.warning("Decent attempt. Review the feedback and practice the key areas mentioned.")
    else:
        st.error("This scenario needs more practice. Focus on the fundamental communication principles.")