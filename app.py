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
    
    # Load data
    df = load_data()
    if df is None:
        st.stop()
    
    # Initialize data processor
    data_processor = DataProcessor(df)
    processed_df = data_processor.process_data()
    
    # Sidebar navigation
    st.sidebar.title("🚀 Indian Startup Funding Dashboard")
    st.sidebar.markdown("---")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Choose Analysis Type",
        ["🏢 Startup Analysis", "💼 Investor Analysis", "📊 General Analysis"]
    )
    
    # Display current dataset info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Dataset Info")
    st.sidebar.write(f"**Total Records:** {len(processed_df):,}")
    st.sidebar.write(f"**Date Range:** {processed_df['date'].min().strftime('%Y-%m-%d')} to {processed_df['date'].max().strftime('%Y-%m-%d')}")
    st.sidebar.write(f"**Unique Companies:** {processed_df['startup'].nunique():,}")
    st.sidebar.write(f"**Unique Investors:** {processed_df['investors'].nunique():,}")
    
    # Route to appropriate page
    if page == "🏢 Startup Analysis":
        company_analysis = CompanyAnalysis(processed_df)
        company_analysis.render()
    elif page == "💼 Investor Analysis":
        investor_analysis = InvestorAnalysis(processed_df)
        investor_analysis.render()
    elif page == "📊 General Analysis":
        general_analysis = GeneralAnalysis(processed_df)
        general_analysis.render()

if __name__ == "__main__":
    main()
