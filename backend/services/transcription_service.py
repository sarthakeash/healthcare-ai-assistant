import base64
from fastapi import UploadFile
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from core.config import settings

class TranscriptionService:
    """
    A service to handle audio transcription.
    """

    def __init__(self):
        self.client = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url
        )

    async def transcribe_audio(self, audio_file: UploadFile) -> str:
        """
        Transcribes an audio file to text using a multimodal model via LangChain.
        
        Args:
            audio_file: The audio file uploaded from the frontend.
            
        Returns:
            The transcribed text as a string.
        """
        try:
            audio_bytes = await audio_file.read()
            base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
            audio_url = f"data:audio/wav;base64,{base64_audio}"

            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Transcribe this audio recording of a person speaking. Provide only the text content of the speech.",
                    },
                    {
                        "type": "image_url", 
                        "image_url": {
                            "url": audio_url
                        }
                    },
                ]
            )

            response = self.client.invoke([message])
            transcribed_text = response.content
            print(f"Transcription result: {transcribed_text}")
            return transcribed_text

        except Exception as e:
            print(f"Error during audio transcription with LangChain: {e}")
            return ""