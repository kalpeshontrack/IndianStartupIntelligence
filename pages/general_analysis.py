import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.visualizations import Visualizations

class GeneralAnalysis:
    def __init__(self, df):
        self.df = df
        self.viz = Visualizations()
    
    def render(self):
        """Render the general analysis page"""
        st.title("📊 General Market Analysis")
        st.markdown("---")
        
        # Date range filter
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            min_date = self.df['date'].min().date()
            start_date = st.date_input("Start Date", min_date)
        
        with col2:
            max_date = self.df['date'].max().date()
            end_date = st.date_input("End Date", max_date)
        
        # Filter data by date range
        filtered_df = self.df[
            (self.df['date'].dt.date >= start_date) & 
            (self.df['date'].dt.date <= end_date)
        ]
        
        with col3:
            st.info(f"Showing data from {start_date} to {end_date} ({len(filtered_df):,} records)")
        
        # Summary cards
        self.display_summary_cards(filtered_df)
        
        st.markdown("---")
        
        # MoM analysis
        self.display_mom_analysis(filtered_df)
        
        st.markdown("---")
        
        # Sector analysis
        self.display_sector_analysis(filtered_df)
        
        st.markdown("---")
        
        # Funding type and city analysis
        col1, col2 = st.columns(2)
        
        with col1:
            self.display_funding_type_analysis(filtered_df)
        
        with col2:
            self.display_city_analysis(filtered_df)
        
        st.markdown("---")
        
        # Top performers
        self.display_top_performers(filtered_df)
        
        st.markdown("---")
        
        # Funding heatmap
        self.display_funding_heatmap(filtered_df)
    
    def display_summary_cards(self, df):
        """Display summary metrics cards"""
        st.subheader("📈 Key Metrics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_startups = df['startup'].nunique()
            st.metric(
                "Total Startups",
                f"{total_startups:,}",
                help="Unique startups that received funding"
            )
        
        with col2:
            total_funding = df['amount'].sum()
            st.metric(
                "Total Funding",
                f"₹{total_funding:,.0f}M",
                help="Total funding amount raised"
            )
        
        with col3:
            avg_funding = df['amount'].mean()
            st.metric(
                "Avg Funding",
                f"₹{avg_funding:.2f}M",
                help="Average funding per round"
            )
        
        with col4:
            max_funding = df['amount'].max()
            max_startup = df.loc[df['amount'].idxmax(), 'startup']
            st.metric(
                "Largest Round",
                f"₹{max_funding:,.0f}M",
                help=f"Largest funding round by {max_startup}"
            )
        
        with col5:
            total_investors = len(set([
                investor.strip() 
                for investors_str in df['investors'].dropna() 
                for investor in str(investors_str).split(',')
                if investor.strip() and investor.strip().lower() != 'unknown'
            ]))
            st.metric(
                "Active Investors",
                f"{total_investors:,}",
                help="Unique investors in the period"
            )
    
    def display_mom_analysis(self, df):
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
                fig = self.viz.create_line_chart(
                    monthly_data,
                    x='date',
                    y='deal_count',
                    title="Monthly Deal Count",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = self.viz.create_line_chart(
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
    
    def display_sector_analysis(self, df):
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
            fig = self.viz.create_pie_chart(
                top_sectors_count,
                values='deal_count',
                names='sector',
                title="Top 10 Sectors by Deal Count"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Top Sectors by Funding Amount**")
            top_sectors_funding = sector_analysis.nlargest(10, 'total_funding')
            fig = self.viz.create_pie_chart(
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
    
    def display_funding_type_analysis(self, df):
        """Display funding type analysis"""
        st.subheader("💼 Funding Stage Analysis")
        
        stage_analysis = df.groupby('round').agg({
            'startup': 'count',
            'amount': ['sum', 'mean']
        }).reset_index()
        
        stage_analysis.columns = ['stage', 'deal_count', 'total_funding', 'avg_funding']
        stage_analysis = stage_analysis.sort_values('total_funding', ascending=False)
        
        # Pie chart for funding stages
        fig = self.viz.create_pie_chart(
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
            fig = self.viz.create_funnel_chart(
                funnel_df,
                x='count',
                y='stage',
                title="Funding Stage Funnel",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def display_city_analysis(self, df):
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
        fig = self.viz.create_bar_chart(
            top_cities,
            x='city',
            y='total_funding',
            title="Top 10 Cities by Total Funding (₹M)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # City distribution pie chart
        fig = self.viz.create_pie_chart(
            top_cities,
            values='deal_count',
            names='city',
            title="Deal Distribution by City",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def display_top_performers(self, df):
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
    
    def display_funding_heatmap(self, df):
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
