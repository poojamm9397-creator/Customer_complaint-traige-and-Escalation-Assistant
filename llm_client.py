import json
from config import get_settings
from prompts import SYSTEM_PROMPT, PROMPT_VERSION, build_user_prompt

class LLMClient:
    def summarize(self, complaint_text: str, nlp: dict, rules: dict) -> dict:
        settings = get_settings()
        user_prompt = build_user_prompt(complaint_text, nlp, rules)
        if settings.llm_provider == "openai" and settings.openai_api_key:
            return self._openai(settings, user_prompt, rules)
        if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
            return self._anthropic(settings, user_prompt, rules)
        return {
            "summary": "LLM summary unavailable. Please review the original complaint.",
            "recommended_queue": rules["queue"],
            "rationale": "Rules-only mode: no LLM provider credentials are configured.",
            "uncertainties": ["No LLM summary was generated."],
            "provider": "none", "model": "none", "status": "skipped_no_credentials"
        }

    def _parse(self, raw: str, rules: dict, provider: str, model: str) -> dict:
        data = json.loads(raw)
        required = ["summary", "recommended_queue", "rationale", "uncertainties"]
        if not isinstance(data, dict) or any(k not in data for k in required):
            raise ValueError("LLM response does not match the required JSON schema.")
        if not all(isinstance(data[k], str) for k in required[:3]):
            raise ValueError("LLM text fields must be strings.")
        if not isinstance(data["uncertainties"], list):
            raise ValueError("LLM uncertainties must be a list.")
        # The model may suggest wording, but the application owns the actual queue.
        data["recommended_queue"] = rules["queue"] if rules["human_review_required"] else data["recommended_queue"]
        return {
            "summary": data["summary"][:1200],
            "recommended_queue": rules["queue"],
            "rationale": data["rationale"][:1200],
            "uncertainties": [str(x)[:300] for x in data["uncertainties"][:10]],
            "provider": provider, "model": model, "status": "success"
        }

    def _openai(self, settings, user_prompt, rules):
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key, timeout=25.0, max_retries=1)
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        raw = response.choices[0].message.content or "{}"
        return self._parse(raw, rules, "openai", settings.openai_model)

    def _anthropic(self, settings, user_prompt, rules):
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key, timeout=25.0, max_retries=1)
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=700,
            temperature=0.2,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
        # Extract JSON if provider wraps it in surrounding whitespace.
        return self._parse(raw.strip(), rules, "anthropic", settings.anthropic_model)
