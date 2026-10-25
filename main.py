import argparse
import json
import sys
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


# ============================================================
# 1. Environment and LLM Configuration
# ============================================================

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# ============================================================
# 2. Structured Output Schemas
# ============================================================

class SkillList(BaseModel):
    """A flat list of skills."""

    skills: List[str] = Field(
        description="Skills mentioned, each normalized to lowercase"
    )


class SuggestionList(BaseModel):
    """One actionable suggestion per missing skill."""

    suggestions: List[str] = Field(
        description=(
            "Specific, actionable advice. "
            "Each suggestion should name a concrete course, "
            "project, or resource."
        )
    )


# ============================================================
# 3. Function 1 — Extract Skills from Resume
# ============================================================

def extract_skills(text: str) -> List[str]:
    """
    Extract professional skills, tools, competencies,
    and programming languages from resume text.
    """

    prompt = ChatPromptTemplate.from_template(
        """
You are an expert technical recruiter.

Extract every professional skill, tool, competency, and
programming language explicitly mentioned in the resume below.

Rules:
- Only include skills that actually appear in the text.
- Do not infer or guess skills that are not explicitly mentioned.
- Normalize skill names to lowercase.
- Remove unnecessary whitespace.
- Return skills only through the specified structured schema.

Resume:
---
{resume}
---
"""
    )

    # Create a chain that guarantees the expected output structure.
    chain = prompt | llm.with_structured_output(SkillList)

    result = chain.invoke({"resume": text})

    # Normalize and deduplicate while preserving order.
    seen = set()
    skills = []

    for skill in result.skills:
        skill = skill.strip().lower()

        if skill and skill not in seen:
            seen.add(skill)
            skills.append(skill)

    return skills


# ============================================================
# 4. Function 2 — Identify Missing Skills
# ============================================================

def identify_missing_skills(
    skills: List[str],
    target_skills: List[str]
) -> List[str]:
    """
    Return target skills that the candidate does not already have.

    Comparison is case-insensitive and ignores surrounding spaces.
    """

    have = {
        skill.strip().lower()
        for skill in skills
        if skill.strip()
    }

    missing = []
    seen = set()

    for target in target_skills:
        normalized_target = target.strip().lower()

        if (
            normalized_target
            and normalized_target not in have
            and normalized_target not in seen
        ):
            missing.append(normalized_target)
            seen.add(normalized_target)

    return missing


# ============================================================
# 5. Optional Function — Extract Target Skills from Job Description
# ============================================================

def get_target_skills_from_jd(
    job_description: str
) -> List[str]:
    """
    Extract key skills required for a role from its job description.

    This function allows the application to analyze a resume
    against a specific job description instead of using
    hardcoded target skills.
    """

    prompt = ChatPromptTemplate.from_template(
        """
You are an expert technical recruiter.

Identify the key professional and technical skills required
for the role described in the job description below.

Rules:
- Include only skills explicitly stated or clearly required.
- Include programming languages, frameworks, tools,
  platforms, and relevant technical competencies.
- Return skill names in lowercase.
- Do not return explanations.
- Avoid duplicate skills.

Job description:
---
{jd}
---
"""
    )

    chain = prompt | llm.with_structured_output(SkillList)

    result = chain.invoke({"jd": job_description})

    seen = set()
    target_skills = []

    for skill in result.skills:
        skill = skill.strip().lower()

        if skill and skill not in seen:
            seen.add(skill)
            target_skills.append(skill)

    return target_skills


# ============================================================
# 6. Function 3 — Suggest Improvements
# ============================================================

