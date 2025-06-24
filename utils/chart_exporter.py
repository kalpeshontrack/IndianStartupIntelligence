import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from datetime import datetime
import io
import base64

class ChartExporter:
    """Export individual charts and create summary reports"""
    
    def __init__(self, df):
        self.df = df
    
    def export_sector_analysis_chart(self):
        """Create and export sector analysis chart"""
        sector_funding = self.df.groupby('vertical')['amount'].sum().sort_values(ascending=False).head(10)
        
        fig = px.pie(
            values=sector_funding.values,
            names=sector_funding.index,
            title="Top 10 Sectors by Total Funding",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            font=dict(size=14),
            title_font_size=16,
            width=800,
            height=600
        )
        
        return fig
    
    def export_funding_timeline_chart(self):
        """Create and export funding timeline chart"""
        monthly_data = self.df.groupby(self.df['date'].dt.to_period('M')).agg({
            'amount': 'sum',
            'startup': 'nunique'
        }).reset_index()
        
        monthly_data['date'] = monthly_data['date'].astype(str)
        
        # Create dual axis chart
        fig = go.Figure()
        
        # Add funding amount line
        fig.add_trace(go.Scatter(
            x=monthly_data['date'],
            y=monthly_data['amount'],
            mode='lines+markers',
            name='Total Funding (₹M)',
            line=dict(color='#FF6B6B', width=3),
            yaxis='y'
        ))
        
        # Add startup count line
        fig.add_trace(go.Scatter(
            x=monthly_data['date'],
            y=monthly_data['startup'],
            mode='lines+markers',
            name='Number of Startups',
            line=dict(color='#4ECDC4', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Monthly Funding Trends and Startup Activity',
            xaxis_title='Month',
            yaxis=dict(title='Total Funding (₹ Million)', side='left'),
            yaxis2=dict(title='Number of Startups', side='right', overlaying='y'),
            hovermode='x unified',
            width=1000,
            height=500
        )
        
        return fig
    
    def export_top_startups_chart(self):
        """Create and export top startups chart"""
        top_startups = self.df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(15)
        
        fig = px.bar(
            x=top_startups.values,
            y=top_startups.index,
            orientation='h',
            title="Top 15 Startups by Total Funding",
            color=top_startups.values,
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            xaxis_title='Total Funding (₹ Million)',
            yaxis_title='Startup',
            width=1000,
            height=700,
            font=dict(size=12)
        )
        
        return fig
    
    def export_city_distribution_chart(self):
        """Create and export city distribution chart"""
        city_data = self.df.groupby('city').agg({
            'amount': 'sum',
            'startup': 'nunique'
        }).sort_values('amount', ascending=False).head(10)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=city_data.index,
            y=city_data['amount'],
            name='Total Funding (₹M)',
            marker_color='#FF6B6B',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=city_data.index,
            y=city_data['startup'],
            mode='lines+markers',
            name='Number of Startups',
            line=dict(color='#4ECDC4', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Top Cities: Funding vs Startup Count',
            xaxis_title='City',
            yaxis=dict(title='Total Funding (₹ Million)', side='left'),
            yaxis2=dict(title='Number of Startups', side='right', overlaying='y'),
            width=1000,
            height=500,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def export_funding_rounds_chart(self):
        """Create and export funding rounds analysis chart"""
        round_data = self.df.groupby('round').agg({
            'amount': ['sum', 'mean', 'count']
        }).round(2)
        
        round_data.columns = ['Total_Funding', 'Avg_Funding', 'Round_Count']
        round_data = round_data.sort_values('Total_Funding', ascending=False)
        
        fig = go.Figure()
        
        # Add total funding bars
        fig.add_trace(go.Bar(
            x=round_data.index,
            y=round_data['Total_Funding'],
            name='Total Funding (₹M)',
            marker_color='#FF6B6B',
            yaxis='y'
        ))
        
        # Add average funding line
        fig.add_trace(go.Scatter(
            x=round_data.index,
            y=round_data['Avg_Funding'],
            mode='lines+markers',
            name='Average Funding (₹M)',
            line=dict(color='#4ECDC4', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Funding Rounds Analysis: Total vs Average Funding',
            xaxis_title='Round Type',
            yaxis=dict(title='Total Funding (₹ Million)', side='left'),
            yaxis2=dict(title='Average Funding (₹ Million)', side='right', overlaying='y'),
            width=1000,
            height=500,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_downloadable_chart(self, fig, filename):
        """Convert chart to downloadable format"""
        # Export as PNG
        img_bytes = fig.to_image(format="png", width=1200, height=800, scale=2)
        
        return img_bytes
    
    def export_all_charts_section(self):
        """Create a section in Streamlit for exporting charts"""
        st.markdown("### 📊 Export Individual Charts")
        st.markdown("Download high-quality charts for presentations and reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📈 Sector Analysis Chart", help="Download sector funding distribution"):
                fig = self.export_sector_analysis_chart()
                img_bytes = self.create_downloadable_chart(fig, "sector_analysis")
                st.download_button(
                    label="💾 Download Sector Chart",
                    data=img_bytes,
                    file_name=f"sector_analysis_{datetime.now().strftime('%Y%m%d')}.png",
                    mime="image/png"
                )
            
            if st.button("🏙️ City Distribution Chart", help="Download city-wise funding analysis"):
                fig = self.export_city_distribution_chart()
                img_bytes = self.create_downloadable_chart(fig, "city_distribution")
                st.download_button(
                    label="💾 Download City Chart",
                    data=img_bytes,
                    file_name=f"city_distribution_{datetime.now().strftime('%Y%m%d')}.png",
                    mime="image/png"
                )
        
        with col2:
            if st.button("📅 Funding Timeline Chart", help="Download monthly funding trends"):
                fig = self.export_funding_timeline_chart()
                img_bytes = self.create_downloadable_chart(fig, "funding_timeline")
                st.download_button(
                    label="💾 Download Timeline Chart",
                    data=img_bytes,
                    file_name=f"funding_timeline_{datetime.now().strftime('%Y%m%d')}.png",
                    mime="image/png"
                )
            
            if st.button("🔄 Funding Rounds Chart", help="Download funding rounds analysis"):
                fig = self.export_funding_rounds_chart()
                img_bytes = self.create_downloadable_chart(fig, "funding_rounds")
                st.download_button(
                    label="💾 Download Rounds Chart",
                    data=img_bytes,
                    file_name=f"funding_rounds_{datetime.now().strftime('%Y%m%d')}.png",
                    mime="image/png"
                )
        
        if st.button("🏆 Top Startups Chart", help="Download top startups ranking"):
            fig = self.export_top_startups_chart()
            img_bytes = self.create_downloadable_chart(fig, "top_startups")
            st.download_button(
                label="💾 Download Top Startups Chart",
                data=img_bytes,
                file_name=f"top_startups_{datetime.now().strftime('%Y%m%d')}.png",
                mime="image/png"
            )