import json
import os
import re
import csv
from datetime import datetime

base_dir = r"d:\6th Sem\Redrob AI\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge"
path_jsonl = os.path.join(base_dir, "candidates.jsonl")
output_csv = r"d:\6th Sem\Redrob AI\team_antigravity.csv"

# Target terms for TF-IDF / BM25-like heuristic matching
TARGET_SKILLS = {
    "embeddings", "retrieval", "vector database", "faiss", "milvus", "qdrant", "pinecone", 
    "weaviate", "opensearch", "elasticsearch", "sentence-transformers", "llm", "fine-tuning", 
    "lora", "qlora", "peft", "ranking", "learning-to-rank", "ndcg", "mrr", "map", "a/b testing",
    "python", "nlp"
}

SERVICE_COMPANIES = {"tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini", "mphasis", "mindtree"}

def is_honeypot(candidate):
    yoe = candidate["profile"]["years_of_experience"]
    
    # Rule 1: Single job duration exceeds total yoe
    for job in candidate.get("career_history", []):
        dur = job.get("duration_months", 0) / 12.0
        if dur > yoe + 0.2:
            return True
            
    # Rule 2: Title vs description mismatch
    for job in candidate.get("career_history", []):
        title = job.get("title", "").lower()
        desc = job.get("description", "").lower()
        
        if "devops engineer" in title and ("frontend" in desc or "react" in desc or "angular" in desc or "html" in desc):
            return True
        elif "mobile developer" in title and ("test automation" in desc or "qa engineering" in desc or "qa/test" in desc):
            return True
        elif "net developer" in title and ("cloud infrastructure" in desc or "devops" in desc or "terraform" in desc):
            return True
        elif "hr manager" in title and ("marketing leadership" in desc or "demand-generation" in desc or "seo" in desc or "content writing" in desc):
            return True
        elif "civil engineer" in title and ("enterprise sales" in desc or "sales cycle" in desc):
            return True
        elif "graphic designer" in title and ("content writing" in desc or "seo strategy" in desc or "writer" in desc or "brand design" in desc):
            return True
        elif "business analyst" in title and ("customer support" in desc or "tickets" in desc):
            return True
        elif "accountant" in title and ("content writing" in desc or "hr manager" in desc):
            return True
        elif "marketing manager" in title and ("operations management" in desc or "warehouse" in desc):
            return True
            
    return False

def calculate_score(c):
    # Instead of embeddings, we use semantic word-overlap and keyword scoring:
    summary = c["profile"]["summary"].lower()
    headline = c["profile"]["headline"].lower()
    history_descs = " ".join([j["description"].lower() for j in c.get("career_history", [])])
    history_titles = " ".join([j["title"].lower() for j in c.get("career_history", [])])
    
    full_text = f"{summary} {headline} {history_descs} {history_titles}"
    
    # 1. Target keyword counts (mimicking embedding similarity)
    kw_hits = 0
    kws = ["ranking", "recommendation", "embeddings", "retrieval", "vector database", 
           "faiss", "milvus", "qdrant", "pinecone", "weaviate", "learning-to-rank", 
           "rag", "evaluation", "ab test", "a/b test", "ndcg", "mrr"]
    for kw in kws:
        if kw in full_text:
            kw_hits += 1
            if kw in headline or kw in history_titles:
                kw_hits += 0.5 # boost if keywords are in title or headline
                
    sim_score = min(kw_hits / 8.0, 1.0) # maxes out at 8 keywords/boosts
    score = sim_score * 0.40
    
    # 2. Skill Overlap (20%)
    c_skills = {s["name"].lower() for s in c.get("skills", [])}
    matched_skills = TARGET_SKILLS.intersection(c_skills)
    skill_score = min(len(matched_skills) / 6.0, 1.0)
    score += skill_score * 0.20
    
    # 3. Experience Match & Service Company Penalty (20%)
    yoe = c["profile"]["years_of_experience"]
    if 5.0 <= yoe <= 9.0:
        exp_factor = 1.0
    elif yoe < 5.0:
        exp_factor = max(0.0, yoe / 5.0)
    else:
        exp_factor = max(0.0, 1.0 - (yoe - 9.0) / 10.0)
        
    companies = [j["company"].lower() for j in c.get("career_history", [])]
    has_product_experience = any(all(s not in comp for s in SERVICE_COMPANIES) for comp in companies)
    pedigree_factor = 1.0 if has_product_experience else 0.2
    
    score += (exp_factor * pedigree_factor) * 0.20
    
    # 4. Behavioral Signals (20%)
    signals = c.get("redrob_signals", {})
    response_rate = signals.get("recruiter_response_rate", 0.0)
    
    notice = signals.get("notice_period_days", 90)
    if notice <= 30:
        notice_factor = 1.0
    elif notice <= 60:
        notice_factor = 0.7
    elif notice <= 90:
        notice_factor = 0.4
    else:
        notice_factor = 0.1
        
    github = signals.get("github_activity_score", -1)
    github_factor = (github / 100.0) if github >= 0 else 0.0
    
    last_active = signals.get("last_active_date", "2025-01-01")
    if last_active.startswith("2026"):
        recency_factor = 1.0
    elif last_active.startswith("2025-1"):
        recency_factor = 0.7
    else:
        recency_factor = 0.3
        
    behavioral_score = (response_rate * 0.4) + (notice_factor * 0.3) + (github_factor * 0.1) + (recency_factor * 0.2)
    score += behavioral_score * 0.20
    
    return score, matched_skills, yoe

def generate_reasoning(c, matched_skills, yoe):
    prof = c["profile"]
    title = prof.get("current_title", "Engineer")
    skills_str = ", ".join(list(matched_skills)[:4])
    companies = [j["company"] for j in c.get("career_history", [])[:2]]
    comp_str = " & ".join(companies)
    
    reason = f"{yoe:.1f} YoE {title} with experience in {skills_str}. Previously at {comp_str}. "
    
    signals = c.get("redrob_signals", {})
    notice = signals.get("notice_period_days", 90)
    rr = signals.get("recruiter_response_rate", 0.0)
    
    if notice <= 30 and rr > 0.5:
        reason += f"Highly active with quick {notice}-day notice."
    elif rr > 0.6:
        reason += "Strong engagement history with recruiters."
    else:
        reason += f"{notice}-day notice period."
        
    return reason

def main():
    print("Loading candidate records & filtering honeypots...")
    ranked_list = []
    
    with open(path_jsonl, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            c = json.loads(line)
            if is_honeypot(c):
                continue
            
            score, matched_skills, yoe = calculate_score(c)
            reason = generate_reasoning(c, matched_skills, yoe)
            
            ranked_list.append({
                "candidate_id": c["candidate_id"],
                "score": round(score, 4),
                "reasoning": reason
            })
            
            if idx > 0 and idx % 20000 == 0:
                print(f"Processed {idx} records...")

    print("Sorting candidates...")
    # Tiebreak: score descending, then candidate_id ascending
    ranked_list.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    
    top_100 = ranked_list[:100]
    
    print(f"Writing top 100 to {output_csv}...")
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for rank_idx, item in enumerate(top_100, 1):
            writer.writerow([
                item["candidate_id"],
                rank_idx,
                item["score"],
                item["reasoning"]
            ])
            
    print("Ranking complete!")

if __name__ == "__main__":
    main()