def suggest_improvements(missing: List[str]) -> List[str]:
    """
    Generate one specific, actionable suggestion
    for each missing skill.
    """

    if not missing:
        return []

    prompt = ChatPromptTemplate.from_template(
        """
You are an encouraging technical career coach.

For EACH missing skill below, generate exactly ONE
specific, actionable improvement suggestion.

Rules:
- Generate exactly one suggestion per missing skill.
- Keep the suggestions in the same order as the input skills.
- Name a concrete course, project, official documentation,
  or learning resource whenever possible.
- Explain briefly what the candidate should do.
- Avoid generic advice such as "learn this skill".
- Do not claim the candidate has completed anything.
- Return only the structured output requested.

Missing skills:
{missing}
"""
    )

    # A higher temperature can produce more varied suggestions.
    creative_llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7
    )

    chain = prompt | creative_llm.with_structured_output(
        SuggestionList
    )

    result = chain.invoke({
        "missing": ", ".join(missing)
    })

    suggestions = result.suggestions

    # Keep output aligned with missing skills.
    if len(suggestions) != len(missing):
        raise ValueError(
            "The LLM returned a different number of suggestions "
            "than the number of missing skills."
        )

    return suggestions


# ============================================================
# 7. Function 4 — Build Final Output
# ============================================================

def build_output(
    skills: List[str],
    missing: List[str],
    suggestions: List[str]
) -> dict:
    """
    Build the final JSON response.
    """

    return {
        "extracted_skills": skills,
        "missing_skills": missing,
        "suggestions": suggestions
    }


# ============================================================
# 8. Function 5 — Analyze Resume
# ============================================================

def analyze_resume(
    text: str,
    target_skills: List[str]
) -> dict:
    """
    Run the complete resume analysis pipeline.
    """

    skills = extract_skills(text)

    missing = identify_missing_skills(
        skills,
        target_skills
    )

    suggestions = suggest_improvements(missing)

    return build_output(
        skills,
        missing,
        suggestions
    )


# ============================================================
# 9. Main Function — Command-Line Interface
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="AI Resume Analyzer using LangChain and OpenAI"
    )

    # Accept resume text from a file.
    parser.add_argument(
        "--file",
        type=str,
        help="Path to a text file containing the resume"
    )

    # Alternatively, accept resume text directly.
    parser.add_argument(
        "--text",
        type=str,
        help="Resume text provided directly as a command-line argument"
    )

    # Optionally accept a job description file.
    parser.add_argument(
        "--jd-file",
        type=str,
        help="Path to a text file containing the job description"
    )

    # Alternatively, accept a job description directly.
    parser.add_argument(
        "--jd",
        type=str,
        help="Job description provided directly as an argument"
    )

    # Optional comma-separated target skills.
    parser.add_argument(
        "--target-skills",
        type=str,
        help="Comma-separated target skills"
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # Read resume text
    # --------------------------------------------------------

    if args.file:
        try:
            with open(
                args.file,
                "r",
                encoding="utf-8"
            ) as file:
                resume_text = file.read()

        except OSError as exc:
            print(
                f"Error reading resume file: {exc}",
                file=sys.stderr
            )
            sys.exit(1)

    elif args.text:
        resume_text = args.text

    else:
        parser.error(
            "Provide either --file or --text."
        )

    if not resume_text.strip():
        parser.error("The resume text is empty.")

    # --------------------------------------------------------
    # Determine target skills
    # --------------------------------------------------------

    target_skills = []

    if args.target_skills:
        target_skills = [
            skill.strip().lower()
            for skill in args.target_skills.split(",")
            if skill.strip()
        ]

    elif args.jd_file:
        try:
            with open(
                args.jd_file,
                "r",
                encoding="utf-8"
            ) as file:
                job_description = file.read()

        except OSError as exc:
            print(
                f"Error reading job description file: {exc}",
                file=sys.stderr
            )
            sys.exit(1)

        if not job_description.strip():
            parser.error("The job description file is empty.")

        target_skills = get_target_skills_from_jd(
            job_description
        )

    elif args.jd:
        target_skills = get_target_skills_from_jd(args.jd)

    else:
        parser.error(
            "Provide --target-skills, --jd-file, or --jd."
        )

    # --------------------------------------------------------
    # Run analysis
    # --------------------------------------------------------

    try:
        result = analyze_resume(
            resume_text,
            target_skills
        )

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False
            )
        )

    except Exception as exc:
        print(
            f"Resume analysis failed: {exc}",
            file=sys.stderr
        )
        sys.exit(1)


# ============================================================
# 10. Application Entry Point
# ============================================================

if __name__ == "__main__":
    main()
    