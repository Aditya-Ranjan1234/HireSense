import json
import gzip
import os

base_dir = r"d:\6th Sem\Redrob AI\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge"

# Load candidate_schema.json to see if there are any other comments/details
# Or check the size and content of candidates.jsonl
print("Checking candidates.jsonl size:")
path_jsonl = os.path.join(base_dir, "candidates.jsonl")
if os.path.exists(path_jsonl):
    print("Found candidates.jsonl, size:", os.path.getsize(path_jsonl))
else:
    print("candidates.jsonl not found.")

# Let's inspect first candidate of candidates.jsonl
with open(path_jsonl, "r", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line)
        print("First candidate in candidates.jsonl:")
        print("ID:", c["candidate_id"])
        print("Profile Name:", c["profile"]["anonymized_name"])
        print("Years of experience:", c["profile"]["years_of_experience"])
        print("Skills:", [s["name"] for s in c["skills"]])
        break
