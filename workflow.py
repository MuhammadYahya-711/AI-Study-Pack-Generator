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

from groq import Groq

from prompts import (
    PLANNING_PROMPT,
    CONTENT_PROMPT,
    ASSESSMENT_PROMPT,
    REVIEW_PROMPT,
    REFINEMENT_PROMPT,
)


class WorkflowError(Exception):
    """Controlled workflow error shown to the Streamlit UI."""


# ---------------------------------------------------------
# GROQ API CALL
# ---------------------------------------------------------

def call_groq(
    prompt: str,
    api_key: str,
    model: str,
    temperature: float = 0.3,
    max_tokens: int = 5000,
    retries: int = 2,
) -> str:

    """Call Groq using the official Python SDK."""

    if not api_key or not api_key.strip():
        raise WorkflowError(
            "Groq API key is missing."
        )

    try:

        client = Groq(
            api_key=api_key.strip()
        )

    except Exception as exc:

        raise WorkflowError(
            f"Could not initialize the Groq client: {exc}"
        ) from exc

    last_error = "Unknown error"

    for attempt in range(retries + 1):

        try:

            response = client.chat.completions.create(
                model=model,

                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert educational AI. "
                            "Be accurate, age-appropriate, clear, "
                            "and useful for studying. "
                            "Follow output-format instructions exactly."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],

                temperature=temperature,

                max_completion_tokens=max_tokens,

                timeout=90,
            )

            if not response.choices:

                raise WorkflowError(
                    "The AI returned no choices."
                )

            content = response.choices[0].message.content

            if not content or not content.strip():

                raise WorkflowError(
                    "The AI returned an empty response."
                )

            return content.strip()

        except WorkflowError:

            raise

        except Exception as exc:

            last_error = str(exc)

            error_text = str(exc).lower()

            # These errors should not be retried.
            non_retryable = any(
                marker in error_text
                for marker in (
                    "401",
                    "403",
                    "404",
                    "invalid api key",
                    "authentication",
                    "permission",
                    "model not found",
                    "does not exist",
                )
            )

            if non_retryable or attempt >= retries:

                raise WorkflowError(
                    "Groq request failed. "
                    f"Model: {model}. "
                    f"Details: {last_error}"
                ) from exc

            time.sleep(
                2 * (attempt + 1)
            )

    raise WorkflowError(
        last_error
    )


# ---------------------------------------------------------
# JSON EXTRACTION
# ---------------------------------------------------------

def extract_json(text: str) -> Dict[str, Any]:

    """Safely parse JSON returned by an AI stage."""

    cleaned = text.strip()

    # Remove Markdown code fences
    if cleaned.startswith("```"):

        lines = cleaned.splitlines()

        if (
            lines
            and lines[0].strip().startswith("```")
        ):
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip() == "```"
        ):
            lines = lines[:-1]

        cleaned = "\n".join(
            lines
        ).strip()

    # Direct JSON parsing
    try:

        result = json.loads(
            cleaned
        )

        if not isinstance(result, dict):

            raise WorkflowError(
                "AI returned JSON, "
                "but it was not an object."
            )

        return result

    except json.JSONDecodeError:

        pass

    # Try to locate JSON inside extra text
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end > start:

        try:

            result = json.loads(
                cleaned[start:end + 1]
            )

            if isinstance(result, dict):

                return result

        except json.JSONDecodeError:

            pass

    raise WorkflowError(
        "AI returned invalid JSON "
        "for this workflow stage."
    )


# ---------------------------------------------------------
# STAGE 1 — PLANNING
# ---------------------------------------------------------

def planning_stage(
    learner_profile: Dict[str, Any],
    api_key: str,
    model: str,
) -> Dict[str, Any]:

    prompt = PLANNING_PROMPT.format(
        learner_profile=json.dumps(
            learner_profile,
            indent=2,
            ensure_ascii=False,
        )
    )

    result = call_groq(
        prompt=prompt,
        api_key=api_key,
        model=model,
        temperature=0.2,
        max_tokens=3000,
    )

    return extract_json(result)


# ---------------------------------------------------------
# STAGE 2 — CONTENT GENERATION
# ---------------------------------------------------------

