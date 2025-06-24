import streamlit as st
import pandas as pd
import plotly.express as px
from utils.visualizations import Visualizations
from utils.data_processor import DataProcessor

class CompanyAnalysis:
    def __init__(self, df):
        self.df = df
        self.viz = Visualizations()
        self.data_processor = DataProcessor(df)
    
    def render(self):
        """Render the company analysis page"""
        st.title("🏢 Startup Analysis")
        st.markdown("---")
        
        # Company search and selection
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Get unique companies
            companies = sorted(self.df['startup'].unique())
            selected_company = st.selectbox(
                "Search and Select Startup",
                options=[""] + companies,
                help="Type to search for a startup"
            )
        
        with col2:
            # Quick stats
            st.metric("Total Startups", f"{self.df['startup'].nunique():,}")
        
        if selected_company:
            self.display_company_details(selected_company)
        else:
            self.display_company_overview()
    
    def display_company_details(self, company_name):
        """Display detailed analysis for selected company"""
        company_info = self.data_processor.get_company_info(self.df, company_name)
        
        if not company_info:
            st.error("Startup not found in the dataset.")
            return
        
        # Company header
        st.header(f"📊 {company_info['name']}")
        
        # Basic information cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Industry", 
                company_info['industry'],
                help="Primary industry vertical"
            )
        
        with col2:
            st.metric(
                "Sub-Industry", 
                company_info['subindustry'],
                help="Specific sub-vertical"
            )
        
        with col3:
            st.metric(
                "Location", 
                company_info['location'],
                help="Primary business location"
            )
        
        with col4:
            st.metric(
                "Funding Rounds", 
                f"{company_info['funding_rounds']}",
                help="Total number of funding rounds"
            )
        
        # Funding metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Funding",
                f"₹{company_info['total_funding']:.2f}M",
                help="Total funding raised across all rounds"
            )
        
        with col2:
            if company_info['funding_rounds'] > 0:
                avg_funding = company_info['total_funding'] / company_info['funding_rounds']
                st.metric(
                    "Avg. Round Size",
                    f"₹{avg_funding:.2f}M",
                    help="Average funding per round"
                )
        
        with col3:
            if pd.notna(company_info['last_funding_date']):
                st.metric(
                    "Last Funding",
                    company_info['last_funding_date'].strftime('%Y-%m-%d'),
                    help="Date of most recent funding"
                )
        
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
                    fig = self.viz.create_line_chart(
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
        st.subheader("🔍 Similar Startups")
        similar_companies = self.data_processor.find_similar_companies(self.df, company_name)
        
        if similar_companies:
            similar_df = pd.DataFrame(similar_companies)
            similar_df['amount'] = similar_df['amount'].apply(lambda x: f"₹{x:.2f}M")
            similar_df['date'] = pd.to_datetime(similar_df['date']).dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                similar_df[['startup', 'vertical', 'city', 'amount', 'date']],
                column_config={
                    "startup": "Startup",
                    "vertical": "Industry",
                    "city": "Location",
                    "amount": "Total Funding",
                    "date": "Last Funding"
                },
                use_container_width=True
            )
        else:
            st.info("No similar startups found based on industry, sub-industry, or location.")
    
    def display_company_overview(self):
        """Display overview of all companies"""
        st.subheader("📈 Startup Overview")
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_companies = self.df['startup'].nunique()
            st.metric("Total Startups", f"{total_companies:,}")
        
        with col2:
            total_funding = self.df['amount'].sum()
            st.metric("Total Funding", f"₹{total_funding:,.0f}M")
        
        with col3:
            avg_funding = self.df['amount'].mean()
            st.metric("Avg. Funding", f"₹{avg_funding:.2f}M")
        
        with col4:
            max_funding = self.df['amount'].max()
            st.metric("Largest Round", f"₹{max_funding:,.0f}M")
        
        st.markdown("---")
        
        # Industry distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏭 Industry Distribution")
            industry_counts = self.df['vertical'].value_counts().head(10)
            fig = self.viz.create_pie_chart(
                pd.DataFrame({'industry': industry_counts.index, 'count': industry_counts.values}),
                values='count',
                names='industry',
                title="Top 10 Industries by Startup Count"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("💰 Industry Funding")
            industry_funding = self.df.groupby('vertical')['amount'].sum().sort_values(ascending=False).head(10)
            fig = self.viz.create_bar_chart(
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
            city_counts = self.df['city'].value_counts().head(10)
            fig = self.viz.create_bar_chart(
                pd.DataFrame({'city': city_counts.index, 'count': city_counts.values}),
                x='city',
                y='count',
                title="Top 10 Cities by Startup Count"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("💼 Funding Stages")
            stage_counts = self.df['round'].value_counts().head(10)
            fig = self.viz.create_pie_chart(
                pd.DataFrame({'stage': stage_counts.index, 'count': stage_counts.values}),
                values='count',
                names='stage',
                title="Funding Stages Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top funded companies
        st.subheader("🏆 Top Funded Startups")
        top_companies = self.df.groupby('startup').agg({
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
                "startup": "Startup",
                "vertical": "Industry",
                "city": "Location",
                "amount": "Total Funding",
                "date": "Last Funding"
            },
            use_container_width=True
        )
