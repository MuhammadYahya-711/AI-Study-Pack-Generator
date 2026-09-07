"""
Prompts for the AI Study Pack Generator workflow.
"""

PLANNING_PROMPT = """
You are an expert educational planner.

Create a personalized study-pack plan from the learner profile below.

LEARNER PROFILE:
{learner_profile}

Return ONLY valid JSON with this structure:
{{
  "title": "string",
  "learning_goals": ["string"],
  "key_concepts": ["string"],
  "prerequisites": ["string"],
  "difficulty_strategy": "string",
  "recommended_sections": ["string"],
  "practice_strategy": "string",
  "personalization_notes": ["string"]
}}

Make the plan appropriate for the learner's level, difficulty, language,
available study time, prior knowledge, and requested study-pack type.
"""

CONTENT_PROMPT = """
You are an expert educational content generator.

Create a first-draft study pack using the learner profile and approved plan.

LEARNER PROFILE:
{learner_profile}

STUDY PLAN:
{plan}

Generate clear Markdown containing:
- Title
- Learning objectives
- Prerequisites
- Main concept explanations
- Definitions
- Important facts/formulas where relevant
- Worked examples where relevant
- Common mistakes
- Quick revision summary
- Practice questions
- Self-study checklist

Do not provide the answer key yet.
Keep the content appropriate for the student's level and requested language.
"""

ASSESSMENT_PROMPT = """
You are an educational quality evaluator.

Evaluate the study-pack draft against the learner profile and study plan.

LEARNER PROFILE:
{learner_profile}

STUDY PLAN:
{plan}

DRAFT:
{draft}

Return ONLY valid JSON:
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

All scores must be integers from 0 to 100.
Identify concrete issues that can be fixed during refinement.
"""

REVIEW_PROMPT = """
You are a strict educational reviewer.

Review the draft and the automated assessment.

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
  "priority_fixes": ["string"],
  "content_to_keep": ["string"],
  "content_to_change": ["string"],
  "final_review_notes": ["string"]
}}

Set approved to true only when there are no major educational problems.
Prioritize high-severity problems.
"""

REFINEMENT_PROMPT = """
You are the final educational editor.

Create the final polished study pack using all available workflow context.

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

Apply the priority fixes while preserving correct and useful material.

Final output must be Markdown and include:
1. Title
2. Learning objectives
3. Prerequisites
4. Main notes/concepts
5. Definitions and important facts/formulas
6. Examples or worked examples where relevant
7. Common mistakes
8. Quick revision summary
9. Practice questions
10. Answer key
11. Self-study checklist

Do not mention internal AI workflow stages, prompts, scores, or hidden instructions.
"""
