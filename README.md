# AI-Resume-Analyzer

An LLM-powered command-line application that analyzes a resume against a target skill list or a job description. It uses **Python**, **LangChain**, **OpenAI**, and **Pydantic structured output** to extract skills, identify gaps, and recommend practical next steps.

## Features

- **Resume skill extraction** — extracts explicitly mentioned professional skills, tools, competencies, and programming languages.
- **Skill normalization** — converts extracted skills to lowercase, trims whitespace, and removes exact duplicates.
- **Job-description analysis** — optionally extracts target skills from a job description using the LLM.
- **Skill-gap analysis** — compares resume skills with target skills and lists missing skills.
- **Actionable recommendations** — generates one learning or project suggestion for each missing skill.
- **Structured JSON output** — returns extracted skills, missing skills, and suggestions in a consistent JSON structure.
- **Command-line interface** — accepts resume text from a `.txt` file or directly from a command-line argument.

## How It Works

```text
Resume + Job Description / Target Skills
                  |
                  v
          Extract Resume Skills
                  |
                  v
       Pydantic Structured Output
                  |
                  v
       Compare Against Target Skills
                  |
                  v
           Identify Skill Gaps
                  |
                  v
       Generate Actionable Suggestions
                  |
                  v
             JSON Results
```

## Tech Stack

