import json
import os

base_dir = r"d:\6th Sem\Redrob AI\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge"
path_jsonl = os.path.join(base_dir, "candidates.jsonl")

# Let's inspect the entire candidate profile for CAND_0016000 or CAND_0003582 or CAND_0033817
ids_to_inspect = {"CAND_0003582", "CAND_0016000", "CAND_0033817"}

with open(path_jsonl, "r", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line)
        if c["candidate_id"] in ids_to_inspect:
            print("CANDIDATE DETAILS FOR:", c["candidate_id"])
            print("Skills:")
            for s in c["skills"]:
                if s["proficiency"] == "expert" and s["duration_months"] == 0:
                    print("  ", s)
            print("History:")
            for job in c["career_history"]:
                print(f"  {job['company']} | {job['title']} | Duration: {job['duration_months']} mo")
                print(f"    Description: {job['description']}")
            print("=" * 60)
