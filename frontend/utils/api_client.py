import requests
from typing import List, Dict, Any, Optional
import streamlit as st

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_v1 = f"{base_url}/api/v1"
    
    def get_scenarios(self) -> List[Dict[str, Any]]:
        """Get all available scenarios"""
        try:
            response = requests.get(f"{self.api_v1}/scenarios/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching scenarios: {e}")
            return []
    
    def get_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific scenario"""
        try:
            response = requests.get(f"{self.api_v1}/scenarios/{scenario_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching scenario: {e}")
            return None
    
    def submit_practice(self, scenario_id: str, user_response: str, input_type: str = "text") -> Optional[Dict[str, Any]]:
        """Submit a practice attempt"""
        try:
            data = {
                "scenario_id": scenario_id,
                "user_response": user_response,
                "input_type": input_type
            }
            response = requests.post(f"{self.api_v1}/practice/submit", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error submitting practice: {e}")
            return None
    
    def get_all_feedback(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all feedback results"""
        try:
            response = requests.get(f"{self.api_v1}/results/feedback?limit={limit}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching feedback: {e}")
            return []
    
    def get_all_attempts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all practice attempts"""
        try:
            response = requests.get(f"{self.api_v1}/results/attempts?limit={limit}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching attempts: {e}")
            return []