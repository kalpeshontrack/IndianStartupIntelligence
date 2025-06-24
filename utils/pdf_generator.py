import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

class PDFReportGenerator:
    def __init__(self, df, data_processor):
        self.df = df
        self.data_processor = data_processor
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#FF6B6B'),
            alignment=1  # Center alignment
        )
        
        # Heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            textColor=HexColor('#4ECDC4'),
            leftIndent=0
        )
        
        # Subheading style
        self.subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            textColor=HexColor('#666666')
        )
        
        # Body style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            textColor=HexColor('#333333')
        )
    
    def create_chart_image(self, fig, width=6*inch, height=4*inch):
        """Convert Plotly figure to image for PDF"""
        img_bytes = fig.to_image(format="png", width=600, height=400)
        img_buffer = io.BytesIO(img_bytes)
        return Image(img_buffer, width=width, height=height)
    
    def generate_executive_summary(self):
        """Generate executive summary section"""
        elements = []
        
        # Calculate key metrics
        total_startups = self.df['startup'].nunique()
        total_funding = self.df['amount'].sum()
        avg_funding = self.df['amount'].mean()
        date_range = f"{self.df['date'].min().strftime('%Y-%m-%d')} to {self.df['date'].max().strftime('%Y-%m-%d')}"
        
        elements.append(Paragraph("Executive Summary", self.heading_style))
        
        summary_text = f"""
        This report provides a comprehensive analysis of the Indian startup funding ecosystem based on data spanning {date_range}.
        
        <b>Key Highlights:</b><br/>
        • Total Startups Analyzed: {total_startups:,}<br/>
        • Total Funding Raised: ₹{total_funding:,.0f} Million<br/>
        • Average Funding per Round: ₹{avg_funding:.2f} Million<br/>
        • Analysis Period: {date_range}<br/>
        
        The Indian startup ecosystem continues to show robust growth with significant investment activity across various sectors.
        This report examines funding patterns, investor behavior, and market trends to provide actionable insights.
        """
        
        elements.append(Paragraph(summary_text, self.body_style))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def generate_market_overview(self):
        """Generate market overview with charts"""
        elements = []
        
        elements.append(Paragraph("Market Overview", self.heading_style))
        
        # Top 10 sectors by funding
        sector_funding = self.df.groupby('vertical')['amount'].sum().sort_values(ascending=False).head(10)
        
        # Create pie chart for sectors
        fig = px.pie(
            values=sector_funding.values, 
            names=sector_funding.index,
            title="Top 10 Sectors by Funding Volume"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=False, width=600, height=400)
        
        elements.append(self.create_chart_image(fig))
        elements.append(Spacer(1, 15))
        
        # Monthly funding trends
        monthly_data = self.df.groupby(self.df['date'].dt.to_period('M'))['amount'].sum().reset_index()
        monthly_data['date'] = monthly_data['date'].astype(str)
        
        fig2 = px.line(
            monthly_data, 
            x='date', 
            y='amount',
            title="Monthly Funding Trends"
        )
        fig2.update_layout(xaxis_title="Month", yaxis_title="Funding (₹ Million)")
        
        elements.append(self.create_chart_image(fig2))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def generate_top_performers(self):
        """Generate top performers section"""
        elements = []
        
        elements.append(Paragraph("Top Performers", self.heading_style))
        
        # Top funded startups
        top_startups = self.df.groupby('startup').agg({
            'amount': 'sum',
            'vertical': 'first',
            'city': 'first'
        }).sort_values('amount', ascending=False).head(10)
        
        # Create table data
        table_data = [['Rank', 'Startup', 'Industry', 'City', 'Total Funding (₹M)']]
        for i, (startup, data) in enumerate(top_startups.iterrows(), 1):
            table_data.append([
                str(i),
                startup[:25] + "..." if len(startup) > 25 else startup,
                data['vertical'][:15] + "..." if len(data['vertical']) > 15 else data['vertical'],
                data['city'],
                f"₹{data['amount']:.1f}M"
            ])
        
        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#FF6B6B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#CCCCCC'))
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def generate_city_analysis(self):
        """Generate city-wise analysis"""
        elements = []
        
        elements.append(Paragraph("Geographic Distribution", self.heading_style))
        
        # City-wise funding
        city_funding = self.df.groupby('city')['amount'].sum().sort_values(ascending=False).head(8)
        
        fig = px.bar(
            x=city_funding.index,
            y=city_funding.values,
            title="Top Cities by Funding Volume"
        )
        fig.update_layout(xaxis_title="City", yaxis_title="Funding (₹ Million)")
        fig.update_xaxes(tickangle=45)
        
        elements.append(self.create_chart_image(fig))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def generate_investor_insights(self):
        """Generate investor analysis section"""
        elements = []
        
        elements.append(Paragraph("Investor Landscape", self.heading_style))
        
        # Get top investors
        all_investors = []
        for investors_str in self.df['investors'].dropna():
            if pd.notna(investors_str) and str(investors_str).lower() != 'unknown':
                investors = [inv.strip() for inv in str(investors_str).split(',')]
                all_investors.extend(investors)
        
        investor_counts = pd.Series(all_investors).value_counts().head(10)
        
        # Create horizontal bar chart
        fig = px.bar(
            x=investor_counts.values,
            y=investor_counts.index,
            orientation='h',
            title="Most Active Investors (by number of investments)"
        )
        fig.update_layout(xaxis_title="Number of Investments", yaxis_title="Investor")
        
        elements.append(self.create_chart_image(fig))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def generate_funding_rounds_analysis(self):
        """Generate funding rounds analysis"""
        elements = []
        
        elements.append(Paragraph("Funding Rounds Analysis", self.heading_style))
        
        # Round type distribution
        round_counts = self.df['round'].value_counts()
        
        fig = px.pie(
            values=round_counts.values,
            names=round_counts.index,
            title="Distribution of Funding Rounds"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=False)
        
        elements.append(self.create_chart_image(fig))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def generate_pdf_report(self, filename="startup_funding_report.pdf"):
        """Generate complete PDF report"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        
        # Title page
        elements.append(Paragraph("Indian Startup Funding Report", self.title_style))
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", self.body_style))
        elements.append(Spacer(1, 50))
        
        # Add all sections
        elements.extend(self.generate_executive_summary())
        elements.append(PageBreak())
        
        elements.extend(self.generate_market_overview())
        elements.append(PageBreak())
        
        elements.extend(self.generate_top_performers())
        elements.extend(self.generate_city_analysis())
        elements.append(PageBreak())
        
        elements.extend(self.generate_investor_insights())
        elements.extend(self.generate_funding_rounds_analysis())
        
        # Footer
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("This report was generated using the Indian Startup Funding Dashboard", self.body_style))
        
        # Build PDF
        doc.build(elements)
        return filename