# 🌉 Retail Setu: Supply Chain Command Center

**Retail Setu** is a Unified Intelligence Platform that breaks down data silos for modern retailers. By integrating POS transactions, Warehouse Inventory, and Web Logs into a single "Data Lakehouse," we enable real-time decision-making and AI-driven supply chain optimization.

---

## 🚀 Key Features (The "Wow" Factor)
* **⚡ Real-Time Ingestion:** Continuously streams transaction data to mimic live store activity.
* **🛡️ Resilient Data Pipelines:** Automatically handles **Schema Evolution** (new columns) and includes self-healing retry logic.
* **🧠 AI Narrative Layer:** Built-in AI Executive Assistant that interprets complex KPIs into plain English insights.
* **🕰️ SCD Type 2 History:** Tracks customer movements (e.g., address changes) to preserve historical accuracy.

---

## 🛠️ System Architecture

### 1. Medallion Architecture Strategy
We follow the industry-standard **Bronze $\rightarrow$ Silver $\rightarrow$ Gold** flow:
* **Bronze (Raw):** Immutable ingestion of data from 3 silos (POS, Warehouse, Web).
* **Silver (Cleaned):** Deduplicated and validated data.
    * *Data Contract:* Automatically removes negative prices and future dates.
    * *History:* Implements SCD Type 2 for Customer Dimension.
* **Gold (Curated):** Aggregated KPIs optimized for the dashboard (Star Schema).

### 2. Storage & Security Plan (Problem Statement Requirement)
* **Storage Format:** We use **CSV/Parquet** for the Gold Layer to ensure fast read speeds for the dashboard. In a production environment, this would be stored in **AWS S3** or **Azure Data Lake**.
* **Partitioning:** Data is partitioned by `Date` and `Region` to minimize query costs.
* **Access Control (RBAC):**
    * *Data Engineers:* Read/Write access to Bronze/Silver.
    * *Analysts:* Read-only access to Gold.
    * *PII Protection:* Customer phone numbers are masked in the Gold Layer.

---

## 💻 How to Run Locally

**Prerequisites:** Python 3.9+

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/YourUsername/RetailSetu.git](https://github.com/YourUsername/RetailSetu.git)
    cd RetailSetu
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Launch the System (3-Terminal Setup)**
    * **Terminal 1 (Data Generator):** `python src/orchestration/pipeline_runner.py`
        *(This runs the Ingestion, Cleaning, and KPI logic in a continuous loop)*
    * **Terminal 2 (Dashboard):** `streamlit run src/dashboard/app.py`

4.  **Experience Live AI:**
    * Open the dashboard URL (usually `http://localhost:8501`).
    * Toggle **"Enable Live Mode"** in the sidebar.
    * Watch sales update in real-time!

---

## 🧪 Technology Stack
* **Ingestion:** Python `Faker`, Custom Stream Simulator
* **Processing:** Pandas (Bronze/Silver/Gold transformations)
* **Orchestration:** Custom Python Runner (Simulating Airflow)
* **Visualization:** Streamlit, Plotly
* **CI/CD:** GitHub Actions (Ready for deployment)

---

### 🏆 Hackathon Checklist
- [x] Automated Ingestion (Batch & Real-time)
- [x] Schema Evolution Handling
- [x] Data Quality Contracts (Negative Price Checks)
- [x] SCD Type 2 (History Tracking)
- [x] Interactive AI Dashboard