import time
import os

# We import the logic you already wrote (reusing your code!)
# NOTE: We use os.system to keep it simple and avoid path/import errors during the hackathon
def run_full_pipeline():
    print("🔄 PIPELINE START: Moving Data from Bronze -> Silver -> Gold")
    
    # 1. Cleaning (Bronze -> Silver)
    os.system("python src/transformation/process_silver_layer.py")
    
    # 2. KPI Calculation (Silver -> Gold)
    os.system("python src/transformation/gold_kpi_logic.py")
    
    print("✅ PIPELINE FINISHED. Dashboard data updated.\n")

if __name__ == "__main__":
    print("🚀 STARTING AUTOMATED PIPELINE ORCHESTRATOR...")
    print("   (Press Ctrl+C to stop)")
    
    try:
        while True:
            run_full_pipeline()
            print("⏳ Waiting 5 seconds before next run...")
            time.sleep(5) 
    except KeyboardInterrupt:
        print("\n🛑 Orchestrator Stopped.")