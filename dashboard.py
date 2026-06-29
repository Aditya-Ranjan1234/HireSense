import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(
    page_title="HireSense - Discovery & Ranking Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling & Typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;600&display=swap');
    
    .stApp {
        background-color: #0d0f1a;
        color: #f7fafc;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
    }
    
    .main-title {
        font-size: 3rem;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 5px;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    
    /* Stats Panels */
    .metric-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .metric-val {
        font-size: 2.2rem;
        font-weight: bold;
        color: #00f2fe;
        font-family: 'Outfit', sans-serif;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Candidate Cards */
    .candidate-card {
        background: rgba(30, 41, 59, 0.45);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .candidate-card:hover {
        transform: translateY(-3px);
        border-color: rgba(0, 242, 254, 0.4);
        box-shadow: 0 12px 20px -10px rgba(0, 242, 254, 0.15);
        background: rgba(30, 41, 59, 0.6);
    }
    
    .rank-badge {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: #0d0f1a;
        padding: 6px 16px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        letter-spacing: 0.5px;
    }
    
    .score-badge {
        background: rgba(0, 242, 254, 0.08);
        color: #00f2fe;
        border: 1px solid rgba(0, 242, 254, 0.2);
        padding: 5px 15px;
        border-radius: 30px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-left: 8px;
    }

    .meta-tag {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: #cbd5e1;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        margin-right: 6px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">HireSense</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Native Recruitment Engine & Match Verification Dashboard</div>', unsafe_allow_html=True)

# Paths
base_dir = os.path.dirname(os.path.abspath(__file__))
path_csv = os.path.join(base_dir, "team_antigravity.csv")
path_jsonl = os.path.join(base_dir, "[PUB] India_runs_data_and_ai_challenge", "India_runs_data_and_ai_challenge", "candidates.jsonl")

if not os.path.exists(path_csv):
    st.error(f"Ranking CSV file not found at {path_csv}. Run rank.py first.")
else:
    df = pd.read_csv(path_csv)
    
    # Configuration and Architecture panel in sidebar
    st.sidebar.markdown("### HireSense Engine")
    st.sidebar.write("A hybrid retrieval pipeline leveraging keyword-overlap semantic models, experience matching, company pedigree, and platform behavioral signals.")
    
    # KPI Grid
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len(df)}</div><div class="metric-label">Candidates Evaluated</div></div>', unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{df.iloc[0]["score"]:.4f}</div><div class="metric-label">Top Fit Score</div></div>', unsafe_allow_html=True)
    with col_kpi3:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{df.iloc[-1]["score"]:.4f}</div><div class="metric-label">Rank 100 Score</div></div>', unsafe_allow_html=True)

    # Read profiles from candidates.jsonl if it exists.
    # If not found (e.g. on Streamlit Cloud), gracefully fallback to mock or sample details.
    top_100_ids = set(df['candidate_id'].tolist())
    top_profiles = {}
    
    if os.path.exists(path_jsonl):
        try:
            with open(path_jsonl, "r", encoding="utf-8") as f:
                for line in f:
                    c = json.loads(line)
                    cid = c["candidate_id"]
                    if cid in top_100_ids:
                        top_profiles[cid] = c
        except Exception:
            pass

    # Search Bar
    search_query = st.text_input("Filter candidates by ID, skills, or rationale...", "")
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df['candidate_id'].str.contains(search_query, case=False) |
            filtered_df['reasoning'].str.contains(search_query, case=False)
        ]

    st.markdown("### Match Discovery Results")
    
    for index, row in filtered_df.iterrows():
        cid = row['candidate_id']
        rank = row['rank']
        score = row['score']
        reasoning = row['reasoning']
        
        prof = top_profiles.get(cid, {})
        prof_detail = prof.get("profile", {})
        
        yoe_val = prof_detail.get('years_of_experience')
        yoe_str = f"{yoe_val:.1f} Years" if yoe_val is not None else "5+ Years"
        
        with st.container():
            st.markdown(f"""
            <div class="candidate-card">
                <div style="margin-bottom: 12px;">
                    <span class="rank-badge">RANK {rank}</span>
                    <span class="score-badge">FIT INDEX: {score:.4f}</span>
                </div>
                <h3 style="margin: 0 0 10px 0; font-size: 1.4rem;">{prof_detail.get('anonymized_name', 'Verified Candidate')} ({cid})</h3>
                <div style="margin-bottom: 15px;">
                    <span class="meta-tag">{prof_detail.get('current_title', 'AI Specialist')}</span>
                    <span class="meta-tag">{yoe_str} Experience</span>
                    <span class="meta-tag">{prof_detail.get('location', 'Tier 1 City, India')}</span>
                </div>
                <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.5; margin: 0 0 10px 0;">
                    <strong>Matching Rationale:</strong> {reasoning}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show details if profiles are available
            if prof:
                with st.expander("Explore Matching Metrics & History Breakdown"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("##### Candidate Work History")
                        for job in prof.get("career_history", []):
                            st.markdown(f"**{job['title']}** at *{job['company']}* ({job['duration_months']} mo)")
                            st.caption(job['description'])
                            st.markdown("---")
                    with col2:
                        st.markdown("##### Verified Skills Inventory")
                        skills_list = [f"{s['name']} ({s['proficiency']})" for s in prof.get("skills", [])]
                        st.write(", ".join(skills_list))
                        
                        st.markdown("##### Behavioral Signals & Availability")
                        sig = prof.get("redrob_signals", {})
                        st.write(f"- **Notice Period:** {sig.get('notice_period_days', 90)} Days")
                        st.write(f"- **Recruiter Engagement Rate:** {sig.get('recruiter_response_rate', 0.0) * 100:.1f}%")
                        st.write(f"- **GitHub Index Score:** {sig.get('github_activity_score', -1)}")
                        st.write(f"- **Last Platform Activity:** {sig.get('last_active_date', 'N/A')}")
