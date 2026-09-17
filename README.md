# Store Intelligence System (Apex Retail)

An end-to-end computer vision and business analytics pipeline that tracks offline customer behavior and correlates spatial data with POS transactions to generate real-time retail intelligence.

## Quick Setup (Under 5 Commands)

Ensure you have Docker and Docker Compose installed.

1. **Clone the repository and enter the directory:**
```bash
   git clone https://github.com/ishitaag1/StoreVision-AI
   cd StoreVision-AI
```
2. **Boot the entire stack (Database, API, and Frontend):**
```bash
   docker-compose up -d --build
```
3. **Verify the API Health:**
```bash
   curl http://localhost:8000/api/health
```

## Live Dashboard Access
Once Docker is running, access the web interface here: http://localhost:3000

## Running the Vision Pipeline (Detection Layer)
To process the raw CCTV clips and stream data into the API, run the edge tracking script locally.
1. Ensure your virtual environment is active and OpenCV/Ultralytics are installed.
2. Navigate to the pipeline directory and execute the run script:
   ```bash
   cd pipeline
   ./run.bat
   ```
3. Open the Live Stream tab in the Next.js dashboard at http://localhost:3000/live-stream to watch the YOLOv8 telemetry feed render in real-time as the script processes the video!

## Running Automated Tests
To run the Pytest suite (which tests idempotency, schema validation, and edge-case funnel handling):

```bash
cd backend
pytest -v
```
