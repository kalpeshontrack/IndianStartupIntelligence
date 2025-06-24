import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re

# Configure page
st.set_page_config(
    page_title="Indian Startup Funding Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data Processing Class
class DataProcessor:
    def __init__(self, df):
        self.df = df.copy()
    
    def process_data(self):
        """Process and clean the startup funding data"""
        df = self.df.copy()
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Clean startup names
        df['startup'] = df['startup'].astype(str).str.strip()
        df['startup'] = df['startup'].str.replace(r'^https?://[^\s]+', '', regex=True)
        df['startup'] = df['startup'].str.replace(r'["\']', '', regex=True)
        
        # Clean amount column
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df['amount'] = df['amount'].fillna(0)
        
        # Clean and standardize other columns
        for col in ['vertical', 'subvertical', 'city', 'investors', 'round']:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('nan', 'Unknown')
            df[col] = df[col].replace('', 'Unknown')
        
        # Standardize city names
        df['city'] = df['city'].str.title()
        city_mapping = {
            'Bengaluru': 'Bangalore',
            'Kormangala': 'Bangalore',
            'Gurgaon': 'Gurugram',
            'New Delhi': 'Delhi',
            'Noida': 'Delhi NCR',
            'Faridabad': 'Delhi NCR'
        }
        df['city'] = df['city'].replace(city_mapping)
        
        # Create additional derived columns
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['month_year'] = df['date'].dt.to_period('M')
        
        # Clean funding round names
        round_mapping = {
            'Seed Round': 'Seed',
            'Seed Funding': 'Seed',
            'Seed': 'Seed',
            'Angel Round': 'Angel',
            'Angel': 'Angel',
            'Series A': 'Series A',
            'Series B': 'Series B',
            'Series C': 'Series C',
            'Series D': 'Series D',
            'Series E': 'Series E',
            'Series F': 'Series F',
            'Series G': 'Series G',
            'Series H': 'Series H',
            'Pre-Series A': 'Pre-Series A',
            'Pre-series A': 'Pre-Series A',
            'Private Equity Round': 'Private Equity',
            'Private Equity': 'Private Equity',
            'Debt Funding': 'Debt',
            'Bridge Round': 'Bridge',
            'Venture Round': 'Venture',
            'Corporate Round': 'Corporate'
        }
        df['round'] = df['round'].replace(round_mapping)
        
        # Remove rows with missing critical data
        df = df.dropna(subset=['date', 'startup'])
        df = df[df['startup'] != 'Unknown']
        
        # Sort by date
        df = df.sort_values('date', ascending=False)
        
        return df
    
    def get_company_info(self, df, company_name):
        """Get detailed information about a specific company"""
        company_data = df[df['startup'].str.contains(company_name, case=False, na=False)]
        
        if company_data.empty:
            return None
        
        # Get the most recent entry for basic info
        latest_entry = company_data.iloc[0]
        
        info = {
            'name': latest_entry['startup'],
            'industry': latest_entry['vertical'],
            'subindustry': latest_entry['subvertical'],
            'location': latest_entry['city'],
            'total_funding': company_data['amount'].sum(),
            'funding_rounds': len(company_data),
            'last_funding_date': company_data['date'].max(),
            'first_funding_date': company_data['date'].min(),
            'funding_history': company_data[['date', 'round', 'amount', 'investors']].sort_values('date')
        }
        
        return info
    
    def get_investor_info(self, df, investor_name):
        """Get detailed information about a specific investor"""
        # Split investors column and create expanded dataframe for analysis
        investor_data = []
        for _, row in df.iterrows():
            investors = str(row['investors']).split(',')
            for investor in investors:
                investor = investor.strip()
                if investor and investor.lower() != 'unknown':
                    investor_data.append({
                        'investor': investor,
                        'startup': row['startup'],
                        'date': row['date'],
                        'amount': row['amount'],
                        'round': row['round'],
                        'vertical': row['vertical'],
                        'city': row['city'],
                        'year': row['year']
                    })
        
        investor_df = pd.DataFrame(investor_data)
        
        # Filter for specific investor
        investor_investments = investor_df[
            investor_df['investor'].str.contains(investor_name, case=False, na=False)
        ]
        
        if investor_investments.empty:
            return None
        
        info = {
            'name': investor_name,
            'total_investments': len(investor_investments),
            'total_amount_invested': investor_investments['amount'].sum(),
            'avg_investment': investor_investments['amount'].mean(),
            'recent_investments': investor_investments.sort_values('date', ascending=False).head(10),
            'biggest_investments': investor_investments.nlargest(10, 'amount'),
            'sectors': investor_investments['vertical'].value_counts(),
            'stages': investor_investments['round'].value_counts(),
            'cities': investor_investments['city'].value_counts(),
            'yearly_investments': investor_investments.groupby('year').agg({
                'startup': 'count',
                'amount': 'sum'
            }).reset_index()
        }
        
        return info
    
    def find_similar_companies(self, df, company_name, limit=5):
        """Find companies similar to the given company"""
        company_data = df[df['startup'].str.contains(company_name, case=False, na=False)]
        
        if company_data.empty:
            return []
        
        # Get company characteristics
        target_vertical = company_data['vertical'].iloc[0]
        target_subvertical = company_data['subvertical'].iloc[0]
        target_city = company_data['city'].iloc[0]
        
        # Find similar companies
        similar = df[
            (df['vertical'] == target_vertical) |
            (df['subvertical'] == target_subvertical) |
            (df['city'] == target_city)
        ]
        
        # Exclude the target company
        similar = similar[~similar['startup'].str.contains(company_name, case=False, na=False)]
        
        # Group by startup and get summary
        similar_summary = similar.groupby('startup').agg({
            'amount': 'sum',
            'vertical': 'first',
            'subvertical': 'first',
            'city': 'first',
            'date': 'max'
        }).reset_index()
        
        similar_summary = similar_summary.sort_values('amount', ascending=False).head(limit)
        
        return similar_summary.to_dict('records')
    
    def find_similar_investors(self, df, investor_name, limit=5):
        """Find investors similar to the given investor"""
        # Create investor analysis dataframe
        investor_data = []
        for _, row in df.iterrows():
            investors = str(row['investors']).split(',')
            for investor in investors:
                investor = investor.strip()
                if investor and investor.lower() != 'unknown':
                    investor_data.append({
                        'investor': investor,
                        'vertical': row['vertical'],
                        'round': row['round'],
                        'amount': row['amount']
                    })
        
        investor_df = pd.DataFrame(investor_data)
        
        # Get target investor characteristics
        target_investments = investor_df[
            investor_df['investor'].str.contains(investor_name, case=False, na=False)
        ]
        
        if target_investments.empty:
            return []
        
        target_sectors = set(target_investments['vertical'].value_counts().head(3).index)
        target_stages = set(target_investments['round'].value_counts().head(3).index)
        
        # Find similar investors
        all_investors = investor_df.groupby('investor').agg({
            'vertical': lambda x: set(x.value_counts().head(3).index),
            'round': lambda x: set(x.value_counts().head(3).index),
            'amount': ['sum', 'count']
        }).reset_index()
        
        all_investors.columns = ['investor', 'top_sectors', 'top_stages', 'total_amount', 'investment_count']
        
        # Calculate similarity score
        def similarity_score(row):
            sector_overlap = len(target_sectors.intersection(row['top_sectors'])) / len(target_sectors.union(row['top_sectors']))
            stage_overlap = len(target_stages.intersection(row['top_stages'])) / len(target_stages.union(row['top_stages']))
            return (sector_overlap + stage_overlap) / 2
        
        all_investors['similarity'] = all_investors.apply(similarity_score, axis=1)
        
        # Exclude the target investor
        similar_investors = all_investors[
            ~all_investors['investor'].str.contains(investor_name, case=False, na=False)
        ]
        
        similar_investors = similar_investors.sort_values('similarity', ascending=False).head(limit)
        
        return similar_investors[['investor', 'total_amount', 'investment_count', 'similarity']].to_dict('records')

# Visualization Class
class Visualizations:
    @staticmethod
    def create_pie_chart(data, values, names, title, height=400):
        """Create an interactive pie chart"""
        fig = px.pie(
            data, 
            values=values, 
            names=names, 
            title=title,
            height=height
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=True)
        return fig
    
    @staticmethod
    def create_bar_chart(data, x, y, title, color=None, height=400):
        """Create an interactive bar chart"""
        fig = px.bar(
            data, 
            x=x, 
            y=y, 
            title=title,
            color=color,
            height=height
        )
        fig.update_layout(xaxis_tickangle=-45)
        return fig
    
    @staticmethod
    def create_line_chart(data, x, y, title, color=None, height=400):
        """Create an interactive line chart"""
        fig = px.line(
            data, 
            x=x, 
            y=y, 
            title=title,
            color=color,
            height=height,
            markers=True
        )
        return fig
    
    @staticmethod
    def create_funnel_chart(data, x, y, title, height=400):
        """Create a funnel chart for funding stages"""
        fig = go.Figure(go.Funnel(
            y=data[y],
            x=data[x],
            textinfo="value+percent initial"
        ))
        
        fig.update_layout(
            title=title,
            height=height
        )
        return fig

# Load Data Function
@st.cache_data
def load_data():
    """Load and cache the startup funding data"""
    try:
        df = pd.read_csv('attached_assets/startup_cleaned_1750747387667.csv')
        return df
    except FileNotFoundError:
        st.error("Dataset file not found. Please ensure the CSV file is in the correct location.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Company Analysis Functions
def display_company_details(df, company_name, data_processor, viz):
    """Display detailed analysis for selected company"""
    company_info = data_processor.get_company_info(df, company_name)
    
    if not company_info:
        st.error("Company not found in the dataset.")
        return
    
    # Company header
    st.header(f"📊 {company_info['name']}")
    
    # Basic information cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Industry", company_info['industry'], help="Primary industry vertical")
    
    with col2:
        st.metric("Sub-Industry", company_info['subindustry'], help="Specific sub-vertical")
    
    with col3:
        st.metric("Location", company_info['location'], help="Primary business location")
    
    with col4:
        st.metric("Funding Rounds", f"{company_info['funding_rounds']}", help="Total number of funding rounds")
    
    # Funding metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Funding", f"₹{company_info['total_funding']:.2f}M", help="Total funding raised across all rounds")
    
    with col2:
        if company_info['funding_rounds'] > 0:
            avg_funding = company_info['total_funding'] / company_info['funding_rounds']
            st.metric("Avg. Round Size", f"₹{avg_funding:.2f}M", help="Average funding per round")
    
    with col3:
        if pd.notna(company_info['last_funding_date']):
            st.metric("Last Funding", company_info['last_funding_date'].strftime('%Y-%m-%d'), help="Date of most recent funding")
    
    st.markdown("---")
    
    # Funding rounds details
    st.subheader("💰 Funding History")
    
    if not company_info['funding_history'].empty:
        funding_df = company_info['funding_history'].copy()
        funding_df['date'] = funding_df['date'].dt.strftime('%Y-%m-%d')
        funding_df['amount'] = funding_df['amount'].apply(lambda x: f"₹{x:.2f}M" if x > 0 else "Undisclosed")
        
        # Display funding table
        st.dataframe(
            funding_df[['date', 'round', 'amount', 'investors']],
            column_config={
                "date": "Date",
                "round": "Round Type",
                "amount": "Amount",
                "investors": "Investors"
            },
            use_container_width=True
        )
        
        # Funding timeline chart
        if len(funding_df) > 1:
            timeline_data = company_info['funding_history'].copy()
            timeline_data = timeline_data[timeline_data['amount'] > 0]  # Only include disclosed amounts
            
            if not timeline_data.empty:
                fig = viz.create_line_chart(
                    timeline_data,
                    x='date',
                    y='amount',
                    title=f"{company_name} - Funding Timeline",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No detailed funding history available for this company.")
    
    st.markdown("---")
    
    # Similar companies
    st.subheader("🔍 Similar Companies")
    similar_companies = data_processor.find_similar_companies(df, company_name)
    
    if similar_companies:
        similar_df = pd.DataFrame(similar_companies)
        similar_df['amount'] = similar_df['amount'].apply(lambda x: f"₹{x:.2f}M")
        similar_df['date'] = pd.to_datetime(similar_df['date']).dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            similar_df[['startup', 'vertical', 'city', 'amount', 'date']],
            column_config={
                "startup": "Company",
                "vertical": "Industry",
                "city": "Location",
                "amount": "Total Funding",
                "date": "Last Funding"
            },
            use_container_width=True
        )
    else:
        st.info("No similar companies found based on industry, sub-industry, or location.")

def display_company_overview(df, viz):
    """Display overview of all companies"""
    st.subheader("📈 Company Overview")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_companies = df['startup'].nunique()
        st.metric("Total Companies", f"{total_companies:,}")
    
    with col2:
        total_funding = df['amount'].sum()
        st.metric("Total Funding", f"₹{total_funding:,.0f}M")
    
    with col3:
        avg_funding = df['amount'].mean()
        st.metric("Avg. Funding", f"₹{avg_funding:.2f}M")
    
    with col4:
        max_funding = df['amount'].max()
        st.metric("Largest Round", f"₹{max_funding:,.0f}M")
    
    st.markdown("---")
    
    # Industry distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏭 Industry Distribution")
        industry_counts = df['vertical'].value_counts().head(10)
        fig = viz.create_pie_chart(
            pd.DataFrame({'industry': industry_counts.index, 'count': industry_counts.values}),
            values='count',
            names='industry',
            title="Top 10 Industries by Company Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Industry Funding")
        industry_funding = df.groupby('vertical')['amount'].sum().sort_values(ascending=False).head(10)
        fig = viz.create_bar_chart(
            pd.DataFrame({'industry': industry_funding.index, 'funding': industry_funding.values}),
            x='industry',
            y='funding',
            title="Top 10 Industries by Total Funding"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # City-wise analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏙️ City Distribution")
        city_counts = df['city'].value_counts().head(10)
        fig = viz.create_bar_chart(
            pd.DataFrame({'city': city_counts.index, 'count': city_counts.values}),
            x='city',
            y='count',
            title="Top 10 Cities by Company Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💼 Funding Stages")
        stage_counts = df['round'].value_counts().head(10)
        fig = viz.create_pie_chart(
            pd.DataFrame({'stage': stage_counts.index, 'count': stage_counts.values}),
            values='count',
            names='stage',
            title="Funding Stages Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top funded companies
    st.subheader("🏆 Top Funded Companies")
    top_companies = df.groupby('startup').agg({
        'amount': 'sum',
        'vertical': 'first',
        'city': 'first',
        'date': 'max'
    }).reset_index()
    
    top_companies = top_companies.sort_values('amount', ascending=False).head(20)
    top_companies['amount'] = top_companies['amount'].apply(lambda x: f"₹{x:.2f}M")
    top_companies['date'] = pd.to_datetime(top_companies['date']).dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        top_companies[['startup', 'vertical', 'city', 'amount', 'date']],
        column_config={
            "startup": "Company",
            "vertical": "Industry",
            "city": "Location",
            "amount": "Total Funding",
            "date": "Last Funding"
        },
        use_container_width=True
    )

# Investor Analysis Functions
def display_investor_details(df, investor_name, data_processor, viz):
    """Display detailed analysis for selected investor"""
    investor_info = data_processor.get_investor_info(df, investor_name)
    
    if not investor_info:
        st.error("Investor not found in the dataset.")
        return
    
    # Investor header
    st.header(f"💼 {investor_info['name']}")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Investments", f"{investor_info['total_investments']:,}", help="Number of companies invested in")
    
    with col2:
        st.metric("Total Amount", f"₹{investor_info['total_amount_invested']:,.0f}M", help="Total amount invested across all deals")
    
    with col3:
        st.metric("Avg Investment", f"₹{investor_info['avg_investment']:.2f}M", help="Average investment per deal")
    
    with col4:
        if not investor_info['recent_investments'].empty:
            last_investment = investor_info['recent_investments'].iloc[0]['date']
            st.metric("Last Investment", last_investment.strftime('%Y-%m-%d'), help="Date of most recent investment")
    
    st.markdown("---")
    
    # Recent investments
    st.subheader("📈 Recent Investments")
    if not investor_info['recent_investments'].empty:
        recent_df = investor_info['recent_investments'].copy()
        recent_df['date'] = recent_df['date'].dt.strftime('%Y-%m-%d')
        recent_df['amount'] = recent_df['amount'].apply(lambda x: f"₹{x:.2f}M" if x > 0 else "Undisclosed")
        
        st.dataframe(
            recent_df[['startup', 'date', 'round', 'amount', 'vertical', 'city']],
            column_config={
                "startup": "Company",
                "date": "Date",
                "round": "Round",
                "amount": "Amount",
                "vertical": "Industry",
                "city": "Location"
            },
            use_container_width=True
        )
    
    # Biggest investments
    st.subheader("💰 Biggest Investments")
    if not investor_info['biggest_investments'].empty:
        biggest_df = investor_info['biggest_investments'].copy()
        biggest_df['date'] = biggest_df['date'].dt.strftime('%Y-%m-%d')
        biggest_df['amount'] = biggest_df['amount'].apply(lambda x: f"₹{x:.2f}M")
        
        st.dataframe(
            biggest_df[['startup', 'amount', 'date', 'round', 'vertical', 'city']],
            column_config={
                "startup": "Company",
                "amount": "Amount",
                "date": "Date",
                "round": "Round",
                "vertical": "Industry",
                "city": "Location"
            },
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Investment patterns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🏭 Sector Distribution")
        if not investor_info['sectors'].empty:
            sectors_df = pd.DataFrame({
                'sector': investor_info['sectors'].index,
                'count': investor_info['sectors'].values
            })
            fig = viz.create_pie_chart(
                sectors_df,
                values='count',
                names='sector',
                title="Investment by Sector"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Stage Distribution")
        if not investor_info['stages'].empty:
            stages_df = pd.DataFrame({
                'stage': investor_info['stages'].index,
                'count': investor_info['stages'].values
            })
            fig = viz.create_pie_chart(
                stages_df,
                values='count',
                names='stage',
                title="Investment by Stage"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.subheader("🏙️ City Distribution")
        if not investor_info['cities'].empty:
            cities_df = pd.DataFrame({
                'city': investor_info['cities'].index,
                'count': investor_info['cities'].values
            })
            fig = viz.create_pie_chart(
                cities_df,
                values='count',
                names='city',
                title="Investment by City"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Year over year investment trend
    st.subheader("📈 Year over Year Investment Trend")
    if not investor_info['yearly_investments'].empty:
        yearly_df = investor_info['yearly_investments']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = viz.create_line_chart(
                yearly_df,
                x='year',
                y='startup',
                title="Number of Investments by Year"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = viz.create_line_chart(
                yearly_df,
                x='year',
                y='amount',
                title="Investment Amount by Year (₹M)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Similar investors
    st.subheader("🔍 Similar Investors")
    similar_investors = data_processor.find_similar_investors(df, investor_name)
    
    if similar_investors:
        similar_df = pd.DataFrame(similar_investors)
        similar_df['total_amount'] = similar_df['total_amount'].apply(lambda x: f"₹{x:.0f}M")
        similar_df['similarity'] = similar_df['similarity'].apply(lambda x: f"{x:.2%}")
        
        st.dataframe(
            similar_df[['investor', 'total_amount', 'investment_count', 'similarity']],
            column_config={
                "investor": "Investor",
                "total_amount": "Total Invested",
                "investment_count": "# Investments",
                "similarity": "Similarity Score"
            },
            use_container_width=True
        )
    else:
        st.info("No similar investors found based on investment patterns.")

def display_investor_overview(df, viz):
    """Display overview of all investors"""
    st.subheader("📊 Investor Overview")
    
    # Create investor analysis dataframe
    investor_data = []
    for _, row in df.iterrows():
        investors = str(row['investors']).split(',')
        for investor in investors:
            investor = investor.strip()
            if investor and investor.lower() != 'unknown':
                investor_data.append({
                    'investor': investor,
                    'startup': row['startup'],
                    'amount': row['amount'],
                    'vertical': row['vertical'],
                    'round': row['round'],
                    'city': row['city'],
                    'year': row['year'],
                    'date': row['date']
                })
    
    investor_df = pd.DataFrame(investor_data)
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        unique_investors = investor_df['investor'].nunique()
        st.metric("Total Investors", f"{unique_investors:,}")
    
    with col2:
        total_investments = len(investor_df)
        st.metric("Total Investments", f"{total_investments:,}")
    
    with col3:
        avg_investment = investor_df['amount'].mean()
        st.metric("Avg Investment", f"₹{avg_investment:.2f}M")
    
    with col4:
        max_investment = investor_df['amount'].max()
        st.metric("Largest Investment", f"₹{max_investment:,.0f}M")
    
    st.markdown("---")
    
    # Top investors by different metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Most Active Investors")
        most_active = investor_df['investor'].value_counts().head(15)
        fig = viz.create_bar_chart(
            pd.DataFrame({'investor': most_active.index, 'investments': most_active.values}),
            x='investments',
            y='investor',
            title="Top 15 Most Active Investors"
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Biggest Investors by Amount")
        biggest_investors = investor_df.groupby('investor')['amount'].sum().sort_values(ascending=False).head(15)
        fig = viz.create_bar_chart(
            pd.DataFrame({'investor': biggest_investors.index, 'amount': biggest_investors.values}),
            x='amount',
            y='investor',
            title="Top 15 Investors by Total Amount"
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Investment patterns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏭 Preferred Sectors")
        sector_investments = investor_df['vertical'].value_counts().head(10)
        fig = viz.create_pie_chart(
            pd.DataFrame({'sector': sector_investments.index, 'count': sector_investments.values}),
            values='count',
            names='sector',
            title="Top 10 Sectors by Investment Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Preferred Stages")
        stage_investments = investor_df['round'].value_counts().head(10)
        fig = viz.create_pie_chart(
            pd.DataFrame({'stage': stage_investments.index, 'count': stage_investments.values}),
            values='count',
            names='stage',
            title="Investment Distribution by Stage"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Geographic preferences
    st.subheader("🗺️ Geographic Investment Preferences")
    city_investments = investor_df['city'].value_counts().head(15)
    fig = viz.create_bar_chart(
        pd.DataFrame({'city': city_investments.index, 'investments': city_investments.values}),
        x='city',
        y='investments',
        title="Top 15 Cities by Investment Count"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Investment trends over time
    st.subheader("📈 Investment Trends Over Time")
    yearly_trends = investor_df.groupby('year').agg({
        'investor': 'count',
        'amount': 'sum'
    }).reset_index()
    yearly_trends.columns = ['year', 'investment_count', 'total_amount']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = viz.create_line_chart(
            yearly_trends,
            x='year',
            y='investment_count',
            title="Number of Investments Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = viz.create_line_chart(
            yearly_trends,
            x='year',
            y='total_amount',
            title="Total Investment Amount Over Time (₹M)"
        )
        st.plotly_chart(fig, use_container_width=True)

# General Analysis Functions
def display_summary_cards(df):
    """Display summary metrics cards"""
    st.subheader("📈 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_startups = df['startup'].nunique()
        st.metric("Total Startups", f"{total_startups:,}", help="Unique startups that received funding")
    
    with col2:
        total_funding = df['amount'].sum()
        st.metric("Total Funding", f"₹{total_funding:,.0f}M", help="Total funding amount raised")
    
    with col3:
        avg_funding = df['amount'].mean()
        st.metric("Avg Funding", f"₹{avg_funding:.2f}M", help="Average funding per round")
    
    with col4:
        max_funding = df['amount'].max()
        max_startup = df.loc[df['amount'].idxmax(), 'startup']
        st.metric("Largest Round", f"₹{max_funding:,.0f}M", help=f"Largest funding round by {max_startup}")
    
    with col5:
        total_investors = len(set([
            investor.strip() 
            for investors_str in df['investors'].dropna() 
            for investor in str(investors_str).split(',')
            if investor.strip() and investor.strip().lower() != 'unknown'
        ]))
        st.metric("Active Investors", f"{total_investors:,}", help="Unique investors in the period")

def display_mom_analysis(df, viz):
    """Display month-over-month analysis"""
    st.subheader("📅 Month-over-Month Analysis")
    
    # Prepare monthly data
    monthly_data = df.groupby(df['date'].dt.to_period('M')).agg({
        'startup': 'count',
        'amount': 'sum'
    }).reset_index()
    monthly_data['date'] = monthly_data['date'].dt.to_timestamp()
    monthly_data.columns = ['date', 'deal_count', 'total_amount']
    
    if len(monthly_data) > 1:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = viz.create_line_chart(
                monthly_data,
                x='date',
                y='deal_count',
                title="Monthly Deal Count",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = viz.create_line_chart(
                monthly_data,
                x='date',
                y='total_amount',
                title="Monthly Funding Amount (₹M)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Combined chart
        fig = go.Figure()
        
        # Add deal count
        fig.add_trace(go.Scatter(
            x=monthly_data['date'],
            y=monthly_data['deal_count'],
            mode='lines+markers',
            name='Deal Count',
            yaxis='y',
            line=dict(color='blue')
        ))
        
        # Add funding amount on secondary y-axis
        fig.add_trace(go.Scatter(
            x=monthly_data['date'],
            y=monthly_data['total_amount'],
            mode='lines+markers',
            name='Funding Amount (₹M)',
            yaxis='y2',
            line=dict(color='red')
        ))
        
        # Update layout for dual y-axis
        fig.update_layout(
            title="Monthly Deals vs Funding Amount",
            xaxis_title="Date",
            yaxis=dict(title="Deal Count", side="left"),
            yaxis2=dict(title="Funding Amount (₹M)", side="right", overlaying="y"),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient data for month-over-month analysis.")

def display_sector_analysis(df, viz):
    """Display sector analysis"""
    st.subheader("🏭 Sector Analysis")
    
    # Sector analysis by count and sum
    sector_analysis = df.groupby('vertical').agg({
        'startup': 'count',
        'amount': 'sum'
    }).reset_index()
    sector_analysis.columns = ['sector', 'deal_count', 'total_funding']
    sector_analysis = sector_analysis.sort_values('total_funding', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top Sectors by Deal Count**")
        top_sectors_count = sector_analysis.nlargest(10, 'deal_count')
        fig = viz.create_pie_chart(
            top_sectors_count,
            values='deal_count',
            names='sector',
            title="Top 10 Sectors by Deal Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**Top Sectors by Funding Amount**")
        top_sectors_funding = sector_analysis.nlargest(10, 'total_funding')
        fig = viz.create_pie_chart(
            top_sectors_funding,
            values='total_funding',
            names='sector',
            title="Top 10 Sectors by Total Funding"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed sector table
    st.write("**Detailed Sector Analysis**")
    sector_display = sector_analysis.copy()
    sector_display['total_funding'] = sector_display['total_funding'].apply(lambda x: f"₹{x:,.0f}M")
    sector_display['avg_funding'] = (sector_analysis['total_funding'] / sector_analysis['deal_count']).apply(lambda x: f"₹{x:.2f}M")
    
    st.dataframe(
        sector_display[['sector', 'deal_count', 'total_funding', 'avg_funding']].head(20),
        column_config={
            "sector": "Sector",
            "deal_count": "Deal Count",
            "total_funding": "Total Funding",
            "avg_funding": "Avg Funding"
        },
        use_container_width=True
    )

def display_funding_type_analysis(df, viz):
    """Display funding type analysis"""
    st.subheader("💼 Funding Stage Analysis")
    
    stage_analysis = df.groupby('round').agg({
        'startup': 'count',
        'amount': ['sum', 'mean']
    }).reset_index()
    
    stage_analysis.columns = ['stage', 'deal_count', 'total_funding', 'avg_funding']
    stage_analysis = stage_analysis.sort_values('total_funding', ascending=False)
    
    # Pie chart for funding stages
    fig = viz.create_pie_chart(
        stage_analysis.head(10),
        values='deal_count',
        names='stage',
        title="Distribution by Funding Stage",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Funnel chart for funding stages
    stage_order = ['Seed', 'Angel', 'Pre-Series A', 'Series A', 'Series B', 'Series C', 'Series D', 'Series E']
    funnel_data = []
    
    for stage in stage_order:
        stage_data = stage_analysis[stage_analysis['stage'] == stage]
        if not stage_data.empty:
            funnel_data.append({
                'stage': stage,
                'count': stage_data['deal_count'].iloc[0]
            })
    
    if funnel_data:
        funnel_df = pd.DataFrame(funnel_data)
        fig = viz.create_funnel_chart(
            funnel_df,
            x='count',
            y='stage',
            title="Funding Stage Funnel",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

def display_city_analysis(df, viz):
    """Display city-wise funding analysis"""
    st.subheader("🏙️ City-wise Funding")
    
    city_analysis = df.groupby('city').agg({
        'startup': 'count',
        'amount': 'sum'
    }).reset_index()
    city_analysis.columns = ['city', 'deal_count', 'total_funding']
    city_analysis = city_analysis.sort_values('total_funding', ascending=False)
    
    # Top cities by funding
    top_cities = city_analysis.head(10)
    fig = viz.create_bar_chart(
        top_cities,
        x='city',
        y='total_funding',
        title="Top 10 Cities by Total Funding (₹M)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # City distribution pie chart
    fig = viz.create_pie_chart(
        top_cities,
        values='deal_count',
        names='city',
        title="Deal Distribution by City",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def display_top_performers(df):
    """Display top performers analysis"""
    st.subheader("🏆 Top Performers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top Startups (Overall)**")
        top_startups = df.groupby('startup').agg({
            'amount': 'sum',
            'vertical': 'first',
            'city': 'first'
        }).reset_index()
        top_startups = top_startups.sort_values('amount', ascending=False).head(15)
        
        top_startups_display = top_startups.copy()
        top_startups_display['amount'] = top_startups_display['amount'].apply(lambda x: f"₹{x:,.0f}M")
        
        st.dataframe(
            top_startups_display[['startup', 'amount', 'vertical', 'city']],
            column_config={
                "startup": "Startup",
                "amount": "Total Funding",
                "vertical": "Industry",
                "city": "City"
            },
            use_container_width=True
        )
    
    with col2:
        st.write("**Top Startups (Year-wise)**")
        year_filter = st.selectbox(
            "Select Year",
            options=sorted(df['year'].unique(), reverse=True),
            key="year_filter"
        )
        
        yearly_df = df[df['year'] == year_filter]
        top_yearly = yearly_df.groupby('startup').agg({
            'amount': 'sum',
            'vertical': 'first',
            'city': 'first'
        }).reset_index()
        top_yearly = top_yearly.sort_values('amount', ascending=False).head(15)
        
        top_yearly_display = top_yearly.copy()
        top_yearly_display['amount'] = top_yearly_display['amount'].apply(lambda x: f"₹{x:,.0f}M")
        
        st.dataframe(
            top_yearly_display[['startup', 'amount', 'vertical', 'city']],
            column_config={
                "startup": "Startup",
                "amount": f"{year_filter} Funding",
                "vertical": "Industry",
                "city": "City"
            },
            use_container_width=True
        )
    
    # Top investors
    st.write("**Top Investors**")
    
    # Create investor analysis
    investor_data = []
    for _, row in df.iterrows():
        investors = str(row['investors']).split(',')
        for investor in investors:
            investor = investor.strip()
            if investor and investor.lower() != 'unknown':
                investor_data.append({
                    'investor': investor,
                    'amount': row['amount'],
                    'startup': row['startup']
                })
    
    if investor_data:
        investor_df = pd.DataFrame(investor_data)
        top_investors = investor_df.groupby('investor').agg({
            'amount': 'sum',
            'startup': 'count'
        }).reset_index()
        top_investors.columns = ['investor', 'total_amount', 'investment_count']
        top_investors = top_investors.sort_values('total_amount', ascending=False).head(20)
        
        top_investors_display = top_investors.copy()
        top_investors_display['total_amount'] = top_investors_display['total_amount'].apply(lambda x: f"₹{x:,.0f}M")
        
        st.dataframe(
            top_investors_display,
            column_config={
                "investor": "Investor",
                "total_amount": "Total Invested",
                "investment_count": "# Investments"
            },
            use_container_width=True
        )

def display_funding_heatmap(df):
    """Display funding heatmap"""
    st.subheader("🔥 Funding Heatmap")
    
    # Create year-month heatmap data
    df['year_month'] = df['date'].dt.to_period('M')
    heatmap_data = df.groupby(['year', 'month']).agg({
        'amount': 'sum',
        'startup': 'count'
    }).reset_index()
    
    # Choose metric for heatmap
    metric = st.selectbox(
        "Select Metric for Heatmap",
        options=["Total Funding Amount", "Number of Deals"],
        key="heatmap_metric"
    )
    
    value_col = 'amount' if metric == "Total Funding Amount" else 'startup'
    
    # Pivot data for heatmap
    heatmap_pivot = heatmap_data.pivot_table(
        index='year',
        columns='month',
        values=value_col,
        fill_value=0
    )
    
    if not heatmap_pivot.empty:
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values,
            x=[f"Month {i}" for i in heatmap_pivot.columns],
            y=heatmap_pivot.index,
            colorscale='RdYlBu_r',
            hoverongaps=False,
            colorbar=dict(title=metric)
        ))
        
        fig.update_layout(
            title=f"Funding Heatmap - {metric}",
            xaxis_title="Month",
            yaxis_title="Year",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient data to generate heatmap.")
    
    # Additional insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Best month
        monthly_totals = df.groupby(df['date'].dt.month)['amount'].sum()
        best_month = monthly_totals.idxmax()
        month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                      7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        st.metric(
            "Best Month",
            month_names.get(best_month, best_month),
            f"₹{monthly_totals.max():,.0f}M"
        )
    
    with col2:
        # Best year
        yearly_totals = df.groupby('year')['amount'].sum()
        best_year = yearly_totals.idxmax()
        st.metric(
            "Best Year",
            str(best_year),
            f"₹{yearly_totals.max():,.0f}M"
        )
    
    with col3:
        # Peak quarter
        quarterly_totals = df.groupby(df['date'].dt.quarter)['amount'].sum()
        best_quarter = quarterly_totals.idxmax()
        st.metric(
            "Best Quarter",
            f"Q{best_quarter}",
            f"₹{quarterly_totals.max():,.0f}M"
        )

# Main Application
def main():
    """Main application function"""
    
    # Load data
    df = load_data()
    if df is None:
        st.stop()
    
    # Initialize processors
    data_processor = DataProcessor(df)
    processed_df = data_processor.process_data()
    viz = Visualizations()
    
    # Sidebar navigation
    st.sidebar.title("🚀 Indian Startup Funding Dashboard")
    st.sidebar.markdown("---")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Choose Analysis Type",
        ["🏢 Company Analysis", "💼 Investor Analysis", "📊 General Analysis"]
    )
    
    # Display current dataset info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Dataset Info")
    st.sidebar.write(f"**Total Records:** {len(processed_df):,}")
    st.sidebar.write(f"**Date Range:** {processed_df['date'].min().strftime('%Y-%m-%d')} to {processed_df['date'].max().strftime('%Y-%m-%d')}")
    st.sidebar.write(f"**Unique Companies:** {processed_df['startup'].nunique():,}")
    st.sidebar.write(f"**Unique Investors:** {processed_df['investors'].nunique():,}")
    
    # Route to appropriate page
    if page == "🏢 Company Analysis":
        st.title("🏢 Company Analysis")
        st.markdown("---")
        
        # Company search and selection
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Get unique companies
            companies = sorted(processed_df['startup'].unique())
            selected_company = st.selectbox(
                "Search and Select Company",
                options=[""] + companies,
                help="Type to search for a company"
            )
        
        with col2:
            # Quick stats
            st.metric("Total Companies", f"{processed_df['startup'].nunique():,}")
        
        if selected_company:
            display_company_details(processed_df, selected_company, data_processor, viz)
        else:
            display_company_overview(processed_df, viz)
            
    elif page == "💼 Investor Analysis":
        st.title("💼 Investor Analysis")
        st.markdown("---")
        
        # Get unique investors
        all_investors = set()
        for investors_str in processed_df['investors'].dropna():
            investors = str(investors_str).split(',')
            for investor in investors:
                investor = investor.strip()
                if investor and investor.lower() != 'unknown':
                    all_investors.add(investor)
        
        investors_list = sorted(list(all_investors))
        
        # Investor search and selection
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_investor = st.selectbox(
                "Search and Select Investor",
                options=[""] + investors_list,
                help="Type to search for an investor"
            )
        
        with col2:
            st.metric("Total Investors", f"{len(investors_list):,}")
        
        if selected_investor:
            display_investor_details(processed_df, selected_investor, data_processor, viz)
        else:
            display_investor_overview(processed_df, viz)
            
    elif page == "📊 General Analysis":
        st.title("📊 General Market Analysis")
        st.markdown("---")
        
        # Date range filter
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            min_date = processed_df['date'].min().date()
            start_date = st.date_input("Start Date", min_date)
        
        with col2:
            max_date = processed_df['date'].max().date()
            end_date = st.date_input("End Date", max_date)
        
        # Filter data by date range
        filtered_df = processed_df[
            (processed_df['date'].dt.date >= start_date) & 
            (processed_df['date'].dt.date <= end_date)
        ]
        
        with col3:
            st.info(f"Showing data from {start_date} to {end_date} ({len(filtered_df):,} records)")
        
        # Summary cards
        display_summary_cards(filtered_df)
        
        st.markdown("---")
        
        # MoM analysis
        display_mom_analysis(filtered_df, viz)
        
        st.markdown("---")
        
        # Sector analysis
        display_sector_analysis(filtered_df, viz)
        
        st.markdown("---")
        
        # Funding type and city analysis
        col1, col2 = st.columns(2)
        
        with col1:
            display_funding_type_analysis(filtered_df, viz)
        
        with col2:
            display_city_analysis(filtered_df, viz)
        
        st.markdown("---")
        
        # Top performers
        display_top_performers(filtered_df)
        
        st.markdown("---")
        
        # Funding heatmap
        display_funding_heatmap(filtered_df)

if __name__ == "__main__":
    main()