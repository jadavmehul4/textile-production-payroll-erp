import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from loguru import logger

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
            logger.warning("OPENAI_API_KEY not found in environment. LLM will run in simulation mode.")

        self.client = AsyncOpenAI(api_key=self.api_key, timeout=30.0) if self.api_key else None

    async def reason(self, prompt: str, context: str = ""):
        """Deep reasoning based on input and context."""
        if not self.client:
            logger.info("Using simulated reasoning (no client).")
            return f"[Simulated Reason] Reasoning about: {prompt[:50]}... with context: {context[:50]}..."

        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are the Ω GOD_BRAIN_CORE_Ω, a sovereign cognitive operating system. Reason deeply and provide structured output."},
                        {"role": "user", "content": f"Context: {context}\n\nTask: {prompt}"}
                    ]
                ),
                timeout=45.0
            )
            return response.choices[0].message.content
        except asyncio.TimeoutError:
            logger.error("LLM reasoning timed out.")
            return "Reasoning failed: Request timed out."
        except Exception as e:
            logger.exception(f"Error in LLM Reasoning: {str(e)}")
            return f"Reasoning failed due to internal error: {str(e)}"

    async def augment_thought(self, thought: str):
        """Enhances a generated thought with deeper insights."""
        if not self.client:
            logger.info("Using simulated augmentation (no client).")
            return f"[Simulated Augmentation] Augmented thought: {thought}"

        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are the augmentation layer of Ω GOD_BRAIN_CORE_Ω. Expand and refine the following thought."},
                        {"role": "user", "content": thought}
                    ]
                ),
                timeout=30.0
            )
            return response.choices[0].message.content
        except asyncio.TimeoutError:
            logger.error("Thought augmentation timed out.")
            return thought  # Fallback to original thought
        except Exception as e:
            logger.exception(f"Error in Thought Augmentation: {str(e)}")
            return thought  # Fallback to original thought
