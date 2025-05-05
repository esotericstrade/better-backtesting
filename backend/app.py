from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import os
import uuid
import shutil
from typing import List
import tempfile
import io
import base64
from starlette.responses import StreamingResponse

# Import utility functions
from utils.data_processor import process_kite_data, process_tradingview_data, calculate_deltas
from utils.visualizer import generate_pnl_chart, generate_delta_chart

app = FastAPI(title="Stock Trading Performance Analyzer")

# Configure CORS to allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for uploaded files and analysis results
uploaded_files = {}
analysis_results = {}

@app.post("/upload")
async def upload_files(
    kite_file: UploadFile = File(...),
    tradingview_files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload Kite and TradingView files for analysis
    """
    session_id = str(uuid.uuid4())
    
    # Create temporary directory for this session
    temp_dir = tempfile.mkdtemp()
    uploaded_files[session_id] = {
        "kite_file": os.path.join(temp_dir, kite_file.filename),
        "tradingview_files": []
    }
    
    # Save Kite file
    with open(uploaded_files[session_id]["kite_file"], "wb") as f:
        shutil.copyfileobj(kite_file.file, f)
    
    # Save TradingView files
    for tv_file in tradingview_files:
        tv_file_path = os.path.join(temp_dir, tv_file.filename)
        with open(tv_file_path, "wb") as f:
            shutil.copyfileobj(tv_file.file, f)
        uploaded_files[session_id]["tradingview_files"].append(tv_file_path)
    
    # Process files in background
    if background_tasks:
        background_tasks.add_task(process_files, session_id)
    else:
        await process_files(session_id)
    
    return {"session_id": session_id, "message": "Files uploaded successfully. Processing started."}

async def process_files(session_id: str):
    """
    Process uploaded files and generate analysis results
    """
    try:
        # Get file paths
        kite_file = uploaded_files[session_id]["kite_file"]
        tradingview_files = uploaded_files[session_id]["tradingview_files"]
        
        # Process data
        kite_data = process_kite_data(kite_file)
        tradingview_data = process_tradingview_data(tradingview_files)
        delta_data = calculate_deltas(kite_data, tradingview_data)
        
        # Store results
        analysis_results[session_id] = {
            "kite_data": kite_data,
            "tradingview_data": tradingview_data,
            "delta_data": delta_data
        }
    except Exception as e:
        # Log the error
        print(f"Error processing files: {str(e)}")
        analysis_results[session_id] = {"error": str(e)}

@app.get("/analysis/{session_id}")
async def get_analysis(session_id: str):
    """
    Get analysis results for a specific session
    """
    if session_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found or still processing")
    
    if "error" in analysis_results[session_id]:
        raise HTTPException(status_code=500, detail=analysis_results[session_id]["error"])
    
    return analysis_results[session_id]

@app.get("/charts/{session_id}/{chart_type}")
async def get_chart(session_id: str, chart_type: str):
    """
    Get chart image for a specific session and chart type
    """
    if session_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found or still processing")
    
    if "error" in analysis_results[session_id]:
        raise HTTPException(status_code=500, detail=analysis_results[session_id]["error"])
    
    try:
        if chart_type == "pnl":
            img_bytes = generate_pnl_chart(
                analysis_results[session_id]["kite_data"],
                analysis_results[session_id]["tradingview_data"]
            )
        elif chart_type == "delta":
            img_bytes = generate_delta_chart(analysis_results[session_id]["delta_data"])
        elif chart_type == "distribution":
            # Generate P&L distribution chart
            stock_data = list(analysis_results[session_id]["kite_data"]["stocks_summary"].values())
            img_bytes = generate_pnl_distribution_chart(stock_data)
        elif chart_type == "buysell":
            # Generate Buy vs Sell scatter chart
            img_bytes = generate_buy_sell_chart(analysis_results[session_id]["kite_data"]["stocks_summary"])
        else:
            raise HTTPException(status_code=400, detail="Invalid chart type")
        
        # Convert to base64 for easier handling in frontend
        return {"chart_data": base64.b64encode(img_bytes.getvalue()).decode("utf-8")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/charts-data/{session_id}")
async def get_charts_data(session_id: str):
    """
    Get all chart data as JSON for a specific session
    """
    if session_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found or still processing")
    
    if "error" in analysis_results[session_id]:
        raise HTTPException(status_code=500, detail=analysis_results[session_id]["error"])
    
    try:
        # Generate all chart data in JSON format
        chart_data = generate_plotly_json(
            analysis_results[session_id]["kite_data"],
            analysis_results[session_id]["tradingview_data"],
            analysis_results[session_id]["delta_data"]
        )
        
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{session_id}")
async def download_summary(session_id: str):
    """
    Download analysis summary as CSV
    """
    if session_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found or still processing")
    
    if "error" in analysis_results[session_id]:
        raise HTTPException(status_code=500, detail=analysis_results[session_id]["error"])
    
    try:
        # Combine data into a single CSV
        delta_data = analysis_results[session_id]["delta_data"]
        csv_content = delta_data.to_csv(index=False)
        
        # Return as downloadable file
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=trading_analysis_summary.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Stock Trading Performance Analyzer API"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8003, reload=True)
