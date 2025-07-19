# ClimaShield-AI 🛡️

Public Deploymemt: https://climashield-ai-dutuse2ruumozk5necijyb.streamlit.app/
List of realworld datasources: https://www.notion.so/ClimaShield-23482e3d81d88025b796fcf45437301c?source=copy_link

For this project we have used synthetic data. Cleaning and using realworld data seemed out of scope for a 24h. But we did deep research to find out what all data sources we can use when building it later.
**AI-Powered Climate Risk Assessment & Prediction Platform**

ClimaShield-AI is an intelligent climate risk assessment system that combines machine learning predictions with AI-powered insights to evaluate environmental risks for construction and urban planning projects.

## 🌟 Features

- **Climate Risk Scoring**: Multi-factor risk assessment (Air Quality, Construction Stability, Water Management)
- **AI-Powered Insights**: OpenAI-powered intelligent analysis and recommendations
- **Predictive Analytics**: ML models for AQI and rainfall predictions (2025-2030)
- **Interactive Dashboard**: Beautiful Streamlit web interface with real-time analysis
- **Soil Analysis**: Comprehensive soil type and elevation-based risk assessment
- **Historical Trend Analysis**: Data-driven trend analysis for informed decision making

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd ClimaShield-AI
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key**

   ```bash
   # Create a .streamlit/secrets.toml file
   echo "OPEN_API_KEY = 'your-openai-api-key-here'" > .streamlit/secrets.toml
   ```

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

## 📊 Usage

1. **Launch the web interface** at `http://localhost:8501`
2. **Select an area** from the dropdown menu
3. **Click "Analyze Climate Risk"** to generate comprehensive insights
4. **Review results** including:
   - AI-generated recommendations
   - Risk scores and visualizations
   - Historical trend analysis
   - Soil characteristics assessment

## 🏗️ Project Structure

```
ClimaShield-AI/
├── src/
│   ├── insight-engine.py    # AI-powered analysis engine
│   ├── ml-engine.py         # Machine learning models
│   └── __init__.py
├── input-data/
│   ├── AQI-Rainfall.csv     # Historical climate data
│   └── Soil_type-Elevation.csv
├── output-data/
│   └── aqi_rainfall_predictions_2025_2030.csv
├── streamlit_app.py         # Web interface
├── requirements.txt         # Python dependencies
└── setup.py                # Package configuration
```

## 🔧 Technical Details

### Core Components

- **ClimateInsightEngine**: OpenAI-powered analysis engine for intelligent insights
- **ML Engine**: Linear regression models for AQI and rainfall predictions
- **Streamlit Interface**: Interactive web dashboard with real-time analysis

### Risk Assessment Factors

1. **Air Quality Score**: Based on historical AQI trends and current levels
2. **Construction Stability**: Evaluated using soil absorption and waterlogging risk
3. **Water Management**: Assessed through rainfall patterns and soil characteristics

### Data Sources

- Historical AQI and rainfall data
- Soil type and elevation information
- ML-generated predictions (2025-2030)

## 🤖 AI Features

- **Intelligent Analysis**: OpenAI GPT models provide contextual insights
- **Risk Recommendations**: AI-generated actionable recommendations
- **Trend Interpretation**: Natural language explanation of data trends

## 📈 Machine Learning

- **Linear Regression Models**: Area-specific AQI and rainfall predictions
- **Multi-factor Analysis**: Comprehensive risk scoring algorithm
- **Predictive Analytics**: Future climate projections (2025-2030)

## 🛠️ Development

### Running ML Models

```bash
python src/ml-engine.py
```

### Package Installation

```bash
pip install -e .
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Vidushee Geetam** - [vidusheegeetam@gmail.com](mailto:vidusheegeetam@gmail.com)

---

**Built with ❤️ for sustainable urban development**
