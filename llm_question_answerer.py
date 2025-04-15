"""
LLM Question Answerer - Uses LLMs to answer questions about financial documents.
"""
import os
import re
import json
import requests
from typing import Dict, List, Any, Optional

class LLMQuestionAnswerer:
    """
    Question answerer that uses LLMs to provide sophisticated answers to financial questions.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the LLM question answerer.
        
        Args:
            api_key: API key for the LLM service (default: None, uses environment variable)
            model: Model to use for answering questions (default: gpt-4o-mini)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
        self.model = model
        self.use_openrouter = "OPENROUTER_API_KEY" in os.environ or self.api_key and self.api_key.startswith("sk-or-")
        
        if not self.api_key:
            print("Warning: No API key provided for LLM. Question answering will be limited.")
    
    def answer_question(self, question: str, context: str) -> str:
        """
        Answer a question based on the provided context.
        
        Args:
            question: Question to answer
            context: Context information to use for answering the question
        
        Returns:
            Answer to the question
        """
        if not self.api_key:
            return "LLM question answering is not available. Please provide an API key."
        
        try:
            # Prepare the prompt
            prompt = self._prepare_prompt(question, context)
            
            # Call the LLM API
            if self.use_openrouter:
                response = self._call_openrouter_api(prompt)
            else:
                response = self._call_openai_api(prompt)
            
            return response
            
        except Exception as e:
            print(f"Error answering question with LLM: {str(e)}")
            return f"Error answering question: {str(e)}"
    
    def _prepare_prompt(self, question: str, context: str) -> str:
        """
        Prepare a prompt for the LLM.
        
        Args:
            question: Question to answer
            context: Context information to use for answering the question
        
        Returns:
            Prompt for the LLM
        """
        # Truncate context if it's too long
        max_context_length = 8000
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
        
        return f"""You are a financial document analysis assistant. You help users understand financial documents and answer questions about them.

Below is information extracted from a financial document:

{context}

Please answer the following question based on the information above:

{question}

If the information needed to answer the question is not in the provided context, say so clearly. Do not make up information.
Provide a clear, concise, and accurate answer based on the financial document.
"""
    
    def _call_openai_api(self, prompt: str) -> str:
        """
        Call the OpenAI API to get a response.
        
        Args:
            prompt: Prompt to send to the API
        
        Returns:
            Response from the API
        """
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a financial document analysis assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"]
        else:
            error_message = response_json.get("error", {}).get("message", "Unknown error")
            raise Exception(f"API error: {error_message}")
    
    def _call_openrouter_api(self, prompt: str) -> str:
        """
        Call the OpenRouter API to get a response.
        
        Args:
            prompt: Prompt to send to the API
        
        Returns:
            Response from the API
        """
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/aviadkim/backv2"  # Replace with your actual site URL
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a financial document analysis assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"]
        else:
            error_message = response_json.get("error", {}).get("message", "Unknown error")
            raise Exception(f"API error: {error_message}")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Answer questions about financial documents using LLMs.")
    parser.add_argument("question", help="Question to answer")
    parser.add_argument("--context-file", help="Path to a file containing context information")
    parser.add_argument("--context", help="Context information to use for answering the question")
    parser.add_argument("--api-key", help="API key for the LLM service")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model to use for answering questions")
    
    args = parser.parse_args()
    
    # Get context
    context = args.context
    if args.context_file:
        with open(args.context_file, "r", encoding="utf-8") as f:
            context = f.read()
    
    if not context:
        print("Error: No context provided. Use --context or --context-file.")
        return 1
    
    # Create question answerer
    answerer = LLMQuestionAnswerer(api_key=args.api_key, model=args.model)
    
    # Answer the question
    answer = answerer.answer_question(args.question, context)
    
    print(f"Question: {args.question}")
    print(f"Answer: {answer}")
    
    return 0

if __name__ == "__main__":
    main()
