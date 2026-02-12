import pandas as pd
import os
from datetime import datetime

# Configuration
DATA_DIR = "data"
CUSTOMER_SOURCE = f"{DATA_DIR}/dim_customers.csv" # You might need to generate this first if it doesn't exist
SCD_TARGET = f"{DATA_DIR}/dim_customers_scd2.csv"

def run_scd_type_2():
    print("⏳ STARTING: SCD Type 2 (History Tracking)...")

    # 1. Simulate an Update: Let's pretend Customer C001 moved from Mumbai to Delhi
    # In a real scenario, this comes from a new "Updates File"
    incoming_updates = [
        {"customer_id": "C001", "city": "Delhi", "phone": "9999999999", "updated_at": datetime.now().strftime("%Y-%m-%d")}
    ]
    df_updates = pd.DataFrame(incoming_updates)
    
    # 2. Load Existing Dimension Table
    # If it doesn't exist, create it from the updates (First Load)
    if not os.path.exists(SCD_TARGET):
        print("   - First time load. Creating SCD table.")
        df_updates['start_date'] = df_updates['updated_at']
        df_updates['end_date'] = None
        df_updates['is_current'] = True
        df_updates.to_csv(SCD_TARGET, index=False)
        return

    df_current = pd.read_csv(SCD_TARGET)

    # 3. The Logic: Compare & Expire
    for index, new_row in df_updates.iterrows():
        cust_id = new_row['customer_id']
        
        # Check if customer exists and is active
        mask = (df_current['customer_id'] == cust_id) & (df_current['is_current'] == True)
        
        if not df_current[mask].empty:
            # Get the current record
            current_record = df_current[mask].iloc[0]
            
            # Check if the city actually changed
            if current_record['city'] != new_row['city']:
                print(f"   - ⚠️ DETECTED CHANGE for {cust_id}: {current_record['city']} -> {new_row['city']}")
                
                # A. Expire the old row
                df_current.loc[mask, 'is_current'] = False
                df_current.loc[mask, 'end_date'] = new_row['updated_at']
                
                # B. Add the new row
                new_entry = new_row.copy()
                new_entry['start_date'] = new_row['updated_at']
                new_entry['end_date'] = None
                new_entry['is_current'] = True
                
                # Append strictly using pandas concat
                df_current = pd.concat([df_current, pd.DataFrame([new_entry])], ignore_index=True)
                print(f"   - History Updated: Old Record Expired, New Record Added.")
            else:
                print(f"   - No change detected for {cust_id}.")
        else:
             # New Customer
            new_row['start_date'] = new_row['updated_at']
            new_row['end_date'] = None
            new_row['is_current'] = True
            df_current = pd.concat([df_current, pd.DataFrame([new_row])], ignore_index=True)

    # 4. Save
    df_current.to_csv(SCD_TARGET, index=False)
    print("✅ SCD Type 2 Sync Complete.")

if __name__ == "__main__":
    # Create a dummy customer file first if you don't have one
    if not os.path.exists(SCD_TARGET):
        initial_data = pd.DataFrame([{"customer_id": "C001", "city": "Mumbai", "phone": "1234567890", "start_date": "2024-01-01", "end_date": None, "is_current": True}])
        initial_data.to_csv(SCD_TARGET, index=False)
        
    run_scd_type_2()