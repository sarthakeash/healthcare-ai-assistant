import streamlit as st
from typing import Dict, Any

def display_scenario(scenario: Dict[str, Any]):
    """Display scenario information"""
    if not scenario:
        st.error("No scenario data available")
        return
    
    # Main scenario info
    st.subheader(scenario.get('title', 'Unknown Scenario'))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Difficulty", scenario.get('difficulty', 'Unknown').title())
    with col2:
        st.metric("Medical Area", scenario.get('medical_area', 'General'))
    with col3:
        st.metric("Patient Type", scenario.get('patient_type', 'Standard'))
    
    # Description and context
    st.markdown("**Description:**")
    st.write(scenario.get('description', 'No description available'))
    
    st.markdown("**Scenario Context:**")
    st.info(scenario.get('context', 'No context available'))
    
    # Key points to cover
    key_points = scenario.get('key_points', [])
    if key_points:
        st.markdown("**Key Points to Address:**")
        for i, point in enumerate(key_points, 1):
            st.write(f"{i}. {point}")
    
    st.divider()