def content_stage(
    learner_profile: Dict[str, Any],
    plan: Dict[str, Any],
    api_key: str,
    model: str,
) -> str:

    prompt = CONTENT_PROMPT.format(
        learner_profile=json.dumps(
            learner_profile,
            indent=2,
            ensure_ascii=False,
        ),

        plan=json.dumps(
            plan,
            indent=2,
            ensure_ascii=False,
        ),
    )

    return call_groq(
        prompt=prompt,
        api_key=api_key,
        model=model,
        temperature=0.4,
        max_tokens=6500,
    )


# ---------------------------------------------------------
# STAGE 3 — ASSESSMENT
# ---------------------------------------------------------

def assessment_stage(
    learner_profile: Dict[str, Any],
    plan: Dict[str, Any],
    draft: str,
    api_key: str,
    model: str,
) -> Dict[str, Any]:

    prompt = ASSESSMENT_PROMPT.format(
        learner_profile=json.dumps(
            learner_profile,
            indent=2,
            ensure_ascii=False,
        ),

        plan=json.dumps(
            plan,
            indent=2,
            ensure_ascii=False,
        ),

        draft=draft,
    )

    result = call_groq(
        prompt=prompt,
        api_key=api_key,
        model=model,
        temperature=0.1,
        max_tokens=4000,
    )

    return extract_json(result)


# ---------------------------------------------------------
# STAGE 4 — REVIEW
# ---------------------------------------------------------

def review_stage(
    learner_profile: Dict[str, Any],
    plan: Dict[str, Any],
    draft: str,
    assessment: Dict[str, Any],
    api_key: str,
    model: str,
) -> Dict[str, Any]:

    prompt = REVIEW_PROMPT.format(
        learner_profile=json.dumps(
            learner_profile,
            indent=2,
            ensure_ascii=False,
        ),

        plan=json.dumps(
            plan,
            indent=2,
            ensure_ascii=False,
        ),

        draft=draft,

        assessment=json.dumps(
            assessment,
            indent=2,
            ensure_ascii=False,
        ),
    )

    result = call_groq(
        prompt=prompt,
        api_key=api_key,
        model=model,
        temperature=0.1,
        max_tokens=3500,
    )

    return extract_json(result)


# ---------------------------------------------------------
# STAGE 5 — REFINEMENT
# ---------------------------------------------------------

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
        learner_profile=json.dumps(
            learner_profile,
            indent=2,
            ensure_ascii=False,
        ),

        plan=json.dumps(
            plan,
            indent=2,
            ensure_ascii=False,
        ),

        draft=draft,

        assessment=json.dumps(
            assessment,
            indent=2,
            ensure_ascii=False,
        ),

        review=json.dumps(
            review,
            indent=2,
            ensure_ascii=False,
        ),
    )

    return call_groq(
        prompt=prompt,
        api_key=api_key,
        model=model,
        temperature=0.3,
        max_tokens=7000,
    )


# ---------------------------------------------------------
# COMPLETE WORKFLOW
# ---------------------------------------------------------

def run_workflow(
    learner_profile: Dict[str, Any],
    api_key: str,
    model: str,
    progress_callback: Optional[
        Callable[[str, int], None]
    ] = None,
) -> Dict[str, Any]:

    """
    Execute the complete workflow.

    Context flow:

    learner profile
        ↓
    planning
        ↓
    content generation
        ↓
    assessment
        ↓
    review
        ↓
    refinement
        ↓
    final study pack
    """

    def progress(
        stage: str,
        value: int,
    ) -> None:

        if progress_callback:

            progress_callback(
                stage,
                value,
            )

    context: Dict[str, Any] = {
        "learner_profile": learner_profile
    }

    # Stage 1
    progress(
        "Planning",
        10,
    )

    context["plan"] = planning_stage(
        learner_profile,
        api_key,
        model,
    )

    # Stage 2
    progress(
        "Content Generation",
        30,
    )

    context["draft"] = content_stage(
        learner_profile,
        context["plan"],
        api_key,
        model,
    )

    # Stage 3
    progress(
        "Assessment",
        55,
    )

    context["assessment"] = assessment_stage(
        learner_profile,
        context["plan"],
        context["draft"],
        api_key,
        model,
    )

    # Stage 4
    progress(
        "Review",
        75,
    )

    context["review"] = review_stage(
        learner_profile,
        context["plan"],
        context["draft"],
        context["assessment"],
        api_key,
        model,
    )

    # Stage 5
    progress(
        "Refinement",
        100,
    )

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
