import pandas as pd
import numpy as np
import openai
import os
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class ClimateInsightEngine:
    def __init__(self, openai_api_key: str):
        """
        Initialize the Climate Insight Engine
        
        Args:
            openai_api_key: OpenAI API key for intelligent analysis
        """
        openai.api_key = openai_api_key
        self.client = openai.OpenAI(api_key=openai_api_key)
        
        # Load data files
        self.aqi_rainfall_data = None
        self.soil_elevation_data = None
        self.predictions_data = None
        
        # Soil type water absorption mapping (lower score = less absorption = higher waterlogging risk)
        self.soil_absorption_map = {
            'Clayey Soil': 2,  # Poor drainage, high waterlogging risk
            'Red Loamy Soil': 7,  # Good drainage
            'Laterite Soil': 5,  # Moderate drainage
            'Sandy Soil': 9,  # Excellent drainage
            'Black Cotton Soil': 1,  # Very poor drainage, high expansion-contraction
            'Alluvial Soil': 6  # Good drainage
        }
        
        self.load_data()
    
    def load_data(self):
        """Load all required data files"""
        try:
            # Load historical AQI and rainfall data
            self.aqi_rainfall_data = pd.read_csv('input-data/AQI-Rainfall.csv')
            
            # Load soil and elevation data
            self.soil_elevation_data = pd.read_csv('input-data/Soil_type-Elevation.csv')
            
            # Load predictions data
            self.predictions_data = pd.read_csv('output-data/aqi_rainfall_predictions_2025_2030.csv')
            
            # Clean the data
            self._clean_data()
            
            print("✅ Data loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
    
    def _clean_data(self):
        """Clean and preprocess the data"""
        # Clean AQI rainfall data - remove 'mm' and 'meters' suffixes
        if 'Rainfall (mm)' in self.aqi_rainfall_data.columns:
            self.aqi_rainfall_data['Rainfall'] = self.aqi_rainfall_data['Rainfall (mm)'].str.replace(' mm', '').astype(float)
        
        # Clean soil elevation data
        if 'Elevation (m)' in self.soil_elevation_data.columns:
            self.soil_elevation_data['Elevation'] = self.soil_elevation_data['Elevation (m)'].str.replace(' meters', '').astype(float)
    
    def analyze_historical_trends(self, area: str) -> Dict:
        """
        Analyze historical AQI and rainfall trends for an area
        
        Args:
            area: Name of the area to analyze
            
        Returns:
            Dictionary containing trend analysis
        """
        # Filter data for the specific area
        area_data = self.aqi_rainfall_data[self.aqi_rainfall_data['Area'] == area].copy()
        
        if area_data.empty:
            return {
                'aqi_trend': 'No data available',
                'rainfall_trend': 'No data available',
                'aqi_score': 5,  # Neutral score
                'rainfall_score': 5,
                'data_years': []
            }
        
        # Calculate trends
        aqi_values = area_data['AQI'].values
        rainfall_values = area_data['Rainfall'].values
        years = area_data['Year'].values
        
        # Calculate trend direction
        aqi_trend = 'stable'
        rainfall_trend = 'stable'
        
        if len(aqi_values) > 1:
            aqi_slope = np.polyfit(range(len(aqi_values)), aqi_values, 1)[0]
            if aqi_slope > 2:
                aqi_trend = 'worsening'
            elif aqi_slope < -2:
                aqi_trend = 'improving'
        
        if len(rainfall_values) > 1:
            rainfall_slope = np.polyfit(range(len(rainfall_values)), rainfall_values, 1)[0]
            if rainfall_slope > 10:
                rainfall_trend = 'increasing'
            elif rainfall_slope < -10:
                rainfall_trend = 'decreasing'
        
        # Calculate scores (1-10 scale)
        avg_aqi = np.mean(aqi_values)
        avg_rainfall = np.mean(rainfall_values)
        
        # AQI Score (lower AQI is better, so invert the score)
        aqi_score = max(1, min(10, 10 - (avg_aqi / 50) * 9))
        
        # Rainfall Score (moderate rainfall is best, too much or too little is bad)
        optimal_rainfall = 1200  # mm per year
        rainfall_deviation = abs(avg_rainfall - optimal_rainfall) / optimal_rainfall
        rainfall_score = max(1, min(10, 10 - rainfall_deviation * 9))
        
        return {
            'aqi_trend': aqi_trend,
            'rainfall_trend': rainfall_trend,
            'aqi_score': round(aqi_score, 1),
            'rainfall_score': round(rainfall_score, 1),
            'avg_aqi': round(avg_aqi, 1),
            'avg_rainfall': round(avg_rainfall, 1),
            'data_years': list(years)
        }
    
    def analyze_soil_characteristics(self, area: str) -> Dict:
        """
        Analyze soil type and elevation to determine lake bed probability and water absorption
        
        Args:
            area: Name of the area to analyze
            
        Returns:
            Dictionary containing soil analysis
        """
        # Filter soil data for the area
        soil_data = self.soil_elevation_data[self.soil_elevation_data['Area'] == area]
        
        if soil_data.empty:
            return {
                'soil_type': 'Unknown',
                'elevation': 0,
                'lake_bed_probability': 5,
                'water_absorption_score': 5,
                'waterlogging_risk': 5
            }
        
        # Get soil type and elevation (take first match if multiple)
        soil_type = soil_data.iloc[0]['Soil Type']
        elevation = soil_data.iloc[0]['Elevation']
        
        # Calculate lake bed probability based on elevation and soil type
        # Lower elevation + clayey soil = higher lake bed probability
        elevation_factor = max(0, (1000 - elevation) / 1000)  # Normalized elevation factor
        soil_factor = 0.8 if 'Clayey' in soil_type else 0.3
        lake_bed_probability = min(10, max(1, (elevation_factor + soil_factor) * 10))
        
        # Get water absorption score from soil type
        absorption_score = self.soil_absorption_map.get(soil_type, 5)
        
        # Calculate waterlogging risk (inverse of absorption + elevation factor)
        waterlogging_risk = max(1, min(10, 11 - absorption_score + elevation_factor * 3))
        
        return {
            'soil_type': soil_type,
            'elevation': elevation,
            'lake_bed_probability': round(lake_bed_probability, 1),
            'water_absorption_score': absorption_score,
            'waterlogging_risk': round(waterlogging_risk, 1)
        }
    
    def calculate_risk_scores(self, historical_analysis: Dict, soil_analysis: Dict) -> Dict:
        """
        Calculate climate risk scores for different factors
        
        Args:
            historical_analysis: Historical trend analysis results
            soil_analysis: Soil characteristics analysis results
            
        Returns:
            Dictionary containing risk scores
        """
        # Air Quality Score (based on AQI trends)
        air_quality_score = historical_analysis['aqi_score']
        
        # Construction Stability Score (based on soil absorption and waterlogging risk)
        # Lower waterlogging risk = higher construction stability
        construction_stability = max(1, min(10, 11 - soil_analysis['waterlogging_risk']))
        
        # Water Management Score (based on rainfall trends and absorption)
        water_mgmt_base = (historical_analysis['rainfall_score'] + soil_analysis['water_absorption_score']) / 2
        water_management_score = min(10, max(1, water_mgmt_base))
        
        # Overall Climate Risk Score (inverted - lower is better for risk)
        overall_score = (air_quality_score + construction_stability + water_management_score) / 3
        climate_risk_score = max(1, min(10, 11 - overall_score))  # Invert so higher = more risk
        
        return {
            'air_quality': round(air_quality_score, 1),
            'construction_stability': round(construction_stability, 1),
            'water_management': round(water_management_score, 1),
            'climate_risk_score': round(climate_risk_score, 1)
        }
    
    def get_ai_insights(self, area: str, analysis_data: Dict) -> str:
        """
        Use OpenAI to generate intelligent insights about the area
        
        Args:
            area: Area name
            analysis_data: Complete analysis data
            
        Returns:
            AI-generated insights string
        """
        try:
            prompt = f"""
            Analyze the climate risk data for {area} and provide a brief, actionable insight (2-3 sentences max):
            
            Climate Risk Score: {analysis_data['risk_scores']['climate_risk_score']}/10
            Air Quality Score: {analysis_data['risk_scores']['air_quality']}/10  
            Construction Stability: {analysis_data['risk_scores']['construction_stability']}/10
            Water Management: {analysis_data['risk_scores']['water_management']}/10
            
            Soil Type: {analysis_data['soil_analysis']['soil_type']}
            Waterlogging Risk: {analysis_data['soil_analysis']['waterlogging_risk']}/10
            AQI Trend: {analysis_data['historical_analysis']['aqi_trend']}
            Rainfall Trend: {analysis_data['historical_analysis']['rainfall_trend']}
            
            Focus on the biggest risks and actionable recommendations.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a climate risk analyst providing brief, actionable insights for urban planning."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"AI analysis unavailable: {str(e)}"
    
    def generate_insights(self, area: str) -> Dict:
        """
        Generate comprehensive climate insights for an area
        
        Args:
            area: Name of the area to analyze
            
        Returns:
            Complete insights dictionary
        """
        print(f"\n🔍 Analyzing climate risks for: {area}")
        print("=" * 50)
        
        # Perform all analyses
        historical_analysis = self.analyze_historical_trends(area)
        soil_analysis = self.analyze_soil_characteristics(area)
        risk_scores = self.calculate_risk_scores(historical_analysis, soil_analysis)
        
        # Compile complete analysis
        complete_analysis = {
            'area': area,
            'historical_analysis': historical_analysis,
            'soil_analysis': soil_analysis,
            'risk_scores': risk_scores
        }
        
        # Get AI insights
        ai_insights = self.get_ai_insights(area, complete_analysis)
        complete_analysis['ai_insights'] = ai_insights
        
        return complete_analysis
    
    def display_insights(self, insights: Dict):
        """
        Display insights in a formatted way
        
        Args:
            insights: Complete insights dictionary
        """
        area = insights['area']
        hist = insights['historical_analysis']
        soil = insights['soil_analysis']
        scores = insights['risk_scores']
        
        print(f"\n📊 CLIMATE RISK ASSESSMENT FOR {area.upper()}")
        print("=" * 60)
        
        print(f"\n🎯 CLIMATE RISK SCORE: {scores['climate_risk_score']}/10")
        print("\n📈 RISK FACTORS:")
        
        # Create progress bars for visualization
        def create_progress_bar(score, max_score=10, length=20):
            filled = int((score / max_score) * length)
            return "█" * filled + "░" * (length - filled)
        
        print(f"   🌬️  Air Quality:         {create_progress_bar(scores['air_quality'])} {scores['air_quality']}/10")
        print(f"   🏗️  Construction Stability: {create_progress_bar(scores['construction_stability'])} {scores['construction_stability']}/10")
        print(f"   💧 Water Management:     {create_progress_bar(scores['water_management'])} {scores['water_management']}/10")
        
        print(f"\n📋 DETAILED ANALYSIS:")
        print(f"   • Soil Type: {soil['soil_type']}")
        print(f"   • Elevation: {soil['elevation']}m")
        print(f"   • Average AQI: {hist['avg_aqi']} ({hist['aqi_trend']} trend)")
        print(f"   • Average Rainfall: {hist['avg_rainfall']}mm ({hist['rainfall_trend']} trend)")
        print(f"   • Waterlogging Risk: {soil['waterlogging_risk']}/10")
        print(f"   • Lake Bed Probability: {soil['lake_bed_probability']}/10")
        
        print(f"\n🤖 AI INSIGHTS:")
        print(f"   {insights['ai_insights']}")
        
        print("\n" + "=" * 60)


# Main testing block
if __name__ == "__main__":
    # Set your OpenAI API key here
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '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')
 
    # Initialize the insight engine
    try:
        engine = ClimateInsightEngine(OPENAI_API_KEY)
        
        # Test with different areas
        test_areas = ['Koramangala', 'Hebbal', 'Malleswaram', 'Anekal']
        
        print("🌍 CLIMASHIELD - INSIGHT ENGINE")
        print("====================================")
        
        # Interactive mode
        while True:
            print("\n" + "="*50)
            print("Available test areas:", ", ".join(test_areas))
            area_input = input("\nEnter area name (or 'quit' to exit): ").strip()
            
            if area_input.lower() == 'quit':
                print("👋 Thank you for using ClimaShield!")
                break
            
            if not area_input:
                area_input = 'Koramangala'  # Default for testing
                print(f"Using default area: {area_input}")
            
            # Generate and display insights
            insights = engine.generate_insights(area_input)
            engine.display_insights(insights)
            
            # Ask if user wants to continue
            continue_choice = input("\nAnalyze another area? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("👋 Thank you for using ClimaShield!")
                break
                
    except Exception as e:
        print(f"❌ Error initializing engine: {e}")
        print("Make sure your OpenAI API key is set correctly.")
