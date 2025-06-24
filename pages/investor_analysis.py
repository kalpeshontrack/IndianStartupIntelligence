import streamlit as st
import pandas as pd
import plotly.express as px
from utils.visualizations import Visualizations
from utils.data_processor import DataProcessor

class InvestorAnalysis:
    def __init__(self, df):
        self.df = df
        self.viz = Visualizations()
        self.data_processor = DataProcessor(df)
    
    def render(self):
        """Render the investor analysis page"""
        st.markdown('<h2 class="section-header">💼 Investor Analysis</h2>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Deep dive into investor behavior, portfolio analysis, and investment patterns across the Indian startup ecosystem</div>', unsafe_allow_html=True)
        
        # Get unique investors
        all_investors = set()
        for investors_str in self.df['investors'].dropna():
            investors = str(investors_str).split(',')
            for investor in investors:
                investor = investor.strip()
                if investor and investor.lower() != 'unknown':
                    all_investors.add(investor)
        
        investors_list = sorted(list(all_investors))
        
        # Enhanced investor search section
        st.markdown("### 🔍 Investor Search")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_investor = st.selectbox(
                "🔍 Search and Select Investor",
                options=[""] + investors_list,
                help="Type to search for an investor and explore their portfolio"
            )
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>💼 Total Investors</h4>
                <h2>{len(investors_list):,}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        if selected_investor:
            self.display_investor_details(selected_investor)
        else:
            self.display_investor_overview()
    
    def display_investor_details(self, investor_name):
        """Display detailed analysis for selected investor"""
        investor_info = self.data_processor.get_investor_info(self.df, investor_name)
        
        if not investor_info:
            st.error("Investor not found in the dataset.")
            return
        
        # Investor header
        st.header(f"💼 {investor_info['name']}")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Investments",
                f"{investor_info['total_investments']:,}",
                help="Number of companies invested in"
            )
        
        with col2:
            st.metric(
                "Total Amount",
                f"₹{investor_info['total_amount_invested']:,.0f}M",
                help="Total amount invested across all deals"
            )
        
        with col3:
            st.metric(
                "Avg Investment",
                f"₹{investor_info['avg_investment']:.2f}M",
                help="Average investment per deal"
            )
        
        with col4:
            if not investor_info['recent_investments'].empty:
                last_investment = investor_info['recent_investments'].iloc[0]['date']
                st.metric(
                    "Last Investment",
                    last_investment.strftime('%Y-%m-%d'),
                    help="Date of most recent investment"
                )
        
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
                fig = self.viz.create_pie_chart(
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
                fig = self.viz.create_pie_chart(
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
                fig = self.viz.create_pie_chart(
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
                fig = self.viz.create_line_chart(
                    yearly_df,
                    x='year',
                    y='startup',
                    title="Number of Investments by Year"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = self.viz.create_line_chart(
                    yearly_df,
                    x='year',
                    y='amount',
                    title="Investment Amount by Year (₹M)"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Similar investors
        st.subheader("🔍 Similar Investors")
        similar_investors = self.data_processor.find_similar_investors(self.df, investor_name)
        
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
    
    def display_investor_overview(self):
        """Display overview of all investors"""
        st.subheader("📊 Investor Overview")
        
        # Create investor analysis dataframe
        investor_data = []
        for _, row in self.df.iterrows():
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
            fig = self.viz.create_bar_chart(
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
            fig = self.viz.create_bar_chart(
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
            fig = self.viz.create_pie_chart(
                pd.DataFrame({'sector': sector_investments.index, 'count': sector_investments.values}),
                values='count',
                names='sector',
                title="Top 10 Sectors by Investment Count"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Preferred Stages")
            stage_investments = investor_df['round'].value_counts().head(10)
            fig = self.viz.create_pie_chart(
                pd.DataFrame({'stage': stage_investments.index, 'count': stage_investments.values}),
                values='count',
                names='stage',
                title="Investment Distribution by Stage"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Geographic preferences
        st.subheader("🗺️ Geographic Investment Preferences")
        city_investments = investor_df['city'].value_counts().head(15)
        fig = self.viz.create_bar_chart(
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
            fig = self.viz.create_line_chart(
                yearly_trends,
                x='year',
                y='investment_count',
                title="Number of Investments Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = self.viz.create_line_chart(
                yearly_trends,
                x='year',
                y='total_amount',
                title="Total Investment Amount Over Time (₹M)"
            )
            st.plotly_chart(fig, use_container_width=True)
