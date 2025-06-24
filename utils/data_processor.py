import pandas as pd
import numpy as np
from datetime import datetime
import re

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
