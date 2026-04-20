import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMBrain:
    """
    Responsibilities:
    Natural language reasoning
    Deep context understanding
    Response generation
    Thought augmentation
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            # Fallback for demonstration if key is missing,
            # though the requirement says use it.
            print("Warning: OPENAI_API_KEY not found in environment.")

        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def reason(self, prompt: str, context: str = ""):
        """Deep reasoning based on input and context."""
        if not self.client:
            return f"[Simulated Reason] Reasoning about: {prompt[:50]}... with context: {context[:50]}..."

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are the Ω GOD_BRAIN_CORE_Ω, a sovereign cognitive operating system. Reason deeply and provide structured output."},
                    {"role": "user", "content": f"Context: {context}\n\nTask: {prompt}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in LLM Reasoning: {str(e)}"

    async def augment_thought(self, thought: str):
        """Enhances a generated thought with deeper insights."""
        if not self.client:
            return f"[Simulated Augmentation] Augmented thought: {thought}"

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are the augmentation layer of Ω GOD_BRAIN_CORE_Ω. Expand and refine the following thought."},
                    {"role": "user", "content": thought}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in Thought Augmentation: {str(e)}"
