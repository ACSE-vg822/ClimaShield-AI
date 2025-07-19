import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import os

def load_and_clean_data():
    data = pd.read_csv('input-data/AQI-Rainfall.csv')
    data['Rainfall_numeric'] = data['Rainfall (mm)'].str.replace(' mm', '').astype(float)
    return data

def train_models_per_area(data):
    models = {}
    unique_areas = data['Area'].unique()
    
    for area in unique_areas:
        area_data = data[data['Area'] == area]
        
        if len(area_data) > 1:  # Need at least 2 points for linear regression
            X = area_data[['Year']].values
            y_aqi = area_data['AQI'].values
            y_rainfall = area_data['Rainfall_numeric'].values
            
            # Train AQI model for this area
            model_aqi = LinearRegression()
            model_aqi.fit(X, y_aqi)
            
            # Train Rainfall model for this area
            model_rainfall = LinearRegression()
            model_rainfall.fit(X, y_rainfall)
            
            models[area] = {
                'aqi_model': model_aqi,
                'rainfall_model': model_rainfall
            }
    
    return models

def generate_predictions(models, data):
    results = []
    
    # Add historical data
    for _, row in data.iterrows():
        results.append({
            'Year': row['Year'],
            'Area': row['Area'],
            'AQI': row['AQI'],
            'Rainfall_mm': row['Rainfall_numeric']
        })
    
    # Add predictions for each area
    future_years = np.arange(2025, 2031).reshape(-1, 1)
    
    for area, area_models in models.items():
        future_aqi = area_models['aqi_model'].predict(future_years)
        future_rainfall = area_models['rainfall_model'].predict(future_years)
        
        for i, year in enumerate(range(2025, 2031)):
            results.append({
                'Year': year,
                'Area': area,
                'AQI': round(future_aqi[i], 1),
                'Rainfall_mm': round(future_rainfall[i], 1)
            })
    
    return pd.DataFrame(results)

def save_results(results_df):
    os.makedirs('output-data', exist_ok=True)
    results_df.to_csv('output-data/aqi_rainfall_predictions_2025_2030.csv', index=False)

def main():
    print("ClimaShield AI - Processing...")
    
    data = load_and_clean_data()
    models = train_models_per_area(data)
    results_df = generate_predictions(models, data)
    save_results(results_df)
    
    print("✅ Analysis complete - Results saved to output-data/")

if __name__ == "__main__":
    main()
