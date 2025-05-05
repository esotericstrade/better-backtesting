# Stock Trading Performance Analyzer

A full-stack web application for analyzing and comparing stock trading performance data from different sources. This application works entirely in-memory without requiring a database.

## Features

- **File Upload**: Upload Kite Zerodha XLSX/CSV and TradingView CSV files
- **Data Analysis**: Process and compare trading data from different sources
- **Interactive Visualizations**:
  - P&L Comparison Charts (Kite vs TradingView)
  - Delta Analysis Charts
  - P&L Distribution Pie Charts
  - Buy vs Sell Scatter Plot with size-coded bubbles
- **Performance Insights**: Identify top and worst-performing stocks
- **Data Export**: 
  - Download analysis results as CSV
  - Export charts as PNG images

## Project Structure

```
stock-analyzer/
├── backend/
│   ├── app.py                # FastAPI application entry point
│   ├── requirements.txt      # Python dependencies
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_processor.py # Data processing functions
│   │   └── visualizer.py     # Chart generation functions
├── frontend/
│   ├── index.html            # Main application page
│   ├── css/
│   │   └── styles.css        # Custom styles
│   ├── js/
│   │   ├── main.js           # Main application logic
│   │   └── charts.js         # Chart rendering functions
```

## Requirements

### Backend

- Python 3.8+
- FastAPI
- Pandas
- NumPy
- Matplotlib
- Plotly
- Kaleido (for saving Plotly charts)
- Openpyxl (for Excel file processing)

### Frontend

- HTML5
- CSS3
- JavaScript (ES6+)
- Bootstrap 5
- Plotly.js

## Installation and Setup

### Backend Setup

1. Navigate to the backend directory:

```bash
cd stock-analyzer/backend
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the FastAPI server:

```bash
python app.py
```

The backend API will be available at http://localhost:8003.

### Frontend Setup

1. Simply open the `frontend/index.html` file in your web browser.

For development purposes, you can use any local server to serve the frontend files. For example:

```bash
cd stock-analyzer/frontend
python -m http.server 8080
```

Then access the application at http://localhost:8080.

## Usage

1. **Upload Files**:
   - Select a Kite Zerodha XLSX/CSV file
   - Select one or more TradingView CSV files (one per stock)
   - Click "Upload & Analyze"

2. **View Analysis**:
   - Check summary cards for quick insights
   - Explore interactive charts:
     - P&L Comparison: Compare Kite and TradingView P&L values
     - Delta Analysis: View differences between platforms
     - P&L Distribution: See profit vs loss breakdown
     - Buy vs Sell: Visualize trading activity with size-coded bubbles
   - Review detailed data tables for top performers, worst performers, and deltas

3. **Export Results**:
   - Use the "Download Summary CSV" button to export delta analysis
   - Export any chart as PNG using the download buttons below each chart

## Sample Data Format

### Kite Zerodha File Format (CSV/XLSX)

The Kite file should contain the following columns:

```
Symbol, ISIN, Quantity, Buy Value, Sell Value, Realized P&L, Realized P&L Pct., Previous Closing Price, Open Quantity, Open Quantity Type, Open Value, Unrealized P&L, Unrealized P&L Pct.
```

### TradingView File Format (CSV)

TradingView files typically include the following columns:

```
Date/Time, Action (Buy/Sell), Quantity, Price
```

Note: The application attempts to detect column names automatically, so slight variations in column names are supported.

## License

MIT