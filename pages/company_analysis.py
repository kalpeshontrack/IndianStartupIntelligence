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
        st.markdown('<h2 class="section-header">🏢 Startup Analysis</h2>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Explore detailed insights about Indian startups, their funding journey, and industry comparisons</div>', unsafe_allow_html=True)
        
        # Enhanced search section
        st.markdown("### 🔍 Startup Search")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Get unique companies
            companies = sorted(self.df['startup'].unique())
            selected_company = st.selectbox(
                "🔍 Search and Select Startup",
                options=[""] + companies,
                help="Type to search for a startup and explore its funding journey"
            )
        
        with col2:
            # Enhanced quick stats
            st.markdown(f"""
            <div class="metric-card">
                <h4>🏢 Total Startups</h4>
                <h2>{self.df['startup'].nunique():,}</h2>
            </div>
            """, unsafe_allow_html=True)
        
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
        
        # Enhanced company header
        st.markdown(f'<h2 class="section-header">📊 {company_info["name"]}</h2>', unsafe_allow_html=True)
        
        # Basic information cards with enhanced styling
        st.markdown("#### 🏭 Company Profile")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🏭 Industry</h4>
                <h3>{company_info['industry']}</h3>
                <small>Primary industry vertical</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🎯 Sub-Industry</h4>
                <h3>{company_info['subindustry']}</h3>
                <small>Specific sub-vertical</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📍 Location</h4>
                <h3>{company_info['location']}</h3>
                <small>Primary business location</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🔄 Funding Rounds</h4>
                <h3>{company_info['funding_rounds']}</h3>
                <small>Total number of rounds</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced funding metrics
        st.markdown("#### 💰 Funding Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>💰 Total Funding</h4>
                <h2>₹{company_info['total_funding']:.2f}M</h2>
                <small>Total funding raised across all rounds</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if company_info['funding_rounds'] > 0:
                avg_funding = company_info['total_funding'] / company_info['funding_rounds']
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📊 Avg. Round Size</h4>
                    <h2>₹{avg_funding:.2f}M</h2>
                    <small>Average funding per round</small>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if pd.notna(company_info['last_funding_date']):
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📅 Last Funding</h4>
                    <h2>{company_info['last_funding_date'].strftime('%Y-%m-%d')}</h2>
                    <small>Date of most recent funding</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Enhanced funding rounds details
        st.markdown('<h3 class="section-header">💰 Funding History</h3>', unsafe_allow_html=True)
        
        if not company_info['funding_history'].empty:
            funding_df = company_info['funding_history'].copy()
            funding_df['date'] = funding_df['date'].dt.strftime('%Y-%m-%d')
            funding_df['amount'] = funding_df['amount'].apply(lambda x: f"₹{x:.2f}M" if x > 0 else "Undisclosed")
            
            # Display enhanced funding table
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.dataframe(
                funding_df[['date', 'round', 'amount', 'investors']],
                column_config={
                    "date": "📅 Date",
                    "round": "🔄 Round Type",
                    "amount": "💰 Amount",
                    "investors": "💼 Investors"
                },
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Funding timeline chart
            if len(funding_df) > 1:
                timeline_data = company_info['funding_history'].copy()
                timeline_data = timeline_data[timeline_data['amount'] > 0]  # Only include disclosed amounts
                
                if not timeline_data.empty:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    fig = self.viz.create_line_chart(
                        timeline_data,
                        x='date',
                        y='amount',
                        title=f"📈 {company_name} - Funding Timeline",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No detailed funding history available for this company.")
        
        st.markdown("---")
        
        # Enhanced similar companies section
        st.markdown('<h3 class="section-header">🔍 Similar Startups</h3>', unsafe_allow_html=True)
        similar_companies = self.data_processor.find_similar_companies(self.df, company_name)
        
        if similar_companies:
            similar_df = pd.DataFrame(similar_companies)
            similar_df['amount'] = similar_df['amount'].apply(lambda x: f"₹{x:.2f}M")
            similar_df['date'] = pd.to_datetime(similar_df['date']).dt.strftime('%Y-%m-%d')
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.dataframe(
                similar_df[['startup', 'vertical', 'city', 'amount', 'date']],
                column_config={
                    "startup": "🏢 Startup",
                    "vertical": "🏭 Industry",
                    "city": "📍 Location",
                    "amount": "💰 Total Funding",
                    "date": "📅 Last Funding"
                },
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box">No similar startups found based on industry, sub-industry, or location.</div>', unsafe_allow_html=True)
    
    def display_company_overview(self):
        """Display overview of all companies"""
        st.markdown('<h3 class="section-header">📈 Startup Overview</h3>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Comprehensive overview of all startups in the Indian ecosystem</div>', unsafe_allow_html=True)
        
        # Enhanced top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_companies = self.df['startup'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <h4>🏢 Total Startups</h4>
                <h2>{total_companies:,}</h2>
                <small>Unique companies in ecosystem</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_funding = self.df['amount'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h4>💰 Total Funding</h4>
                <h2>₹{total_funding:,.0f}M</h2>
                <small>Total capital raised</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_funding = self.df['amount'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h4>📊 Avg. Funding</h4>
                <h2>₹{avg_funding:.2f}M</h2>
                <small>Average per round</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            max_funding = self.df['amount'].max()
            st.markdown(f"""
            <div class="metric-card">
                <h4>🚀 Largest Round</h4>
                <h2>₹{max_funding:,.0f}M</h2>
                <small>Biggest single funding</small>
            </div>
            """, unsafe_allow_html=True)
        
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
