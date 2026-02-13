Data Ingestion Design

1. Batch Ingestion

POS transactions are ingested from silo CSV files using a resilient ingestion pipeline.

2. Retry Strategy

Automatic retry mechanism attempts ingestion up to 3 times in case of failure.

3. Schema Evolution Handling

If new columns appear:

Logged as warning

Automatically handled by pandas

If required columns are missing:

Columns auto-filled with NULL

Error logged

4. Logging

All ingestion events are logged into:

logs/ingestion.log

Includes:

Attempt number

Errors

Warnings

Success confirmation

5. Data Validation

Basic checks:

Negative revenue detection

Missing critical columns handling
