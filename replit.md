# Indian Startup Funding Dashboard

## Overview

This is a Streamlit-based web application that provides comprehensive analysis of Indian startup funding data. The application offers interactive dashboards for company analysis, investor analysis, and general market trends. It processes CSV data containing startup funding information and presents insights through various visualizations and metrics.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for rapid prototyping and built-in interactive components
- **Layout**: Wide layout with expandable sidebar navigation
- **Styling**: Custom theme with primary color #FF6B6B and clean white background
- **Caching**: Streamlit's @st.cache_data decorator for efficient data loading

### Backend Architecture
- **Language**: Python 3.11
- **Structure**: Modular design with separate classes for different analysis types
- **Data Processing**: Custom DataProcessor class handles data cleaning and standardization
- **Visualization**: Plotly for interactive charts and graphs

### Page Structure
The application follows a multi-page architecture:
- **Main App** (`app.py`): Entry point and navigation controller
- **Company Analysis** (`pages/company_analysis.py`): Individual company deep-dives
- **Investor Analysis** (`pages/investor_analysis.py`): Investor portfolio and activity analysis
- **General Analysis** (`pages/general_analysis.py`): Market trends and overview metrics

## Key Components

### Data Processing (`utils/data_processor.py`)
- **Purpose**: Centralizes data cleaning and standardization logic
- **Key Functions**:
  - Date parsing and validation
  - Company name cleaning (removes URLs, quotes)
  - Amount normalization
  - City name standardization with mapping
  - Derived column creation (year, month, quarter)

### Visualization Engine (`utils/visualizations.py`)
- **Purpose**: Provides reusable chart creation methods
- **Chart Types**: Pie charts, bar charts, line charts
- **Library**: Plotly for interactive visualizations
- **Customization**: Consistent styling and height parameters

### Analysis Modules
- **CompanyAnalysis**: Company-specific metrics and comparisons
- **InvestorAnalysis**: Investor portfolio tracking and performance
- **GeneralAnalysis**: Market-wide trends and time-series analysis

## Data Flow

1. **Data Loading**: CSV file loaded from `attached_assets/` directory
2. **Data Processing**: DataProcessor cleans and standardizes the dataset
3. **Caching**: Processed data cached using Streamlit's caching mechanism
4. **User Interaction**: Sidebar navigation allows switching between analysis types
5. **Filtering**: Date ranges and search functionality filter the displayed data
6. **Visualization**: Processed data rendered through Plotly charts
7. **Real-time Updates**: Interactive components update visualizations dynamically

## External Dependencies

### Core Libraries
- **Streamlit (>=1.46.0)**: Web application framework
- **Pandas (>=2.3.0)**: Data manipulation and analysis
- **NumPy (>=2.3.1)**: Numerical computing
- **Plotly (>=6.1.2)**: Interactive visualization library

### Supporting Libraries
- **Altair**: Additional visualization support
- **Jinja2**: Template engine for dynamic content
- **JSONSchema**: Data validation
- **Cachetools**: Enhanced caching capabilities

### Data Source
- **Dataset**: CSV file containing Indian startup funding data
- **Columns**: date, startup, vertical, subvertical, city, investors, round, amount
- **Volume**: Sample includes ~50 records from 2019-2020 timeframe

## Deployment Strategy

### Platform Configuration
- **Environment**: Replit with Python 3.11 modules
- **Nix Channel**: stable-24_05 for consistent package management
- **Port**: Application runs on port 5000
- **Deployment Target**: Autoscale for handling variable traffic

### Workflow Setup
- **Run Command**: `streamlit run app.py --server.port 5000`
- **Mode**: Parallel workflow execution
- **Health Check**: Waits for port 5000 to be available

### Configuration
- **Server Settings**: Headless mode, bound to 0.0.0.0
- **Theme**: Custom color scheme optimized for data visualization
- **Performance**: Caching enabled for data loading operations

## Changelog

```
Changelog:
- June 24, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

## Notes for Development

- The application is designed to handle missing or malformed data gracefully
- City names are standardized to handle common variations (e.g., Bengaluru → Bangalore)
- Investor data supports comma-separated lists for multiple investors per funding round
- Amount fields are converted to numeric format with fallback to 0 for invalid entries
- The modular structure allows easy addition of new analysis types or visualization methods
- Future enhancements could include database integration (potentially PostgreSQL with Drizzle ORM)