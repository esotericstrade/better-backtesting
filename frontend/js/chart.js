// Charts.js - Handles chart generation for Stock Trading Performance Analyzer

// Global chart objects
let pnlChart = null;
let deltaChart = null;

// Initialize charts
function initializeCharts() {
    // Get chart containers
    const pnlChartContainer = document.getElementById('pnl-chart');
    const deltaChartContainer = document.getElementById('delta-chart');
    
    // Check if we have backend chart data
    if (window.chartData) {
        // Create charts using backend data
        createPnLChartFromData(pnlChartContainer, window.chartData.pnl_chart);
        createDeltaChartFromData(deltaChartContainer, window.chartData.delta_chart);
    } else {
        // Create charts using local data
        createPnLChart(pnlChartContainer);
        createDeltaChart(deltaChartContainer);
    }
    
    // Set up tab event listeners to redraw charts when tabs are shown
    const chartTabs = document.querySelectorAll('button[data-bs-toggle="tab"]');
    chartTabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', () => {
            if (pnlChart && tab.getAttribute('data-bs-target') === '#pnl-chart-tab') {
                Plotly.relayout(pnlChartContainer, {
                    'xaxis.autorange': true,
                    'yaxis.autorange': true
                });
            }
            if (deltaChart && tab.getAttribute('data-bs-target') === '#delta-chart-tab') {
                Plotly.relayout(deltaChartContainer, {
                    'xaxis.autorange': true,
                    'yaxis.autorange': true
                });
            }
        });
    });
}

// Create P&L Comparison Chart from backend data
function createPnLChartFromData(container, chartData) {
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
    
    pnlChart = Plotly.newPlot(container, chartData.data, chartData.layout, config);
}

// Create Delta Chart from backend data
function createDeltaChartFromData(container, chartData) {
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
    
    deltaChart = Plotly.newPlot(container, chartData.data, chartData.layout, config);
}

