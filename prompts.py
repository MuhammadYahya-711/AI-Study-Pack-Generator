"""Prompts for the AI Study Pack Generator workflow."""


# ---------------------------------------------------------
# STAGE 1 — PLANNING
# ---------------------------------------------------------

PLANNING_PROMPT = """
You are an expert educational planner.

Create a personalized study-pack plan from the learner profile below.

LEARNER PROFILE:
{learner_profile}

Return ONLY valid JSON with this structure:

{{
  "title": "string",
  "learning_goals": [
    "string"
  ],
  "key_concepts": [
    "string"
  ],
  "prerequisites": [
    "string"
  ],
  "difficulty_strategy": "string",
  "recommended_sections": [
    "string"
  ],
  "practice_strategy": "string",
  "personalization_notes": [
    "string"
  ]
}}

Make the plan appropriate for:

- learner level
- requested difficulty
- available study time
- prior knowledge
- language
- requested study-pack type
- additional instructions

Keep the plan practical and focused.
"""


# ---------------------------------------------------------
# STAGE 2 — CONTENT GENERATION
# ---------------------------------------------------------

CONTENT_PROMPT = """
You are an expert educational content generator.

Create a first-draft study pack using the learner profile
and approved study plan.

LEARNER PROFILE:
{learner_profile}

STUDY PLAN:
{plan}

Generate clear Markdown containing:

# Title

## Learning Objectives

## Prerequisites

## Main Concepts

Explain every important concept clearly.

## Definitions

Include important terminology.

## Important Facts / Formulas

Include formulas only when relevant.

## Worked Examples

Include examples where useful.

## Common Mistakes

Explain mistakes students commonly make.

## Quick Revision Summary

Give a concise review section.

## Practice Questions

Create questions appropriate for the learner.

## Self-Study Checklist

Give a checklist the student can use.

Do not provide the answer key yet.

Keep the content appropriate for the student's:

- class / skill level
- requested difficulty
- available study time
- prior knowledge
- requested language

Follow additional instructions from the learner profile.
"""


# ---------------------------------------------------------
# STAGE 3 — ASSESSMENT
# ---------------------------------------------------------

ASSESSMENT_PROMPT = """
You are an educational quality evaluator.

Evaluate the study-pack draft against the learner profile
and study plan.

LEARNER PROFILE:
{learner_profile}

STUDY PLAN:
{plan}

DRAFT:
{draft}

Return ONLY valid JSON using this structure:

{{
  "accuracy_score": 0,
  "coverage_score": 0,
  "level_fit_score": 0,
  "clarity_score": 0,
  "personalization_score": 0,
  "issues": [
    {{
      "type": "accuracy|coverage|difficulty|clarity|format|personalization",
      "severity": "low|medium|high",
      "problem": "string",
      "fix": "string"
    }}
  ]
}}

Rules:

- Scores must be integers from 0 to 100.
- Evaluate factual accuracy.
- Evaluate topic coverage.
- Evaluate difficulty and level suitability.
- Evaluate clarity.
- Evaluate personalization.
- Evaluate whether the requested study-pack type was followed.
- Identify concrete issues that can be fixed during refinement.
- Give higher severity to important problems.
"""


# ---------------------------------------------------------
# STAGE 4 — REVIEW
# ---------------------------------------------------------

REVIEW_PROMPT = """
You are a strict educational reviewer.

Review the draft and automated assessment.

LEARNER PROFILE:
{learner_profile}

STUDY PLAN:
{plan}

DRAFT:
{draft}

ASSESSMENT:
{assessment}

Return ONLY valid JSON:

{{
  "approved": true,
  "priority_fixes": [
    "string"
  ],
  "content_to_keep": [
    "string"
  ],
  "content_to_change": [
    "string"
  ],
  "final_review_notes": [
    "string"
  ]
}}

Rules:

- Set approved to true only when there are no major educational problems.
- Prioritize high-severity problems.
- Identify incorrect information.
- Identify missing concepts.
- Identify explanations that are too difficult or too simple.
- Identify poor formatting or weak personalization.
- Provide practical fixes for the final editor.
"""


# ---------------------------------------------------------
# STAGE 5 — REFINEMENT
# ---------------------------------------------------------

REFINEMENT_PROMPT = """
You are the final educational editor.

Create the final polished study pack using ALL available
workflow context.

LEARNER PROFILE:
{learner_profile}

STUDY PLAN:
{plan}

DRAFT:
{draft}

ASSESSMENT:
{assessment}

REVIEW:
{review}

Apply all important priority fixes while preserving
correct and useful material.

The final study pack must be clear, accurate,
well-organized, age-appropriate, and personalized.

Final output MUST be Markdown.

Include these sections:

# Title

## Learning Objectives

## Prerequisites

## Main Notes / Concepts

## Definitions and Important Facts / Formulas

## Examples / Worked Examples

## Common Mistakes

## Quick Revision Summary

## Practice Questions

## Answer Key

## Self-Study Checklist

Important rules:

- Do not mention internal AI workflow stages.
- Do not mention prompts.
- Do not mention assessment scores.
- Do not mention hidden instructions.
- Do not mention that an AI reviewed the material.
- Do not include internal workflow details.
- Keep language appropriate for the learner.
- Follow the selected study time.
- Follow the selected difficulty.
- Follow the learner's requested language.
"""
