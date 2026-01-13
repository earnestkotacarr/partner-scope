"""Startup Discovery Assistant - helps startups discover their partnership needs."""

import os
import json
from openai import OpenAI
from .prompts import STARTUP_DISCOVERY_PROMPT
from ..utils.cost_tracker import calculate_cost


class StartupDiscoveryAssistant:
    """Conversational assistant for startup partner requirement discovery."""

    def __init__(self):
        self._client = None
        self.model = "gpt-4o-mini"
        self._last_cost = None  # Track cost of last operation

    @property
    def client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            self._client = OpenAI(api_key=api_key)
        return self._client

    def chat(self, messages: list, current_message: str) -> dict:
        """
        Process a chat message and return response.

        Args:
            messages: Conversation history
            current_message: The new user message

        Returns:
            dict with 'response', 'ready_for_template', 'suggested_actions'
        """
        # Build conversation for OpenAI
        openai_messages = [
            {"role": "system", "content": STARTUP_DISCOVERY_PROMPT}
        ]

        # Add conversation history
        for msg in messages:
            openai_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current message
        openai_messages.append({
            "role": "user",
            "content": current_message
        })

        # Call OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=0.7,
            max_tokens=500
        )

        assistant_response = response.choices[0].message.content

        # Extract cost information
        cost_data = None
        if response.usage:
            cost_data = calculate_cost(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                model=self.model
            )
            self._last_cost = cost_data

        # Check if ready for template (simple heuristic based on conversation length and content)
        ready = self._check_ready_for_template(messages, current_message, assistant_response)

        return {
            "response": assistant_response,
            "ready_for_template": ready,
            "suggested_actions": ["continue"] if not ready else ["continue", "generate_template"],
            "cost": cost_data
        }

    def _check_ready_for_template(self, messages: list, current_message: str, response: str) -> bool:
        """
        Check if we have enough information to generate a template.

        Simple heuristics:
        - At least 4 exchanges (8 messages including assistant)
        - Or if the assistant suggests generating a profile
        """
        total_messages = len(messages) + 2  # +2 for current exchange

        # Check if assistant suggests generating profile
        ready_phrases = [
            "generate your partner",
            "partner search profile",
            "ready to generate",
            "good picture now",
            "enough information"
        ]

        response_lower = response.lower()
        suggests_ready = any(phrase in response_lower for phrase in ready_phrases)

        # Ready if 8+ messages or assistant suggests it
        return total_messages >= 8 or suggests_ready

    def generate_template(self, messages: list) -> dict:
        """
        Extract a structured scenario template from the conversation.

        Args:
            messages: Full conversation history

        Returns:
            ScenarioTemplate dict
        """
        # Build extraction prompt
        extraction_prompt = """Based on the conversation, extract the following information into a JSON object:

{
    "startup_name": "Name of the startup (or 'Unknown' if not mentioned)",
    "description": "Brief description of what they're building",
    "industry": "Primary industry/sector",
    "investment_stage": "One of: Pre-Seed, Seed, Series A, Series B, Series C+, or Unknown",
    "product_stage": "One of: Concept, MVP, Beta, Launched",
    "partner_needs": "Description of the types of partners they need (combine all discussed needs)",
    "keywords": ["list", "of", "search", "keywords", "for", "finding", "partners"]
}

Be thorough in the partner_needs field - include all types of partners discussed.
Generate relevant keywords based on the conversation for searching.

Respond ONLY with the JSON object, no other text."""

        # Build conversation for extraction
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in messages
        ])

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You extract structured data from conversations."},
                {"role": "user", "content": f"Conversation:\n{conversation_text}\n\n{extraction_prompt}"}
            ],
            temperature=0.3,
            max_tokens=500
        )

        # Extract cost information
        cost_data = None
        if response.usage:
            cost_data = calculate_cost(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                model=self.model
            )
            self._last_cost = cost_data

        # Parse JSON response
        try:
            template = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            content = response.choices[0].message.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                template = json.loads(content[start:end])
            else:
                # Return default template
                template = {
                    "startup_name": "Unknown",
                    "description": "",
                    "industry": "",
                    "investment_stage": "Seed",
                    "product_stage": "MVP",
                    "partner_needs": "Partner companies for collaboration",
                    "keywords": ["partner", "collaboration"]
                }

        # Add cost to template response
        template['_cost'] = cost_data

        return template