// Create P&L Comparison Chart
function createPnLChart(container) {
    // Extract data for the chart
    const symbols = [];
    const kitePnL = [];
    const tvPnL = [];
    
    // Get common symbols between Kite and TradingView
    const kiteSymbols = Object.keys(analysisData.kite_data.stocks_summary);
    const tvSymbols = Object.keys(analysisData.tradingview_data.stocks_data);
    
    // Find common symbols
    const commonSymbols = kiteSymbols.filter(symbol => tvSymbols.includes(symbol));
    
    // If no common symbols, add note to container
    if (commonSymbols.length === 0) {
        const noDataMessage = document.createElement('div');
        noDataMessage.className = 'alert alert-info';
        noDataMessage.textContent = 'No matching symbols found between Kite and TradingView data.';
        container.appendChild(noDataMessage);
        return;
    }
    
    // Prepare data
    commonSymbols.forEach(symbol => {
        const kitePnLValue = analysisData.kite_data.stocks_summary[symbol].realized_pnl;
        const tvPnLValue = analysisData.tradingview_data.stocks_data[symbol].realized_pnl;
        
        symbols.push(symbol);
        kitePnL.push(kitePnLValue);
        tvPnL.push(tvPnLValue);
    });
    
    // Sort by Kite P&L
    const sortedIndices = kitePnL.map((val, idx) => ({ val, idx }))
                                .sort((a, b) => b.val - a.val)
                                .map(item => item.idx);
    
    const sortedSymbols = sortedIndices.map(idx => symbols[idx]);
    const sortedKitePnL = sortedIndices.map(idx => kitePnL[idx]);
    const sortedTvPnL = sortedIndices.map(idx => tvPnL[idx]);
    
    // Create Plotly chart
    const chartData = [
        {
            x: sortedSymbols,
            y: sortedKitePnL,
            type: 'bar',
            name: 'Kite P&L',
            marker: {
                color: 'rgb(49, 130, 189)',
                opacity: 0.8
            }
        },
        {
            x: sortedSymbols,
            y: sortedTvPnL,
            type: 'bar',
            name: 'TradingView P&L',
            marker: {
                color: 'rgb(204, 204, 204)',
                opacity: 0.7
            }
        }
    ];
    
    const layout = {
        title: 'P&L Comparison: Kite vs TradingView',
        xaxis: {
            title: 'Stock Symbol',
            tickangle: -45
        },
        yaxis: {
            title: 'Realized P&L (₹)'
        },
        barmode: 'group',
        bargap: 0.15,
        bargroupgap: 0.1,
        hovermode: 'closest',
        autosize: true,
        margin: {
            l: 80,
            r: 50,
            b: 100,
            t: 100,
            pad: 4
        },
        legend: {
            x: 0,
            y: 1.1,
            orientation: 'h'
        }
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
    
    pnlChart = Plotly.newPlot(container, chartData, layout, config);
}

// Create Delta Chart
function createDeltaChart(container) {
    // Extract data for the chart
    const deltaData = [...analysisData.delta_data];
    
    // Sort by absolute delta
    deltaData.sort((a, b) => Math.abs(b.Delta) - Math.abs(a.Delta));
    
    // Take top 10
    const topDeltas = deltaData.slice(0, 10);
    
    // Prepare data
    const symbols = topDeltas.map(d => d.Symbol);
    const deltas = topDeltas.map(d => d.Delta);
    
    // Create colors based on delta values (green for positive, red for negative)
    const colors = deltas.map(d => d >= 0 ? 'rgba(75, 192, 192, 0.8)' : 'rgba(255, 99, 132, 0.8)');
    
    // Create Plotly chart
    const chartData = [
        {
            x: symbols,
            y: deltas,
            type: 'bar',
            name: 'Delta (Kite - TradingView)',
            marker: {
                color: colors
            }
        }
    ];
    
    const layout = {
        title: 'Delta Analysis: Kite P&L - TradingView P&L',
        xaxis: {
            title: 'Stock Symbol',
            tickangle: -45
        },
        yaxis: {
            title: 'P&L Difference (₹)'
        },
        shapes: [
            {
                type: 'line',
                x0: -0.5,
                y0: 0,
                x1: symbols.length - 0.5,
                y1: 0,
                line: {
                    color: 'rgba(0, 0, 0, 0.5)',
                    width: 2,
                    dash: 'dot'
                }
            }
        ],
        bargap: 0.15,
        hovermode: 'closest',
        autosize: true,
        margin: {
            l: 80,
            r: 50,
            b: 100,
            t: 100,
            pad: 4
        }
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
    
    deltaChart = Plotly.newPlot(container, chartData, layout, config);
}

// Create pie chart for overall P&L distribution
function createPnLDistributionChart(container, pnlData) {
    // Categorize P&L into profit and loss
    let profitSum = 0;
    let lossSum = 0;
    
    pnlData.forEach(stock => {
        if (stock.realized_pnl >= 0) {
            profitSum += stock.realized_pnl;
        } else {
            lossSum += Math.abs(stock.realized_pnl);
        }
    });
    
    // Prepare data for pie chart
    const chartData = [
        {
            labels: ['Profit', 'Loss'],
            values: [profitSum, lossSum],
            type: 'pie',
            marker: {
                colors: ['rgba(75, 192, 192, 0.8)', 'rgba(255, 99, 132, 0.8)']
            },
            textinfo: 'label+percent',
            textposition: 'inside',
            insidetextorientation: 'radial'
        }
    ];
    
    const layout = {
        title: 'P&L Distribution',
        height: 400,
        width: 500,
        margin: {
            l: 50,
            r: 50,
            b: 50,
            t: 50,
            pad: 4
        }
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false
    };
    
    Plotly.newPlot(container, chartData, layout, config);
}

// Create scatter plot for comparing buy/sell values
function createBuySellScatterChart(container, stocksData) {
    // Prepare data for scatter plot
    const symbols = [];
    const buyValues = [];
    const sellValues = [];
    const pnlValues = [];
    
    // Extract data
    for (const symbol in stocksData) {
        const stock = stocksData[symbol];
        symbols.push(symbol);
        buyValues.push(stock.buy_value);
        sellValues.push(stock.sell_value);
        pnlValues.push(stock.realized_pnl);
    }
    
    // Create size and color arrays for bubbles
    const sizes = pnlValues.map(pnl => Math.abs(pnl) / 1000 + 10); // Size based on absolute P&L
    const colors = pnlValues.map(pnl => pnl >= 0 ? 'rgba(75, 192, 192, 0.8)' : 'rgba(255, 99, 132, 0.8)');
    
    // Create Plotly chart
    const chartData = [
        {
            x: buyValues,
            y: sellValues,
            mode: 'markers',
            type: 'scatter',
            text: symbols,
            marker: {
                size: sizes,
                color: colors,
                opacity: 0.7,
                line: {
                    color: 'rgb(50, 50, 50)',
                    width: 1
                }
            },
            hovertemplate: 
                '<b>%{text}</b><br>' +
                'Buy Value: ₹%{x:.2f}<br>' +
                'Sell Value: ₹%{y:.2f}<br>' +
                '<extra></extra>'
        }
    ];
    
    // Add diagonal line (buy = sell)
    const maxValue = Math.max(...buyValues, ...sellValues);
    chartData.push({
        x: [0, maxValue],
        y: [0, maxValue],
        mode: 'lines',
        type: 'scatter',
        name: 'Break-even Line',
        line: {
            color: 'rgba(0, 0, 0, 0.5)',
            width: 2,
            dash: 'dot'
        },
        hoverinfo: 'none'
    });
    
    const layout = {
        title: 'Buy vs. Sell Values',
        xaxis: {
            title: 'Buy Value (₹)',
            zeroline: true
        },
        yaxis: {
            title: 'Sell Value (₹)',
            zeroline: true
        },
        hovermode: 'closest',
        autosize: true,
        margin: {
            l: 80,
            r: 50,
            b: 80,
            t: 100,
            pad: 4
        },
        showlegend: false
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false
    };
    
    Plotly.newPlot(container, chartData, layout, config);
}

// Handle window resize to make charts responsive
window.addEventListener('resize', () => {
    if (pnlChart) {
        Plotly.relayout('pnl-chart', {
            'xaxis.autorange': true,
            'yaxis.autorange': true
        });
    }
    
    if (deltaChart) {
        Plotly.relayout('delta-chart', {
            'xaxis.autorange': true,
            'yaxis.autorange': true
        });
    }
});

// Export chart data for download
function exportChartAsImage(chartId, filename) {
    const chartContainer = document.getElementById(chartId);
    
    Plotly.downloadImage(chartContainer, {
        format: 'png',
        width: 1200,
        height: 800,
        filename: filename
    });
}

// Update chart with new data
function updateChart(chartContainer, newData, newLayout) {
    Plotly.react(chartContainer, newData, newLayout);
}