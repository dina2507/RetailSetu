import time
import subprocess
import sys
import os

# Global variables to track the stream simulator process
stream_process = None

def start_stream_simulator():
    """Starts the stream simulator in background if not already running."""
    global stream_process
    if stream_process is None or stream_process.poll() is not None:
        print("🌊 Starting Stream Simulator...")
        stream_process = subprocess.Popen(
            [sys.executable, "src/ingestion/stream_simulator.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Give it time to start

def run_pipeline():
    """
    Executes the silver and gold layer transformation scripts.
    """
    print("🔄 Running transformation pipeline...")
    
    # Define the scripts to run
    silver_script = "src/transformation/process_silver_layer.py"
    gold_script = "src/transformation/gold_kpi_logic.py"
    
    # Use the current Python executable to run the scripts
    python_executable = sys.executable

    try:
        # Run Silver Layer Transformation
        subprocess.run([python_executable, silver_script], check=True)
        
        # Run Gold Layer/KPI Logic
        subprocess.run([python_executable, gold_script], check=True)
        
        print("✅ Data Pipeline Refreshed")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error occurred while running pipeline scripts: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    print("🚀 Starting Data Pipeline Runner...")
    print("📊 This will run: Stream Simulator + Transformations")
    print("Press Ctrl+C to stop.")
    
    # Start the stream simulator once
    start_stream_simulator()
    
    try:
        while True:
            run_pipeline()
            # Wait for 5 seconds before the next transformation run
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n🛑 Pipeline stopped by user.")
        if stream_process:
            stream_process.terminate()
            print("   Stream simulator stopped.")

if __name__ == "__main__":
    main()