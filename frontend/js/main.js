// Process analysis data and display charts
function processAnalysisData() {
    // Display summary data
    displaySummaryData();
    
    // Display tables
    displayTopPerformers();
    displayWorstPerformers();
    displayDeltaTable();
    
    // Fetch chart data from backend
    fetchChartData();
}

// Fetch chart data from backend
async function fetchChartData() {
    try {
        const response = await fetch(`${API_URL}/charts-data/${sessionId}`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch chart data');
        }
        
        const chartData = await response.json();
        
        // Store chart data for use in chart initialization
        window.chartData = chartData;
        
        // Initialize charts
        initializeCharts();
        
        // Add additional chart tabs
        addAdditionalChartTabs();
        
    } catch (error) {
        console.error('Error fetching chart data:', error);
        showAlert(`Failed to load charts: ${error.message}`, 'warning');
        
        // Initialize charts with available data anyway
        initializeCharts();
    }
}// Main JavaScript file for the Stock Trading Performance Analyzer

// API URL - change this if the backend is hosted elsewhere
const API_URL = 'http://localhost:8003';

// Global variables
let sessionId = null;
let analysisData = null;

// DOM elements
const uploadForm = document.getElementById('upload-form');
const kiteFileInput = document.getElementById('kite-file');
const tradingviewFilesInput = document.getElementById('tradingview-files');
const uploadBtn = document.getElementById('upload-btn');
const loadingSpinner = document.getElementById('loading-spinner');
const resultsSection = document.getElementById('results-section');
const alertContainer = document.getElementById('alert-container');
const downloadSummaryBtn = document.getElementById('download-summary');

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Set up event listeners
    uploadForm.addEventListener('submit', handleFileUpload);
    downloadSummaryBtn.addEventListener('click', handleDownloadSummary);
});

