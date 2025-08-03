from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List


class MedicalAccuracyDetail(BaseModel):
    score: int = Field(..., description="Score for medical accuracy (1-10)")
    explanation: str = Field(...,
                             description="Explanation for the medical accuracy score")
    strengths: List[str] = Field(...,
                                 description="Strengths in medical accuracy")
    improvements: List[str] = Field(...,
                                    description="Areas for improvement in medical accuracy")


prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a senior medical doctor. Analyze the medical accuracy of the following response. Ignore tone, empathy, and clarity. Focus ONLY on medical facts and terminology. Return your analysis as a structured object."),
    ("user", "Scenario Context: {context}\nKey Points to Cover: {key_points}\n---\nHealthcare Professional's Response:\n\"{user_response}\"\n---\nPlease provide your analysis.")
])

llm = ChatOpenAI(
    model="gemini-2.5-flash",
    api_key="AIzaSyB_FyRxSW7Sw03BnanidKkcTEzBgUJSCkE",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
    temperature=0.2
)
structured_llm = llm.with_structured_output(MedicalAccuracyDetail)

# 3. Compose the chain
chain = prompt | structured_llm

# 4. Example input
input_data = {
    "context": "A patient presents with a sore throat and fever.",
    "key_points": "Ask about duration, check for strep symptoms, assess for complications",
    "user_response": "The patient likely has a viral infection. I recommend rest and fluids."
}

# 5. Invoke the chain and print the structured output
if __name__ == "__main__":
    result = chain.invoke(input_data)
    print("Structured output:")
    print(result)
