import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os

# Configuration
DATA_DIR = "data"
INPUT_FILE = f"{DATA_DIR}/gold_daily_sales.csv"
OUTPUT_FILE = f"{DATA_DIR}/gold_sales_forecast.csv"

def generate_forecast():
    print("🔮 STARTING: AI Demand Forecasting Model...")
    
    if not os.path.exists(INPUT_FILE):
        print("⚠️ No historical data found. Skipping forecast.")
        return

    # 1. Load Data
    df = pd.read_csv(INPUT_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 2. Feature Engineering (Convert Date to Number for Regression)
    # We map dates to "Day 0, Day 1, Day 2..."
    df['day_index'] = (df['Date'] - df['Date'].min()).dt.days
    
    X = df[['day_index']]  # Input: Time
    y = df['Total_Revenue'] # Output: Sales

    # 3. Train the Model (The "AI" Part)
    model = LinearRegression()
    model.fit(X, y)
    
    print(f"   - Model Trained. Coefficient: {model.coef_[0]:.2f}")

    # 4. Predict Next 7 Days
    last_day = df['day_index'].max()
    future_days = np.array([[last_day + i] for i in range(1, 8)])
    
    predictions = model.predict(future_days)
    
    # 5. Create Forecast DataFrame
    future_dates = [df['Date'].max() + pd.Timedelta(days=i) for i in range(1, 8)]
    
    df_forecast = pd.DataFrame({
        'Date': future_dates,
        'Total_Revenue': predictions,
        'Type': 'Forecast'
    })
    
    # Label historical data
    df['Type'] = 'Historical'
    
    # Combine Past + Future
    final_df = pd.concat([df[['Date', 'Total_Revenue', 'Type']], df_forecast])
    
    # Save
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Forecast generated for next 7 days: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_forecast()