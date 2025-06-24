import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Import custom modules
from utils.data_processor import DataProcessor
from pages.company_analysis import CompanyAnalysis
from pages.investor_analysis import InvestorAnalysis
from pages.general_analysis import GeneralAnalysis

# Configure page
st.set_page_config(
    page_title="Indian Startup Funding Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Main dashboard styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Enhanced sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Card styling for metrics */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #FF6B6B;
        margin: 0.5rem 0;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 1.5rem 0;
        padding: 0.5rem 0;
        border-bottom: 2px solid #f0f2f6;
    }
    
    /* Chart container styling */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e8e8e8;
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #e8e8e8;
        border-radius: 10px;
        transition: border-color 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #FF6B6B;
        box-shadow: 0 0 10px rgba(255, 107, 107, 0.3);
    }
    
    /* Info boxes */
    .info-box {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #4ECDC4;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Navigation active state */
    .nav-active {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
    
    /* Dashboard title styling */
    .dashboard-title {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Improved spacing */
    .element-container {
        margin: 0.5rem 0;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        border-top: 1px solid #e8e8e8;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the startup funding data"""
    try:
        # Try to load from the uploaded file path
        df = pd.read_csv('attached_assets/startup_cleaned_1750747387667.csv')
        return df
    except FileNotFoundError:
        st.error("Dataset file not found. Please ensure the CSV file is in the correct location.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def main():
    """Main application function"""
    
    # Add dashboard title with enhanced styling
    st.markdown('<h1 class="dashboard-title">🚀 Indian Startup Funding Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Comprehensive analysis of Indian startup ecosystem with interactive visualizations and insights</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        st.stop()
    
    # Initialize data processor
    data_processor = DataProcessor(df)
    processed_df = data_processor.process_data()
    
    # Enhanced sidebar navigation
    st.sidebar.markdown("## 🚀 Navigation")
    st.sidebar.markdown("---")
    
    # Navigation menu with enhanced styling
    page = st.sidebar.selectbox(
        "📊 Choose Analysis Type",
        ["🏢 Startup Analysis", "💼 Investor Analysis", "📊 General Analysis"],
        help="Select the type of analysis you want to explore"
    )
    
    # Enhanced dataset info section
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📈 Dataset Overview")
    
    # Create info cards in sidebar
    st.sidebar.markdown(f"""
    <div class="metric-card">
        <h4>📊 Total Records</h4>
        <h2>{len(processed_df):,}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"""
    <div class="metric-card">
        <h4>🏢 Unique Startups</h4>
        <h2>{processed_df['startup'].nunique():,}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"""
    <div class="metric-card">
        <h4>💼 Active Investors</h4>
        <h2>{processed_df['investors'].nunique():,}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"""
    <div class="info-box">
        <strong>📅 Date Range:</strong><br>
        {processed_df['date'].min().strftime('%B %d, %Y')} to<br>
        {processed_df['date'].max().strftime('%B %d, %Y')}
    </div>
    """, unsafe_allow_html=True)
    
    # Add feature highlights
    st.sidebar.markdown("---")
    st.sidebar.markdown("## ✨ Features")
    st.sidebar.markdown("""
    • **Startup Analysis**: Detailed company profiles and funding history
    • **Investor Insights**: Investment patterns and portfolio analysis  
    • **Market Trends**: Sector analysis and funding heatmaps
    • **Interactive Charts**: Dynamic visualizations with filters
    """)
    
    # Route to appropriate page with enhanced containers
    if page == "🏢 Startup Analysis":
        with st.container():
            company_analysis = CompanyAnalysis(processed_df)
            company_analysis.render()
    elif page == "💼 Investor Analysis":
        with st.container():
            investor_analysis = InvestorAnalysis(processed_df)
            investor_analysis.render()
    elif page == "📊 General Analysis":
        with st.container():
            general_analysis = GeneralAnalysis(processed_df)
            general_analysis.render()
    
    # Add footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>🚀 Indian Startup Funding Dashboard | Built with Streamlit & Plotly</p>
        <p>Data-driven insights for the Indian startup ecosystem</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
