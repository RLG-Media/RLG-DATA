import openai
from flask import current_app

class AIEmailResponseService:
    """
    Service class for generating AI email responses.
    """
    def __init__(self, openai_api_key):
        if not openai_api_key:
            raise ValueError("OpenAI API key is required to initialize AIEmailResponseService.")
        openai.api_key = openai_api_key

    def generate_response(self, prompt, temperature=0.7, max_tokens=250):
        """
        Generate a response using OpenAI's API.
        
        :param prompt: The prompt for generating the response.
        :param temperature: Sampling temperature (controls randomness).
        :param max_tokens: Maximum number of tokens for the response.
        :return: Generated response text or None in case of error.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            current_app.logger.error(f"Failed to generate response: {str(e)}")
            return None

    def bulk_generate_responses(self, prompts, temperature=0.7, max_tokens=250):
        """
        Generate responses for multiple prompts in bulk.
        
        :param prompts: List of prompts to generate responses for.
        :param temperature: Sampling temperature.
        :param max_tokens: Maximum tokens for each response.
        :return: Dictionary of prompts and their corresponding responses.
        """
        results = {}
        for prompt in prompts:
            response = self.generate_response(prompt, temperature, max_tokens)
            results[prompt] = response
        return results

    def fine_tuned_response(self, prompt, model="fine-tuned-model-id", temperature=0.7, max_tokens=250):
        """
        Generate a response using a fine-tuned OpenAI model.
        
        :param prompt: The prompt for generating the response.
        :param model: Fine-tuned model ID.
        :param temperature: Sampling temperature.
        :param max_tokens: Maximum tokens for the response.
        :return: Generated response text or None in case of error.
        """
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            current_app.logger.error(f"Failed to generate fine-tuned response: {str(e)}")
            return None

# Example usage
if __name__ == "__main__":
    api_key = "your_openai_api_key_here"
    email_service = AIEmailResponseService(openai_api_key=api_key)

    # Single response
    prompt = "Write a formal email response to a customer complaint about delayed delivery."
    response = email_service.generate_response(prompt)
    if response:
        print("Generated Response:", response)
    else:
        print("Failed to generate response.")

    # Bulk responses
    prompts = [
        "Write a thank-you email to a customer for their purchase.",
        "Draft an email apologizing for a service outage.",
        "Create an email offering a discount for loyal customers."
    ]
    bulk_responses = email_service.bulk_generate_responses(prompts)
    for p, r in bulk_responses.items():
        print(f"Prompt: {p}\nResponse: {r}\n")

    # Fine-tuned response
    fine_tuned_prompt = "Generate a marketing email for a new product launch."
    fine_tuned_response = email_service.fine_tuned_response(fine_tuned_prompt)
    if fine_tuned_response:
        print("Fine-tuned Response:", fine_tuned_response)
    else:
        print("Failed to generate fine-tuned response.")
