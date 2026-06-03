@echo off
echo ====================================================================
echo 🚀 LAUNCHING STORE INTELLIGENCE SYSTEM OFFLINE INGESTION PIPELINE
echo ====================================================================

:: Ensure the local Python virtual execution sandbox environment is activated
call ..\venv\Scripts\activate

echo 🔌 Ingesting Entry/Exit Threshold CCTV Segment...
:: Linked to CAM 1 - zone.mp4 (Matched with your specific folder file name)
python detect.py "CAM 1 - zone.mp4" "CAM_ENTRY_01"

echo 🔌 Ingesting Store Floor Zone Spatial Coverage CCTV Segment...
:: Linked to CAM 2 - floor.mp4
python detect.py "CAM 2 - zone.mp4" "CAM_FLOOR_01"

echo 🔌 Ingesting Checkout Counter Queue Management CCTV Segment...
:: Linked to CAM 5 - billing.mp4
python detect.py "CAM 5 - billing.mp4" "CAM_BILLING_01"

echo ====================================================================
echo 🎉 ALL CCTV FOOTAGE LOG DATA STREAMS INGESTED INTO MONGO MATRIX SUCCESSFULLY!
echo ====================================================================
pause