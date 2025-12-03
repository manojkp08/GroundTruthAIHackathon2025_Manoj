import streamlit as st
import pandas as pd
from fpdf import FPDF
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

# --- CONFIGURATION ---
st.set_page_config(page_title="AdPulse | Automated Insights", page_icon="📊", layout="centered")

# --- Gemini API KEY from ENV ---
api_key = os.getenv("GEMINI_API_KEY")

# --- CORE LOGIC (PANDAS) ---
def analyze_campaign_data(df):
    """
    Performs deterministic calculations on the raw data.
    """
    try:
        # 1. Clean & Validate
        required_cols = ['Impressions', 'Clicks', 'Spend', 'Conversions']
        if not all(col in df.columns for col in required_cols):
            return None, "Missing required columns. Please upload a valid AdTech CSV."

        # 2. Aggregations
        total_spend = df['Spend'].sum()
        total_clicks = df['Clicks'].sum()
        total_conversions = df['Conversions'].sum()
        total_impressions = df['Impressions'].sum()

        # 3. Derived Metrics (KPIs)
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        cpa = total_spend / total_conversions if total_conversions > 0 else 0
        cpc = total_spend / total_clicks if total_clicks > 0 else 0
        
        # 4. Identify Winners & Losers
        df['ROAS_Proxy'] = df['Conversions'] / df['Spend'] # Simple Return on Ad Spend proxy
        top_campaign = df.loc[df['Conversions'].idxmax()]['Campaign_Name']
        most_efficient = df.loc[df['ROAS_Proxy'].idxmax()]['Platform']

        stats = {
            "Total Spend": f"${total_spend:,.2f}",
            "Total Conversions": f"{total_conversions:,}",
            "Global CTR": f"{ctr:.2f}%",
            "Avg CPA": f"${cpa:.2f}",
            "Top Campaign": top_campaign,
            "Best Platform": most_efficient
        }
        return stats, None

    except Exception as e:
        return None, f"Data Processing Error: {str(e)}"

# --- AI INSUGHT GENERATOR ---

# --- PDF GENERATION ---

# --- MAIN APPLICATION UI ---
def main():
    st.title("📊 AdPulse: Automated Insight Engine")
    st.markdown("""
    **Transform raw campaign data into executive decisions in seconds.**
    Upload your weekly CSV to generate a PDF report with AI-driven analysis.
    """)
    
    # 1. File Upload
    uploaded_file = st.file_uploader("Upload CSV Data", type=['csv'])
    
    if not uploaded_file:
        st.info("👆 Please upload a CSV file to begin analysis.")

        # Optional: Add a link to sample data if you host it
        # st.markdown("[Download Sample CSV](https://github.com/...)")

        return
    
    # 2. Process Data
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("### 🔍 Data Preview")
        st.dataframe(df.head(5))
        
        if st.button("🚀 Generate Executive Report"):
            with st.spinner("Analyzing performance metrics with Gemini..."):
                # Step A: Numeric Analysis
                stats, error = analyze_campaign_data(df)
                
                if error:
                    st.error(error)
                    return

                # Step B: AI Narrative
                # summary = generate_executive_summary(stats, df.head()) ---> #TODO
                
                # Step C: Display Results
                st.success("Analysis Complete!")
                
                # Metrics Display
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Spend", stats['Total Spend'])
                col2.metric("Conversions", stats['Total Conversions'])
                col3.metric("CPA", stats['Avg CPA'])

                # pdf_bytes = create_pdf(stats, summary) ---> #TODO
                
                st.download_button(
                    label="📥 Download Official PDF Report",
                    # data=pdf_bytes, #TODO
                    file_name="Executive_Ad_Report.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    main()