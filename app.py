import streamlit as st
from utils.parser import extract_text_from_pdf, extract_text_from_image
from utils.analyzer import analyze_resume_for_all_roles
from utils.gpt_helper import get_hf_suggestions
import math

# ======================
# PAGE CONFIGURATION
# ======================
st.set_page_config(
    page_title="Resume Analyzer Pro",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ======================
# CUSTOM CSS
# ======================
def apply_custom_styles():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ======================
# SIDEBAR
# ======================
def show_sidebar():
    with st.sidebar:
        st.title("Resume Analyzer Pro")
        st.markdown("""
        **Upload your resume to:**
        - Discover best matching roles
        - Identify missing skills
        - Get AI-powered suggestions
        """)

        st.markdown("---")
        st.markdown("### Supported Roles:")
        st.markdown("""
        - AI/ML Engineer  
        - Data Scientist  
        - Data Analyst  
        - Research Engineer
        """)

        st.markdown("---")
        st.markdown("Made with ❤️ using Streamlit")

# ======================
# MAIN CONTENT
# ======================
def main():
    st.title("AI Resume Analyzer")
    st.markdown("Get instant feedback on how well your resume matches different tech roles.")

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF or image)",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Supported formats: PDF, PNG, JPG"
    )

    if uploaded_file:
        try:
            file_ext = uploaded_file.name.split(".")[-1].lower()
            if file_ext not in ["pdf", "png", "jpg", "jpeg"]:
                st.error("Unsupported file type uploaded.")
            else:
                analyze_resume(uploaded_file)
        except Exception as e:
            st.error(f"Unexpected error occurred: {e}")

# ======================
# RESUME ANALYSIS
# ======================
def analyze_resume(uploaded_file):
    file_ext = uploaded_file.name.split(".")[-1].lower()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Resume Preview")
        if file_ext == "pdf":
            st.image("https://cdn-icons-png.flaticon.com/512/337/337946.png", 
                     width=100, caption="PDF file")
        else:
            st.image(uploaded_file, use_column_width=True)

    with col2:
        with st.spinner("Analyzing your resume..."):
            try:
                text = extract_text_from_pdf(uploaded_file) if file_ext == "pdf" \
                    else extract_text_from_image(uploaded_file)

                # Optional: show raw extracted text
                with st.expander("🔍 Extracted Resume Text"):
                    st.write(text)

                analysis_results = analyze_resume_for_all_roles(text)
                suggestions = get_hf_suggestions(text, analysis_results)

                show_results(analysis_results, suggestions)
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.stop()

# ======================
# RESULTS DISPLAY
# ======================
def show_results(analysis_results, suggestions):
    st.success("Analysis completed successfully!")

    best_match = max(analysis_results.items(), key=lambda x: x[1]['match_percentage'])
    st.markdown(f"""
    <div class="card">
        <h3>Best Match</h3>
        <h2 style="color: #4f46e5">{best_match[0]} - {best_match[1]['match_percentage']}%</h2>
    </div>
    """, unsafe_allow_html=True)

    # Role Comparison with rows of 2 columns
    st.subheader("Role Comparison")
    roles = list(analysis_results.items())
    columns_per_row = 2
    rows = math.ceil(len(roles) / columns_per_row)

    for i in range(rows):
        cols = st.columns(columns_per_row)
        for j in range(columns_per_row):
            idx = i * columns_per_row + j
            if idx < len(roles):
                role, data = roles[idx]
                cols[j].metric(
                    label=role,
                    value=f"{data['match_percentage']}%",
                    delta="Strong" if data['match_percentage'] > 70 else None
                )

    # Skills Analysis
    with st.expander("Detailed Skills Analysis", expanded=True):
        selected_role = st.selectbox(
            "Select role to examine",
            options=list(analysis_results.keys()),
            index=list(analysis_results.keys()).index(best_match[0])
        )

        role_data = analysis_results[selected_role]
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**✅ Your Strengths**")
            if role_data['found_keywords']:
                for skill in role_data['found_keywords'][:10]:
                    st.markdown(f"- {skill}")
            else:
                st.markdown("_No strong skills found for this role._")

        with col4:
            st.markdown("**📌 Areas to Improve**")
            if role_data['missing_keywords']:
                for skill in role_data['missing_keywords'][:10]:
                    st.markdown(f"- {skill}")
            else:
                st.markdown("_No missing skills detected._")

    # AI Suggestions
    st.markdown(f"""
    <div class="card">
        <h3>AI Suggestions</h3>
        <div>{suggestions}</div>
    </div>
    """, unsafe_allow_html=True)

    # Download Report
    st.download_button(
        label="Download Analysis Report",
        data=generate_report(analysis_results, suggestions),
        file_name="resume_analysis.txt",
        mime="text/plain"
    )

# ======================
# REPORT GENERATION
# ======================
def generate_report(analysis_results, suggestions):
    report = []
    report.append("=== RESUME ANALYSIS REPORT ===\n")
    report.append("Role Matching Scores:")
    for role, data in analysis_results.items():
        report.append(f"- {role}: {data['match_percentage']}%")
    report.append("\nAI Recommendations:")
    report.extend(suggestions.split("\n"))
    return "\n".join(report)

# ======================
# RUN THE APP
# ======================
if __name__ == "__main__":
    apply_custom_styles()
    show_sidebar()
    main()
