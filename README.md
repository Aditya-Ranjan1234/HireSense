# HireSense

Intelligent Candidate Discovery & Ranking pipeline matching candidates to the Redrob Senior AI Engineer job description.

## Structure
- `rank.py`: Local ranking script utilizing filtered keyword overlap matching and recruiter engagement signals. Runs within 1 minute.
- `dashboard.py`: Streamlit-based web dashboard displaying candidates and reasoning details.
- `team_antigravity.csv`: Submission format containing the top 100 candidate IDs, ranks, scores, and explanations.
- `submission_metadata.yaml`: Configuration metadata describing the sandbox setup and tools used.
- `[PUB] India_runs_data_and_ai_challenge/`: Local directory containing challenge specifications and candidate profiles (`candidates.jsonl`).

## Local Setup

1. Create and activate a python virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install pandas streamlit python-docx PyYAML
   ```
3. Run the ranker:
   ```bash
   python rank.py
   ```
4. Run the Streamlit Dashboard:
   ```bash
   streamlit run dashboard.py
   ```
