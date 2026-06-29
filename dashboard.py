import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(
    page_title="Redrob AI Candidate Ranking Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
<style>
    .main {
        background-color: #0f111a;
        color: #ffffff;
    }
    .stApp {
        background-color: #0f111a;
    }
    h1, h2, h3 {
        color: #00f2fe !important;
        font-family: 'Outfit', sans-serif;
    }
    .css-1d391kg {
        background-color: #171b2f;
    }
    .candidate-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.2s, border-color 0.2s;
    }
    .candidate-card:hover {
        transform: translateY(-2px);
        border-color: #00f2fe;
        background: rgba(255, 255, 255, 0.05);
    }
    .rank-badge {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: #0f111a;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .score-badge {
        background: rgba(0, 242, 254, 0.1);
        color: #00f2fe;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("Redrob AI Candidate Ranking Dashboard")
st.write("Visualizing the top 100 ranked candidates matching the founding team Senior AI Engineer JD.")

# Setup paths (using relative paths for streamlit hosting)
base_dir = os.path.dirname(os.path.abspath(__file__))
path_csv = os.path.join(base_dir, "team_antigravity.csv")
path_jsonl = os.path.join(base_dir, "[PUB] India_runs_data_and_ai_challenge", "India_runs_data_and_ai_challenge", "candidates.jsonl")

if not os.path.exists(path_csv):
    st.error(f"Ranking CSV not found at {path_csv}. Please run rank.py first.")
else:
    df = pd.read_csv(path_csv)
    
    # Load additional candidate details for full view
    st.sidebar.title("Configuration & Stats")
    st.sidebar.markdown(f"**Total Ranked:** {len(df)}")
    
    # Simple metrics
    top_score = df.iloc[0]['score']
    cutoff_score = df.iloc[-1]['score']
    
    st.sidebar.metric("Top Score", f"{top_score:.4f}")
    st.sidebar.metric("Rank 100 Score", f"{cutoff_score:.4f}")
    
    # Read the JSON details for search/filters
    # We will only load the top 100 profiles from JSONL to be fast
    top_100_ids = set(df['candidate_id'].tolist())
    top_profiles = {}
    
    with open(path_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            cid = c["candidate_id"]
            if cid in top_100_ids:
                top_profiles[cid] = c
                
    st.markdown("### Top Candidates List")
    
    # Pagination / search
    search_query = st.text_input("Search candidates by ID, skills, or titles", "")
    
    filtered_df = df.copy()
    if search_query:
        # Filter based on search query matching candidate ID or reasoning
        filtered_df = filtered_df[
            filtered_df['candidate_id'].str.contains(search_query, case=False) |
            filtered_df['reasoning'].str.contains(search_query, case=False)
        ]
        
    for index, row in filtered_df.iterrows():
        cid = row['candidate_id']
        rank = row['rank']
        score = row['score']
        reasoning = row['reasoning']
        
        prof = top_profiles.get(cid, {})
        prof_detail = prof.get("profile", {})
        
        with st.container():
            st.markdown(f"""
            <div class="candidate-card">
                <span class="rank-badge">Rank {rank}</span>
                <span class="score-badge">Score: {score:.4f}</span>
                <h3 style="margin-top: 10px; margin-bottom: 5px;">{prof_detail.get('anonymized_name', 'Anonymized Candidate')} ({cid})</h3>
                <p style="color: #a0aec0; font-size: 14px; margin-bottom: 10px;">
                    <strong>Headline:</strong> {prof_detail.get('headline', 'N/A')} | 
                    <strong>Experience:</strong> {prof_detail.get('years_of_experience', 'N/A')} Years | 
                    <strong>Location:</strong> {prof_detail.get('location', 'N/A')}
                </p>
                <p style="margin-bottom: 10px;"><strong>Rational Rationale:</strong> {reasoning}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show expander for deep breakdown
            with st.expander("Show complete profile and signals"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Career History")
                    for job in prof.get("career_history", []):
                        st.markdown(f"**{job['title']}** at *{job['company']}* ({job['duration_months']} months)")
                        st.write(job['description'])
                        st.markdown("---")
                with col2:
                    st.markdown("#### Declared Skills")
                    skills_list = [f"{s['name']} ({s['proficiency']})" for s in prof.get("skills", [])]
                    st.write(", ".join(skills_list))
                    
                    st.markdown("#### Redrob Engagement Signals")
                    sig = prof.get("redrob_signals", {})
                    st.write(f"- **Recruiter Response Rate:** {sig.get('recruiter_response_rate', 0.0) * 100:.1f}%")
                    st.write(f"- **Notice Period:** {sig.get('notice_period_days', 90)} days")
                    st.write(f"- **GitHub Activity Score:** {sig.get('github_activity_score', -1)}")
                    st.write(f"- **Willing to Relocate:** {sig.get('willing_to_relocate', False)}")
                    st.write(f"- **Last Active Date:** {sig.get('last_active_date', 'N/A')}")
