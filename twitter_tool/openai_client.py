"""Utility helpers for interacting with the OpenAI Chat Completions API."""

from __future__ import annotations

from typing import List

from openai import OpenAI


class OpenAIClient:
    """Thin wrapper around the OpenAI Python SDK."""

    def __init__(
        self, 
        api_key: str, 
        model: str, 
        temperature: float = 0.7, 
        max_tokens: int = 500,
        top_p: float = 1.0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0
    ):
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._top_p = top_p
        self._presence_penalty = presence_penalty
        self._frequency_penalty = frequency_penalty

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a single response text."""
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            top_p=self._top_p,
            presence_penalty=self._presence_penalty,
            frequency_penalty=self._frequency_penalty,
        )
        return response.choices[0].message.content.strip()

    def batch_generate(self, system_prompt: str, prompts: List[str]) -> List[str]:
        """Generate a list of responses – one per supplied user prompt."""
        results: List[str] = []
        for prompt in prompts:
            results.append(self.generate(system_prompt, prompt))
        return results