// Handle file upload
async function handleFileUpload(event) {
    event.preventDefault();
    
    // Validate files
    if (!kiteFileInput.files.length) {
        showAlert('Please select a Kite Zerodha file.', 'danger');
        return;
    }
    
    if (!tradingviewFilesInput.files.length) {
        showAlert('Please select at least one TradingView file.', 'danger');
        return;
    }
    
    // Show loading spinner
    toggleLoading(true);
    
    // Create form data
    const formData = new FormData();
    formData.append('kite_file', kiteFileInput.files[0]);
    
    // Add all TradingView files
    for (let i = 0; i < tradingviewFilesInput.files.length; i++) {
        formData.append('tradingview_files', tradingviewFilesInput.files[i]);
    }
    
    try {
        // Upload files
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to upload files');
        }
        
        // Store session ID
        sessionId = data.session_id;
        
        // Poll for analysis results
        pollAnalysisResults();
        
    } catch (error) {
        toggleLoading(false);
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

// Poll for analysis results
async function pollAnalysisResults() {
    try {
        // Fetch analysis results
        const response = await fetch(`${API_URL}/analysis/${sessionId}`);
        
        // If not ready yet, try again after a delay
        if (response.status === 404) {
            setTimeout(pollAnalysisResults, 2000);
            return;
        }
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get analysis results');
        }
        
        // Process results
        analysisData = await response.json();
        
        // Display results
        displayResults();
        
    } catch (error) {
        toggleLoading(false);
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

// Display analysis results
function displayResults() {
    // Hide loading spinner and show results
    toggleLoading(false);
    resultsSection.classList.remove('d-none');
    
    // Process and display data
    processAnalysisData();
    
    // Show success message
    showAlert('Analysis completed successfully!', 'success');
}

// Display summary data
function displaySummaryData() {
    // Kite summary
    document.getElementById('kite-total-pnl').textContent = formatCurrency(analysisData.kite_data.summary.total_pnl);
    document.getElementById('kite-avg-pnl-pct').textContent = formatPercentage(analysisData.kite_data.summary.avg_pnl_pct);
    
    // TradingView summary
    document.getElementById('tv-total-pnl').textContent = formatCurrency(analysisData.tradingview_data.summary.total_pnl);
    document.getElementById('tv-avg-pnl-pct').textContent = formatPercentage(analysisData.tradingview_data.summary.avg_pnl_pct);
    
    // Delta summary
    const totalDelta = analysisData.kite_data.summary.total_pnl - analysisData.tradingview_data.summary.total_pnl;
    document.getElementById('total-delta').textContent = formatCurrency(totalDelta);
    
    // Find largest delta
    let largestDelta = 0;
    if (analysisData.delta_data.length > 0) {
        analysisData.delta_data.forEach(row => {
            if (Math.abs(row.Delta) > Math.abs(largestDelta)) {
                largestDelta = row.Delta;
            }
        });
    }
    document.getElementById('largest-delta').textContent = formatCurrency(largestDelta);
}

// Display top performers table
function displayTopPerformers() {
    const tableBody = document.querySelector('#top-performers-table tbody');
    tableBody.innerHTML = '';
    
    analysisData.kite_data.top_5.forEach(stock => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${stock.Symbol}</td>
            <td>${stock.ISIN}</td>
            <td class="${stock['Realized P&L'] >= 0 ? 'positive-value' : 'negative-value'}">${formatCurrency(stock['Realized P&L'])}</td>
            <td class="${stock['Realized P&L Pct.'] >= 0 ? 'positive-value' : 'negative-value'}">${formatPercentage(stock['Realized P&L Pct.'])}</td>
            <td>${formatCurrency(stock['Buy Value'])}</td>
            <td>${formatCurrency(stock['Sell Value'])}</td>
        `;
        tableBody.appendChild(row);
    });
}

// Display worst performers table
function displayWorstPerformers() {
    const tableBody = document.querySelector('#worst-performers-table tbody');
    tableBody.innerHTML = '';
    
    analysisData.kite_data.bottom_5.forEach(stock => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${stock.Symbol}</td>
            <td>${stock.ISIN}</td>
            <td class="${stock['Realized P&L'] >= 0 ? 'positive-value' : 'negative-value'}">${formatCurrency(stock['Realized P&L'])}</td>
            <td class="${stock['Realized P&L Pct.'] >= 0 ? 'positive-value' : 'negative-value'}">${formatPercentage(stock['Realized P&L Pct.'])}</td>
            <td>${formatCurrency(stock['Buy Value'])}</td>
            <td>${formatCurrency(stock['Sell Value'])}</td>
        `;
        tableBody.appendChild(row);
    });
}

// Display delta table
function displayDeltaTable() {
    const tableBody = document.querySelector('#delta-table-data tbody');
    tableBody.innerHTML = '';
    
    // Get top 10 deltas by absolute value
    const deltaRows = [...analysisData.delta_data];
    deltaRows.sort((a, b) => Math.abs(b.Delta) - Math.abs(a.Delta));
    const top10Deltas = deltaRows.slice(0, 10);
    
    top10Deltas.forEach(delta => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${delta.Symbol}</td>
            <td class="${delta.Kite_PnL >= 0 ? 'positive-value' : 'negative-value'}">${formatCurrency(delta.Kite_PnL)}</td>
            <td class="${delta.TradingView_PnL >= 0 ? 'positive-value' : 'negative-value'}">${formatCurrency(delta.TradingView_PnL)}</td>
            <td class="${delta.Delta >= 0 ? 'positive-value' : 'negative-value'}">${formatCurrency(delta.Delta)}</td>
            <td class="${delta.Delta >= 0 ? 'positive-value' : 'negative-value'}">${formatPercentage(delta.Delta_Pct)}</td>
        `;
        tableBody.appendChild(row);
    });
}

// Handle download summary
function handleDownloadSummary(event) {
    event.preventDefault();
    
    if (sessionId) {
        window.open(`${API_URL}/download/${sessionId}`, '_blank');
    } else {
        showAlert('No analysis data available for download.', 'warning');
    }
}

// Show alert message
function showAlert(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

// Toggle loading state
function toggleLoading(isLoading) {
    if (isLoading) {
        loadingSpinner.classList.remove('d-none');
        resultsSection.classList.add('d-none');
        uploadBtn.disabled = true;
    } else {
        loadingSpinner.classList.add('d-none');
        uploadBtn.disabled = false;
    }
}

// Format currency values
function formatCurrency(value) {
    if (value === undefined || value === null) return '-';
    
    const formatter = new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    return formatter.format(value);
}

// Format percentage values
function formatPercentage(value) {
    if (value === undefined || value === null) return '-';
    
    const formatter = new Intl.NumberFormat('en-IN', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    return formatter.format(value / 100);
}

// Add additional chart tabs dynamically
function addAdditionalChartTabs() {
    // Get the tabs container
    const chartTabsList = document.getElementById('chart-tabs');
    const chartTabsContent = document.getElementById('chart-tabs-content');
    
    // Add PnL Distribution tab
    const distributionTab = document.createElement('li');
    distributionTab.className = 'nav-item';
    distributionTab.role = 'presentation';
    distributionTab.innerHTML = `
        <button class="nav-link" id="distribution-tab" data-bs-toggle="tab" 
                data-bs-target="#distribution-chart-tab" type="button" role="tab" 
                aria-controls="distribution-chart-tab" aria-selected="false">P&L Distribution</button>
    `;
    chartTabsList.appendChild(distributionTab);
    
    // Add Buy vs Sell tab
    const buySellTab = document.createElement('li');
    buySellTab.className = 'nav-item';
    buySellTab.role = 'presentation';
    buySellTab.innerHTML = `
        <button class="nav-link" id="buysell-tab" data-bs-toggle="tab" 
                data-bs-target="#buysell-chart-tab" type="button" role="tab" 
                aria-controls="buysell-chart-tab" aria-selected="false">Buy vs Sell</button>
    `;
    chartTabsList.appendChild(buySellTab);
    
    // Add content containers for the new tabs
    const distributionContent = document.createElement('div');
    distributionContent.className = 'tab-pane fade';
    distributionContent.id = 'distribution-chart-tab';
    distributionContent.role = 'tabpanel';
    distributionContent.setAttribute('aria-labelledby', 'distribution-tab');
    distributionContent.innerHTML = `<div id="distribution-chart" class="chart-container"></div>`;
    chartTabsContent.appendChild(distributionContent);
    
    const buySellContent = document.createElement('div');
    buySellContent.className = 'tab-pane fade';
    buySellContent.id = 'buysell-chart-tab';
    buySellContent.role = 'tabpanel';
    buySellContent.setAttribute('aria-labelledby', 'buysell-tab');
    buySellContent.innerHTML = `<div id="buysell-chart" class="chart-container"></div>`;
    chartTabsContent.appendChild(buySellContent);
    
    // Create event listeners to initialize the charts when tabs are clicked
    document.getElementById('distribution-tab').addEventListener('shown.bs.tab', () => {
        const distributionChartContainer = document.getElementById('distribution-chart');
        
        if (window.chartData && window.chartData.pnl_distribution_chart) {
            // Use backend data if available
            const config = {
                responsive: true,
                displayModeBar: true,
                displaylogo: false
            };
            
            Plotly.newPlot(
                distributionChartContainer, 
                window.chartData.pnl_distribution_chart.data, 
                window.chartData.pnl_distribution_chart.layout, 
                config
            );
        } else {
            // Fallback to local data generation
            const stockData = Object.values(analysisData.kite_data.stocks_summary);
            createPnLDistributionChart(distributionChartContainer, stockData);
        }
    });
    
    document.getElementById('buysell-tab').addEventListener('shown.bs.tab', () => {
        const buySellChartContainer = document.getElementById('buysell-chart');
        
        if (window.chartData && window.chartData.buy_sell_chart) {
            // Use backend data if available
            const config = {
                responsive: true,
                displayModeBar: true,
                displaylogo: false
            };
            
            Plotly.newPlot(
                buySellChartContainer, 
                window.chartData.buy_sell_chart.data, 
                window.chartData.buy_sell_chart.layout, 
                config
            );
        } else {
            // Fallback to local data generation
            createBuySellScatterChart(buySellChartContainer, analysisData.kite_data.stocks_summary);
        }
    });
}