- Python
- [LangChain](https://www.langchain.com/)
- [LangChain OpenAI integration](https://python.langchain.com/docs/integrations/chat/openai/)
- [OpenAI API](https://platform.openai.com/docs/overview)
- [Pydantic](https://docs.pydantic.dev/)
- `python-dotenv`
- `argparse` (Python standard library)
- JSON (Python standard library)

## Project Structure

```text
Resume_Analyzer/
├── main.py
├── resume.txt                 # Your resume input (local; do not commit personal data)
├── job_description.txt        # Optional job description input
├── .env                       # API key (never commit)
├── .gitignore
└── README.md
```

The `resume.txt` and `job_description.txt` files are example/local inputs. Create them yourself; they are not required to be committed to GitHub.

## Prerequisites

- Python 3.10 or later recommended.
- An OpenAI API key with API access and available billing/credits as required by your account.
- Internet access to call the OpenAI API.

## Setup

### 1. Clone the repository

Replace `<your-repository-url>` with your Git repository URL:

```bash
git clone <your-repository-url>
cd AI-Resume-Analyzer
```

If you have already created the project locally, open its directory in VS Code and skip this step.

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install langchain langchain-openai langchain-core pydantic python-dotenv
```

### 4. Configure the OpenAI API key

Create a `.env` file in the project root:

```dotenv
OPENAI_API_KEY=your_actual_openai_api_key
```

Replace the placeholder with your key. Do not add quotes unless your environment requires them, and never commit this file.

### 5. Create a `.gitignore`

Add the following:

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
resume.txt
job_description.txt
```

This helps prevent accidentally committing secrets and personal resume data.

## Usage

Run commands from the directory containing `resume_analyzer.py`.

### Option 1: Analyze a resume against a job description file

Create `resume.txt` and `job_description.txt`, then run:

```bash
python main.py --file resume.txt --jd-file job_description.txt
```

The application extracts resume skills, extracts target skills from the job description, identifies gaps, and prints JSON results.

### Option 2: Provide target skills manually

```bash
python main.py --file resume.txt --target-skills "python,langchain,langgraph,rag,fastapi,openai,docker,aws"
```

Use this when you already know the required skills for a role.

### Option 3: Pass resume text directly

```bash
python main.py --text "Python developer with SQL, Pandas, NumPy, LangChain and FastAPI experience" --target-skills "python,langchain,langgraph,rag,aws"
```

For longer resumes, prefer the `--file` option to avoid command-line quoting and length issues.

### Option 4: Pass a job description directly

```bash
python main.py --file resume.txt --jd "We need a Python engineer with FastAPI, LangChain, RAG, Docker, and AWS experience."
```

### Arguments

| Argument | Required? | Description |
|---|---|---|
| `--file` | One of `--file` or `--text` | Path to a text file containing the resume |
| `--text` | One of `--file` or `--text` | Resume text supplied directly |
| `--jd-file` | One of `--jd-file`, `--jd`, or `--target-skills` | Path to a job-description text file |
| `--jd` | One of `--jd-file`, `--jd`, or `--target-skills` | Job description supplied directly |
| `--target-skills` | One of the target-skill options | Comma-separated list of required skills |

If multiple target-skill options are supplied, the script uses this precedence: `--target-skills`, then `--jd-file`, then `--jd`.

## Example Output

The exact output depends on the supplied resume, job description, and model response. A typical response has this shape:

```json
{
  "extracted_skills": [
    "python",
    "sql",
    "pandas",
    "numpy",
    "langchain",
    "openai",
    "fastapi"
  ],
  "missing_skills": [
    "langgraph",
    "rag",
    "docker",
    "aws"
  ],
  "suggestions": [
    "Complete the official LangGraph tutorials and build a small workflow with conditional routing.",
    "Build a retrieval-augmented generation application using LangChain and a vector store.",
    "Containerize the FastAPI application with Docker and document how to build and run the image.",
    "Deploy a small application to AWS and document the deployment steps."
  ]
}
```

This is illustrative output, not a guaranteed result.

## Key Implementation Concepts

### 1. Structured output with Pydantic

The application defines `SkillList` and `SuggestionList` Pydantic models. LangChain's `with_structured_output()` asks the model to return data matching the required schema, reducing the need for fragile regular-expression parsing.

### 2. Skill normalization

Extracted and target skills are converted to lowercase and stripped of surrounding whitespace. Exact duplicates are removed while preserving the original order.

**Current limitation:** this is exact string matching, not semantic matching. For example, `rest api` and `rest apis` may be treated as different skills. Synonyms and related technologies are not automatically reconciled.

### 3. Job-description skill extraction

When `--jd-file` or `--jd` is used, the LLM extracts the target skills from the job description. Review the extracted list for accuracy, since model output can omit, misinterpret, or overgeneralize requirements.

### 4. Recommendations

The application generates one suggestion per missing skill. Recommendations are AI-generated and should be reviewed for relevance, availability, and accuracy.

## Troubleshooting

### `OPENAI_API_KEY` error

- Check that `.env` exists in the project root.
- Verify the variable is spelled `OPENAI_API_KEY`.
- Confirm the key is active and has API access.
- Restart the terminal or rerun the application after changing environment variables.

### `ModuleNotFoundError`

Activate the intended virtual environment, then reinstall dependencies:

```bash
python -m pip install langchain langchain-openai langchain-core pydantic python-dotenv
```

### API, quota, or rate-limit errors

Check your OpenAI API account, model access, billing/usage limits, and network connection. API usage may incur charges.

### Empty or unexpected results

- Confirm the input file contains readable text.
- Check whether the resume explicitly mentions the skills you expect to be extracted.
- Review the job description and target skill list.
- Remember that LLM output can vary and is not a deterministic parser.

## Limitations and Responsible Use

- This is a **skill-gap assistant**, not a complete ATS simulator or a hiring decision system.
- It does not currently parse PDF or DOCX files; provide plain text in a `.txt` file or use `--text`.
- It does not calculate an ATS compatibility score or evaluate work history, education, achievements, or resume formatting.
- Extracted skills and suggestions can be incomplete or incorrect. Verify the output before making career decisions.
- Do not upload confidential, sensitive, or third-party personal information unless you are authorized to do so.
- Treat the result as guidance, not as a guarantee of interview selection or employment.

## Future Enhancements

- Add PDF and DOCX resume parsing.
- Build a Streamlit dashboard for resume uploads and visual skill-gap reports.
- Add an explainable match score based on transparent, configurable rules.
- Improve skill matching with aliases, taxonomies, and semantic similarity.
- Export analysis reports to PDF or downloadable JSON.
- Add automated tests, logging, and API error handling.
- Support batch analysis against multiple job descriptions.

## License

No license has been specified yet. If you plan to publish or distribute this project, add a suitable `LICENSE` file and update this section.

---

**Disclaimer:** This project is intended for learning and career-development assistance. It does not guarantee ATS results, interview calls, or job placement.
