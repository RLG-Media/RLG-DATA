import openai
from flask import current_app
from typing import Dict, List, Optional
import logging

# Configure logging if not already configured by the application
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AIEmailResponseService:
    """
    Service class for generating AI email responses using OpenAI's ChatCompletion API.
    
    This service supports:
      - Generating a single email response.
      - Generating bulk responses for multiple prompts.
      - Generating responses using a fine-tuned OpenAI model.
      
    It is designed to be robust and scalable, suitable for both RLG Data and RLG Fans.
    """

    def __init__(self, openai_api_key: str) -> None:
        """
        Initialize the AIEmailResponseService with the provided OpenAI API key.
        
        Args:
            openai_api_key (str): The OpenAI API key.
        
        Raises:
            ValueError: If the API key is not provided.
        """
        if not openai_api_key:
            raise ValueError("OpenAI API key is required to initialize AIEmailResponseService.")
        openai.api_key = openai_api_key
        logger.info("AIEmailResponseService initialized successfully.")

    def generate_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 250) -> Optional[str]:
        """
        Generate a single email response using OpenAI's ChatCompletion API.
        
        Args:
            prompt (str): The prompt for generating the response.
            temperature (float): Sampling temperature to control randomness (default: 0.7).
            max_tokens (int): Maximum number of tokens in the generated response (default: 250).
        
        Returns:
            Optional[str]: The generated response text, or None if an error occurs.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            generated_text = response.choices[0].message['content'].strip()
            logger.info("Generated email response successfully.")
            return generated_text
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Failed to generate response: {str(e)}")
            else:
                logger.error(f"Failed to generate response: {str(e)}")
            return None

    def bulk_generate_responses(self, prompts: List[str], temperature: float = 0.7, max_tokens: int = 250) -> Dict[str, Optional[str]]:
        """
        Generate responses for multiple prompts in bulk.
        
        Args:
            prompts (List[str]): List of prompts to generate responses for.
            temperature (float): Sampling temperature for generation.
            max_tokens (int): Maximum tokens for each generated response.
        
        Returns:
            Dict[str, Optional[str]]: Dictionary mapping each prompt to its generated response.
        """
        results = {}
        for prompt in prompts:
            response = self.generate_response(prompt, temperature, max_tokens)
            results[prompt] = response
        logger.info("Bulk email responses generated.")
        return results

    def fine_tuned_response(self, prompt: str, model: str = "fine-tuned-model-id", temperature: float = 0.7, max_tokens: int = 250) -> Optional[str]:
        """
        Generate an email response using a fine-tuned OpenAI model.
        
        Args:
            prompt (str): The prompt for generating the response.
            model (str): The fine-tuned model ID to use.
            temperature (float): Sampling temperature (default: 0.7).
            max_tokens (int): Maximum tokens for the response (default: 250).
        
        Returns:
            Optional[str]: The generated response text, or None if an error occurs.
        """
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            generated_text = response.choices[0].message['content'].strip()
            logger.info("Generated fine-tuned email response successfully.")
            return generated_text
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Failed to generate fine-tuned response: {str(e)}")
            else:
                logger.error(f"Failed to generate fine-tuned response: {str(e)}")
            return None

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    api_key = "your_openai_api_key_here"  # Replace with your actual API key
    email_service = AIEmailResponseService(openai_api_key=api_key)

    # Generate a single email response
    prompt = "Write a formal email response to a customer complaint about delayed delivery."
    response = email_service.generate_response(prompt)
    if response:
        print("Generated Response:")
        print(response)
    else:
        print("Failed to generate response.")

    # Bulk email responses
    prompts = [
        "Write a thank-you email to a customer for their purchase.",
        "Draft an email apologizing for a service outage.",
        "Create an email offering a discount for loyal customers."
    ]
    bulk_responses = email_service.bulk_generate_responses(prompts)
    for p, r in bulk_responses.items():
        print(f"Prompt: {p}\nResponse: {r}\n")

    # Fine-tuned email response
    fine_tuned_prompt = "Generate a marketing email for a new product launch."
    fine_tuned_response = email_service.fine_tuned_response(fine_tuned_prompt)
    if fine_tuned_response:
        print("Fine-tuned Response:")
        print(fine_tuned_response)
    else:
        print("Failed to generate fine-tuned response.")
