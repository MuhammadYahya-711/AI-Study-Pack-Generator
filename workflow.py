"""
Multi-stage AI workflow for the AI Study Pack Generator.

Stages:
1. Planning
2. Content Generation
3. Assessment
4. Review
5. Refinement

Context is passed from one stage to the next.
"""

import json
import time
from typing import Any, Callable, Dict, Optional

import requests

from prompts import (
    PLANNING_PROMPT,
    CONTENT_PROMPT,
    ASSESSMENT_PROMPT,
    REVIEW_PROMPT,
    REFINEMENT_PROMPT,
)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class WorkflowError(Exception):
    """Controlled workflow error shown to the Streamlit UI."""


def call_groq(
    prompt: str,
    api_key: str,
    model: str,
    temperature: float = 0.3,
    max_tokens: int = 5000,
    retries: int = 2,
) -> str:
    """Call Groq with timeout, retry, and rate-limit handling."""
    if not api_key:
        raise WorkflowError("Groq API key is missing.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert educational AI. "
                    "Be accurate, age-appropriate, clear, and useful for studying. "
                    "Follow output-format instructions exactly."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    last_error = "Unknown error"

    for attempt in range(retries + 1):
        try:
            response = requests.post(
                GROQ_URL,
                headers=headers,
                json=payload,
                timeout=90,
            )

            if response.status_code == 429:
                last_error = "Groq rate limit reached."
                if attempt < retries:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise WorkflowError(last_error)

            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            if not content or not content.strip():
                raise WorkflowError("The AI returned an empty response.")

            return content.strip()

        except requests.RequestException as exc:
            last_error = str(exc)
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
            else:
                raise WorkflowError(
                    f"Could not connect to Groq after retries: {last_error}"
                ) from exc

        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise WorkflowError(
                "Groq returned an unexpected response format."
            ) from exc

    raise WorkflowError(last_error)


def extract_json(text: str) -> Dict[str, Any]:
    """Safely parse JSON returned by an AI stage."""
    cleaned = text.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        result = json.loads(cleaned)
        if not isinstance(result, dict):
            raise WorkflowError("AI returned JSON, but it was not an object.")
        return result
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start != -1 and end > start:
            try:
                result = json.loads(cleaned[start:end + 1])
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                pass

    raise WorkflowError("AI returned invalid JSON for this workflow stage.")


def planning_stage(
    learner_profile: Dict[str, Any],
    api_key: str,
    model: str,
) -> Dict[str, Any]:
    prompt = PLANNING_PROMPT.format(
        learner_profile=json.dumps(learner_profile, indent=2, ensure_ascii=False)
    )
    return extract_json(
        call_groq(prompt, api_key, model, temperature=0.2, max_tokens=3000)
    )


def content_stage(
    learner_profile: Dict[str, Any],
    plan: Dict[str, Any],
    api_key: str,
    model: str,
) -> str:
    prompt = CONTENT_PROMPT.format(
        learner_profile=json.dumps(learner_profile, indent=2, ensure_ascii=False),
        plan=json.dumps(plan, indent=2, ensure_ascii=False),
    )
    return call_groq(
        prompt,
        api_key,
        model,
        temperature=0.4,
        max_tokens=6500,
    )


def assessment_stage(
    learner_profile: Dict[str, Any],
    plan: Dict[str, Any],
    draft: str,
    api_key: str,
    model: str,
) -> Dict[str, Any]:
    prompt = ASSESSMENT_PROMPT.format(
        learner_profile=json.dumps(learner_profile, indent=2, ensure_ascii=False),
        plan=json.dumps(plan, indent=2, ensure_ascii=False),
        draft=draft,
    )
    return extract_json(
        call_groq(prompt, api_key, model, temperature=0.1, max_tokens=4000)
    )


def review_stage(
    learner_profile: Dict[str, Any],
    plan: Dict[str, Any],
    draft: str,
    assessment: Dict[str, Any],
    api_key: str,
    model: str,
) -> Dict[str, Any]:
    prompt = REVIEW_PROMPT.format(
        learner_profile=json.dumps(learner_profile, indent=2, ensure_ascii=False),
        plan=json.dumps(plan, indent=2, ensure_ascii=False),
        draft=draft,
        assessment=json.dumps(assessment, indent=2, ensure_ascii=False),
    )
    return extract_json(
        call_groq(prompt, api_key, model, temperature=0.1, max_tokens=3500)
    )


def refinement_stage(
    learner_profile: Dict[str, Any],
    plan: Dict[str, Any],
    draft: str,
    assessment: Dict[str, Any],
    review: Dict[str, Any],
    api_key: str,
    model: str,
) -> str:
    prompt = REFINEMENT_PROMPT.format(
        learner_profile=json.dumps(learner_profile, indent=2, ensure_ascii=False),
        plan=json.dumps(plan, indent=2, ensure_ascii=False),
        draft=draft,
        assessment=json.dumps(assessment, indent=2, ensure_ascii=False),
        review=json.dumps(review, indent=2, ensure_ascii=False),
    )
    return call_groq(
        prompt,
        api_key,
        model,
        temperature=0.3,
        max_tokens=7000,
    )


def run_workflow(
    learner_profile: Dict[str, Any],
    api_key: str,
    model: str,
    progress_callback: Optional[Callable[[str, int], None]] = None,
) -> Dict[str, Any]:
    """
    Execute the complete workflow and return all stage outputs.

    Context flow:
    profile → plan → draft → assessment → review → final_pack
    """

    def progress(stage: str, value: int):
        if progress_callback:
            progress_callback(stage, value)

    context: Dict[str, Any] = {
        "learner_profile": learner_profile
    }

    progress("Planning", 10)
    context["plan"] = planning_stage(
        learner_profile, api_key, model
    )

    progress("Content Generation", 30)
    context["draft"] = content_stage(
        learner_profile,
        context["plan"],
        api_key,
        model,
    )

    progress("Assessment", 55)
    context["assessment"] = assessment_stage(
        learner_profile,
        context["plan"],
        context["draft"],
        api_key,
        model,
    )

    progress("Review", 75)
    context["review"] = review_stage(
        learner_profile,
        context["plan"],
        context["draft"],
        context["assessment"],
        api_key,
        model,
    )

    progress("Refinement", 100)
    context["final_pack"] = refinement_stage(
        learner_profile,
        context["plan"],
        context["draft"],
        context["assessment"],
        context["review"],
        api_key,
        model,
    )

    return context
