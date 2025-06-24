import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

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
    def create_heatmap(data, title, height=500):
        """Create a heatmap for funding analysis"""
        fig = go.Figure(data=go.Heatmap(
            z=data.values,
            x=data.columns,
            y=data.index,
            colorscale='RdYlBu_r',
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=title,
            height=height,
            xaxis_title="Month",
            yaxis_title="Year"
        )
        return fig
    
    @staticmethod
    def create_scatter_plot(data, x, y, size=None, color=None, title="", height=400):
        """Create an interactive scatter plot"""
        fig = px.scatter(
            data, 
            x=x, 
            y=y, 
            size=size,
            color=color,
            title=title,
            height=height,
            hover_data=data.columns
        )
        return fig
    
    @staticmethod
    def create_box_plot(data, x, y, title, height=400):
        """Create a box plot"""
        fig = px.box(
            data, 
            x=x, 
            y=y, 
            title=title,
            height=height
        )
        return fig
    
    @staticmethod
    def create_treemap(data, path, values, title, height=500):
        """Create a treemap visualization"""
        fig = px.treemap(
            data,
            path=path,
            values=values,
            title=title,
            height=height
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
    
    @staticmethod
    def create_gauge_chart(value, max_value, title, height=300):
        """Create a gauge chart for metrics"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, max_value * 0.5], 'color': "lightgray"},
                    {'range': [max_value * 0.5, max_value * 0.8], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_value * 0.9
                }
            }
        ))
        
        fig.update_layout(height=height)
        return fig
    
    @staticmethod
    def create_stacked_bar_chart(data, x, y, color, title, height=400):
        """Create a stacked bar chart"""
        fig = px.bar(
            data, 
            x=x, 
            y=y, 
            color=color,
            title=title,
            height=height
        )
        return fig
    
    @staticmethod
    def create_area_chart(data, x, y, color=None, title="", height=400):
        """Create an area chart"""
        fig = px.area(
            data, 
            x=x, 
            y=y, 
            color=color,
            title=title,
            height=height
        )
        return fig
