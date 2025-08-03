import os
import json
import argparse
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from core.models import Scenario
from core.config import settings

SCENARIOS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'scenarios')

def get_next_scenario_id():
    try:
        existing_files = [f for f in os.listdir(SCENARIOS_DIR) if f.startswith('scenario_') and f.endswith('.json')]
        if not existing_files:
            return "001"
        
        last_num = max([int(f.split('_')[1].split('.')[0]) for f in existing_files])
        next_num = last_num + 1
        return f"{next_num:03d}"
    except Exception as e:
        print(f"Error determining next scenario ID: {e}")
        return "999"

def generate_scenario(difficulty: str, department: str, patient_type: str) -> Scenario:
    print("Initializing AI model to generate scenario...")
    
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_base_url,
        temperature=0.8
    )
    
    structured_llm = llm.with_structured_output(Scenario)
    
    system_prompt = """
    You are an expert in medical education and curriculum design. Your task is to create a realistic, high-quality practice scenario for a healthcare professional.
    The scenario must be detailed, providing clear context and objectives.
    Fill out all fields in the `Scenario` Pydantic model provided, following the example closely.
    The 'id' should be a placeholder like 'temp_id', as it will be replaced by the script.
    """
    
    user_prompt = f"""
    Please generate a new healthcare communication scenario based on the new parameters provided below.
    The 'title' should be derived from the core task within the generated context.
    Follow the structure and tone of this example carefully.

    ---
    **EXAMPLE SCENARIO:**
    - **id**: "scenario_001"
    - **title**: "Greeting and Initial Assessment"
    - **description**: "Greet a nervous new patient, make them comfortable, and gather basic information about their visit."
    - **context**: "A new patient arrives for their first appointment. They seem nervous and are speaking very quickly in broken English. They are clutching their stomach and wringing their hands. Your goal is to start the conversation, make them feel comfortable, and gather basic information about why they're here today."
    - **difficulty**: "beginner"
    - **medical_area**: "General Practice"
    - **patient_type**: "Nervous, limited English speaker"
    - **key_points**: [
        "Use a warm and welcoming tone.",
        "Speak slowly and clearly.",
        "Ask open-ended questions to start the conversation.",
        "Acknowledge their nervousness non-verbally or verbally.",
        "Determine the primary reason for their visit."
    ]
    ---

    **NEW SCENARIO PARAMETERS:**
    - **Difficulty Level:** {difficulty}
    - **Medical Department:** {department}
    - **Patient Type:** {patient_type}

    Now, generate the new scenario based on these new parameters.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    chain = prompt | structured_llm
    
    print(f"Generating scenario for department: '{department}'...")
    generated_scenario = chain.invoke({})
    print("Scenario generated successfully.")
    
    return generated_scenario

def save_scenario_to_file(scenario: Scenario):
    next_id = get_next_scenario_id()
    scenario.id = f"scenario_{next_id}"
    
    file_path = os.path.join(SCENARIOS_DIR, f"{scenario.id}.json")
    
    print(f"Saving new scenario to: {file_path}")
    
    try:
        with open(file_path, 'w') as f:
            json.dump(scenario.dict(), f, indent=4)
        print("Successfully saved the new scenario!")
    except Exception as e:
        print(f"Error saving scenario file: {e}")

if __name__ == "__main__":
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

    parser = argparse.ArgumentParser(description="Generate a new healthcare communication scenario using AI.")
    parser.add_argument("--difficulty", type=str, choices=['beginner', 'intermediate', 'advanced'], required=True, help="The difficulty level of the scenario.")
    parser.add_argument("--department", type=str, required=True, help="The medical department for the scenario (e.g., 'Pediatrics', 'Oncology').")
    parser.add_argument("--patient", type=str, required=True, help="A brief description of the patient (e.g., 'An elderly patient who is hard of hearing').")
    
    args = parser.parse_args()
    
    new_scenario = generate_scenario(
        difficulty=args.difficulty,
        department=args.department, 
        patient_type=args.patient
    )
    if new_scenario:
        save_scenario_to_file(new_scenario)