#!/usr/bin/env python3
"""
ClimaShield - Streamlit Web Interface
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the insight engine from src directory
import importlib.util
spec = importlib.util.spec_from_file_location("insight_engine", os.path.join(os.path.dirname(__file__), "src", "insight-engine.py"))
insight_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(insight_engine)

ClimateInsightEngine = insight_engine.ClimateInsightEngine
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="ClimaShield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .risk-score {
        text-align: center;
        font-size: 4rem;
        font-weight: bold;
        color: #E74C3C;
        margin: 1rem 0;
    }
    .risk-label {
        text-align: center;
        font-size: 1.5rem;
        color: #34495E;
        margin-bottom: 2rem;
    }
    .factor-box {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #3498DB;
    }
    .metric-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .status-good {
        color: #27AE60;
        font-weight: bold;
    }
    .status-warning {
        color: #F39C12;
        font-weight: bold;
    }
    .status-danger {
        color: #E74C3C;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_available_areas():
    """Load available areas from the dataset"""
    try:
        df = pd.read_csv('input-data/AQI-Rainfall.csv')
        return sorted(df['Area'].unique().tolist())
    except:
        return ['Koramangala', 'Hebbal', 'Malleswaram', 'Anekal', 'Hunasamaranahalli']

def create_gauge_chart(value, title, color_scheme='RdYlGn_r'):
    """Create a gauge chart for risk scores"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [None, 10], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 3], 'color': "lightgreen"},
                {'range': [3, 6], 'color': "yellow"},
                {'range': [6, 10], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 8
            }
        }
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig

def create_progress_bar(score, max_score=10):
    """Create a visual progress bar"""
    percentage = (score / max_score) * 100
    if percentage <= 30:
        color = "#27AE60"  # Green
    elif percentage <= 70:
        color = "#F39C12"  # Orange
    else:
        color = "#E74C3C"  # Red
    
    return f"""
    <div style="background-color: #ECF0F1; border-radius: 10px; padding: 2px;">
        <div style="background-color: {color}; width: {percentage}%; height: 20px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
            <span style="color: white; font-weight: bold; font-size: 12px;">{score}/10</span>
        </div>
    </div>
    """

def get_risk_status(score):
    """Get risk status and color based on score"""
    if score <= 3:
        return "Low Risk", "status-good"
    elif score <= 6:
        return "Moderate Risk", "status-warning"
    else:
        return "High Risk", "status-danger"

def main():
    # Header
    st.markdown('<div class="main-header">🛡️ ClimaShield</div>', unsafe_allow_html=True)
    
    # Initialize the engine
    if 'engine' not in st.session_state:
        try:
            api_key = st.secrets["OPEN_API_KEY"]
            st.session_state.engine = ClimateInsightEngine(api_key)
            st.success("✅ ClimaShield Engine Loaded Successfully!")
        except Exception as e:
            st.error(f"❌ Error loading engine: {e}")
            st.stop()
    
    # Area selection
    available_areas = load_available_areas()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_area = st.selectbox(
            "🌍 Select Area for Climate Risk Assessment",
            available_areas,
            index=0 if available_areas else 0
        )
        
        analyze_button = st.button("🔍 Analyze Climate Risk", type="primary", use_container_width=True)
    
    if analyze_button and selected_area:
        with st.spinner('🔄 Analyzing climate data...'):
            # Generate insights
            insights = st.session_state.engine.generate_insights(selected_area)
            
            # Store insights in session state
            st.session_state.insights = insights
    
    # Display results if available
    if 'insights' in st.session_state:
        # AI Insights
        st.markdown("---")
        st.markdown("### 🤖 AI Insights & Recommendations")
        
        insight_text = insights.get('ai_insights', 'No AI insights available')
        st.info(insight_text)

        insights = st.session_state.insights
        scores = insights['risk_scores']
        hist = insights['historical_analysis']
        soil = insights['soil_analysis']
        
        st.markdown("---")
        
        # Main climate risk score
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="risk-label">Climate risk score</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="risk-score">{scores["climate_risk_score"]}</div>', unsafe_allow_html=True)
            
            risk_status, status_class = get_risk_status(scores["climate_risk_score"])
            st.markdown(f'<div class="risk-label"><span class="{status_class}">{risk_status}</span></div>', unsafe_allow_html=True)
        
        st.markdown("### Factors contributing to score")
        
        # Risk factors with progress bars
        st.markdown("#### 🌬️ Air quality")
        st.markdown(create_progress_bar(scores['air_quality']), unsafe_allow_html=True)
        st.caption(f"Average AQI: {hist['avg_aqi']} | Trend: {hist['aqi_trend']}")
        
        st.markdown("#### 🏗️ Construction stability")
        st.markdown(create_progress_bar(scores['construction_stability']), unsafe_allow_html=True)
        st.caption(f"Soil: {soil['soil_type']} | Waterlogging Risk: {soil['waterlogging_risk']}/10")
        
        st.markdown("#### 💧 Water management")
        st.markdown(create_progress_bar(scores['water_management']), unsafe_allow_html=True)
        st.caption(f"Avg Rainfall: {hist['avg_rainfall']}mm | Absorption Score: {soil['water_absorption_score']}/10")
        
        # Detailed analysis in expandable sections
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("📊 Detailed Environmental Data"):
                st.metric("Elevation", f"{soil['elevation']}m")
                st.metric("Lake Bed Probability", f"{soil['lake_bed_probability']}/10")
                st.metric("Rainfall Trend", hist['rainfall_trend'])
                st.metric("Data Years Available", f"{len(hist['data_years'])} years")
        
        with col2:
            with st.expander("🎯 Risk Assessment"):
                # Create gauge charts for each factor
                fig_air = create_gauge_chart(scores['air_quality'], "Air Quality Risk")
                st.plotly_chart(fig_air, use_container_width=True)
                
                fig_construction = create_gauge_chart(scores['construction_stability'], "Construction Stability")
                st.plotly_chart(fig_construction, use_container_width=True)
        
        # Current state section
        st.markdown("---")
        st.markdown("### 📈 Current state")
        st.markdown("*Swipe to see what's likely in 10 years*")
        
        # Future predictions placeholder
        with st.expander("🔮 Future Projections (2025-2030)"):
            st.info("📊 Future climate projections will be displayed here based on ML predictions")
            
            # Create a simple projection chart
            years = [2025, 2026, 2027, 2028, 2029, 2030]
            projected_risk = [scores['climate_risk_score'] + np.random.normal(0, 0.5) for _ in years]
            
            fig = px.line(
                x=years, 
                y=projected_risk,
                title="Projected Climate Risk Score Trend",
                labels={'x': 'Year', 'y': 'Risk Score'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Export functionality
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export Report", use_container_width=True):
                st.success("📄 Report export feature coming soon!")
        
        with col2:
            if st.button("📧 Share Analysis", use_container_width=True):
                st.success("📧 Share feature coming soon!")
        
        with col3:
            if st.button("🔄 Analyze Another Area", use_container_width=True):
                if 'insights' in st.session_state:
                    del st.session_state.insights
                st.experimental_rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #7F8C8D;'>
            🛡️ ClimaShield | Powered by Machine Learning & OpenAI<br>
            Building climate-resilient communities through data-driven insights
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 