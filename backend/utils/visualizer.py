import io
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json

def generate_pnl_chart(kite_data: Dict, tradingview_data: Dict) -> io.BytesIO:
    """
    Generate a PnL comparison chart using Plotly
    
    Returns a BytesIO object containing the PNG image
    """
    # Extract data
    symbols = []
    kite_pnl = []
    tv_pnl = []
    
    # Get common symbols
    common_symbols = set(kite_data['stocks_summary'].keys()) & set(tradingview_data['stocks_data'].keys())
    
    for symbol in common_symbols:
        symbols.append(symbol)
        kite_pnl.append(kite_data['stocks_summary'][symbol]['realized_pnl'])
        tv_pnl.append(tradingview_data['stocks_data'][symbol]['realized_pnl'])
    
    # Create DataFrame for easier plotting
    df = pd.DataFrame({
        'Symbol': symbols,
        'Kite PnL': kite_pnl,
        'TradingView PnL': tv_pnl
    })
    
    # Sort by Kite PnL for better visualization
    df = df.sort_values('Kite PnL', ascending=False)
    
    # Create figure
    fig = make_subplots(rows=1, cols=1)
    
    fig.add_trace(
        go.Bar(
            x=df['Symbol'],
            y=df['Kite PnL'],
            name='Kite PnL',
            marker_color='blue'
        )
    )
    
    fig.add_trace(
        go.Bar(
            x=df['Symbol'],
            y=df['TradingView PnL'],
            name='TradingView PnL',
            marker_color='green'
        )
    )
    
    # Update layout
    fig.update_layout(
        title='P&L Comparison: Kite vs TradingView',
        xaxis_title='Stock Symbol',
        yaxis_title='Realized P&L',
        barmode='group',
        height=600,
        width=1000
    )
    
    # Save to BytesIO
    img_bytes = io.BytesIO()
    fig.write_image(img_bytes, format='png')
    img_bytes.seek(0)
    
    return img_bytes

def generate_delta_chart(delta_data: pd.DataFrame) -> io.BytesIO:
    """
    Generate a delta chart showing the difference between Kite and TradingView data
    
    Returns a BytesIO object containing the PNG image
    """
    # Sort by absolute delta
    df = delta_data.sort_values('Delta', key=abs, ascending=False)
    
    # Limit to top 10 for better visualization
    df = df.head(10)
    
    # Create figure
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            x=df['Symbol'],
            y=df['Delta'],
            name='Delta (Kite - TradingView)',
            marker_color=np.where(df['Delta'] >= 0, 'green', 'red')
        )
    )
    
    # Add a horizontal line at y=0
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=0,
        x1=len(df)-0.5,
        y1=0,
        line=dict(
            color="black",
            width=2,
            dash="dot",
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Delta: Kite P&L - TradingView P&L',
        xaxis_title='Stock Symbol',
        yaxis_title='P&L Difference',
        height=600,
        width=1000
    )
    
    # Save to BytesIO
    img_bytes = io.BytesIO()
    fig.write_image(img_bytes, format='png')
    img_bytes.seek(0)
    
    return img_bytes

def generate_pnl_distribution_chart(stock_data: List[Dict]) -> io.BytesIO:
    """
    Generate a P&L distribution pie chart
    
    Returns a BytesIO object containing the PNG image
    """
    # Calculate profit and loss sums
    profit_sum = sum(stock['realized_pnl'] for stock in stock_data if stock['realized_pnl'] >= 0)
    loss_sum = sum(abs(stock['realized_pnl']) for stock in stock_data if stock['realized_pnl'] < 0)
    
    # Create figure
    fig = go.Figure(data=[go.Pie(
        labels=['Profit', 'Loss'],
        values=[profit_sum, loss_sum],
        marker_colors=['rgba(75, 192, 192, 0.8)', 'rgba(255, 99, 132, 0.8)'],
        textinfo='label+percent',
        textposition='inside',
        insidetextorientation='radial'
    )])
    
    # Update layout
    fig.update_layout(
        title='P&L Distribution',
        height=600,
        width=800
    )
    
    # Save to BytesIO
    img_bytes = io.BytesIO()
    fig.write_image(img_bytes, format='png')
    img_bytes.seek(0)
    
    return img_bytes

def generate_buy_sell_chart(stocks_summary: Dict) -> io.BytesIO:
    """
    Generate a buy vs sell scatter chart
    
    Returns a BytesIO object containing the PNG image
    """
    # Prepare data
    symbols = []
    buy_values = []
    sell_values = []
    pnl_values = []
    
    for symbol, data in stocks_summary.items():
        symbols.append(symbol)
        buy_values.append(data['buy_value'])
        sell_values.append(data['sell_value'])
        pnl_values.append(data['realized_pnl'])
    
    # Calculate sizes and colors for markers
    sizes = [abs(pnl) / 1000 + 10 for pnl in pnl_values]  # Size based on absolute P&L
    colors = ['rgba(75, 192, 192, 0.8)' if pnl >= 0 else 'rgba(255, 99, 132, 0.8)' for pnl in pnl_values]
    
    # Create figure
    fig = go.Figure()
    
    # Add scatter plot
    fig.add_trace(go.Scatter(
        x=buy_values,
        y=sell_values,
        mode='markers',
        text=symbols,
        marker=dict(
            size=sizes,
            color=colors,
            opacity=0.7,
            line=dict(
                color='rgb(50, 50, 50)',
                width=1
            )
        ),
        hovertemplate=
            '<b>%{text}</b><br>' +
            'Buy Value: ₹%{x:.2f}<br>' +
            'Sell Value: ₹%{y:.2f}<br>' +
            '<extra></extra>'
    ))
    
    # Add diagonal line (buy = sell)
    max_value = max(max(buy_values), max(sell_values))
    fig.add_trace(go.Scatter(
        x=[0, max_value],
        y=[0, max_value],
        mode='lines',
        name='Break-even Line',
        line=dict(
            color='rgba(0, 0, 0, 0.5)',
            width=2,
            dash='dot'
        ),
        hoverinfo='none'
    ))
    
    # Update layout
    fig.update_layout(
        title='Buy vs. Sell Values',
        xaxis=dict(
            title='Buy Value (₹)',
            zeroline=True
        ),
        yaxis=dict(
            title='Sell Value (₹)',
            zeroline=True
        ),
        hovermode='closest',
        height=600,
        width=800,
        showlegend=False
    )
    
    # Save to BytesIO
    img_bytes = io.BytesIO()
    fig.write_image(img_bytes, format='png')
    img_bytes.seek(0)
    
    return img_bytes

def generate_plotly_json(kite_data: Dict, tradingview_data: Dict, delta_data: pd.DataFrame) -> Dict:
    """
    Generate Plotly JSON data for frontend rendering
    
    Returns a dictionary with Plotly JSON data for different charts
    """
    # PnL Comparison Chart
    symbols = []
    kite_pnl = []
    tv_pnl = []
    
    # Get common symbols
    common_symbols = set(kite_data['stocks_summary'].keys()) & set(tradingview_data['stocks_data'].keys())
    
    for symbol in common_symbols:
        symbols.append(symbol)
        kite_pnl.append(kite_data['stocks_summary'][symbol]['realized_pnl'])
        tv_pnl.append(tradingview_data['stocks_data'][symbol]['realized_pnl'])
    
    # Create DataFrame for easier plotting
    pnl_df = pd.DataFrame({
        'Symbol': symbols,
        'Kite PnL': kite_pnl,
        'TradingView PnL': tv_pnl
    })
    
    # Sort by Kite PnL for better visualization
    pnl_df = pnl_df.sort_values('Kite PnL', ascending=False)
    
    # PnL Comparison Chart JSON
    pnl_chart = {
        'data': [
            {
                'type': 'bar',
                'x': pnl_df['Symbol'].tolist(),
                'y': pnl_df['Kite PnL'].tolist(),
                'name': 'Kite PnL'
            },
            {
                'type': 'bar',
                'x': pnl_df['Symbol'].tolist(),
                'y': pnl_df['TradingView PnL'].tolist(),
                'name': 'TradingView PnL'
            }
        ],
        'layout': {
            'title': 'P&L Comparison: Kite vs TradingView',
            'xaxis': {'title': 'Stock Symbol'},
            'yaxis': {'title': 'Realized P&L'},
            'barmode': 'group'
        }
    }
    
    # Delta Chart
    # Sort by absolute delta
    delta_df = delta_data.sort_values('Delta', key=abs, ascending=False)
    
    # Limit to top 10 for better visualization
    delta_df = delta_df.head(10)
    
    # Delta Chart JSON
    delta_chart = {
        'data': [
            {
                'type': 'bar',
                'x': delta_df['Symbol'].tolist(),
                'y': delta_df['Delta'].tolist(),
                'name': 'Delta (Kite - TradingView)',
                'marker': {
                    'color': ['green' if d >= 0 else 'red' for d in delta_df['Delta'].tolist()]
                }
            }
        ],
        'layout': {
            'title': 'Delta: Kite P&L - TradingView P&L',
            'xaxis': {'title': 'Stock Symbol'},
            'yaxis': {'title': 'P&L Difference'},
            'shapes': [
                {
                    'type': 'line',
                    'x0': -0.5,
                    'y0': 0,
                    'x1': len(delta_df) - 0.5,
                    'y1': 0,
                    'line': {
                        'color': 'black',
                        'width': 2,
                        'dash': 'dot'
                    }
                }
            ]
        }
    }
    
    # Generate additional chart data
    # P&L Distribution data
    kite_stocks_data = list(kite_data['stocks_summary'].values())
    profit_sum = sum(stock['realized_pnl'] for stock in kite_stocks_data if stock['realized_pnl'] >= 0)
    loss_sum = sum(abs(stock['realized_pnl']) for stock in kite_stocks_data if stock['realized_pnl'] < 0)
    
    pnl_distribution_chart = {
        'data': [
            {
                'labels': ['Profit', 'Loss'],
                'values': [profit_sum, loss_sum],
                'type': 'pie',
                'marker': {
                    'colors': ['rgba(75, 192, 192, 0.8)', 'rgba(255, 99, 132, 0.8)']
                },
                'textinfo': 'label+percent',
                'textposition': 'inside',
                'insidetextorientation': 'radial'
            }
        ],
        'layout': {
            'title': 'P&L Distribution',
            'height': 400,
            'width': 500
        }
    }
    
    # Buy vs Sell Scatter data
    buy_sell_data = []
    for symbol, stock in kite_data['stocks_summary'].items():
        buy_sell_data.append({
            'symbol': symbol,
            'buy_value': stock['buy_value'],
            'sell_value': stock['sell_value'],
            'realized_pnl': stock['realized_pnl']
        })
    
    # Create size and color arrays
    if buy_sell_data:  # Check if we have data to work with
        sizes = [abs(item['realized_pnl']) / 1000 + 10 for item in buy_sell_data]
        colors = ['rgba(75, 192, 192, 0.8)' if item['realized_pnl'] >= 0 else 'rgba(255, 99, 132, 0.8)' 
                for item in buy_sell_data]
        
        # Find max value for diagonal line
        max_buy = max([item['buy_value'] for item in buy_sell_data], default=0)
        max_sell = max([item['sell_value'] for item in buy_sell_data], default=0)
        max_value = max(max_buy, max_sell)
        
        buy_sell_chart = {
            'data': [
                {
                    'x': [item['buy_value'] for item in buy_sell_data],
                    'y': [item['sell_value'] for item in buy_sell_data],
                    'mode': 'markers',
                    'type': 'scatter',
                    'text': [item['symbol'] for item in buy_sell_data],
                    'marker': {
                        'size': sizes,
                        'color': colors,
                        'opacity': 0.7
                    }
                },
                # Add diagonal line (buy = sell)
                {
                    'x': [0, max_value],
                    'y': [0, max_value],
                    'mode': 'lines',
                    'type': 'scatter',
                    'name': 'Break-even Line',
                    'line': {
                        'color': 'rgba(0, 0, 0, 0.5)',
                        'width': 2,
                        'dash': 'dot'
                    }
                }
            ],
            'layout': {
                'title': 'Buy vs. Sell Values',
                'xaxis': {'title': 'Buy Value (₹)'},
                'yaxis': {'title': 'Sell Value (₹)'}
            }
        }
    else:
        # Create empty chart if no data is available
        buy_sell_chart = {
            'data': [],
            'layout': {
                'title': 'Buy vs. Sell Values (No Data Available)',
                'xaxis': {'title': 'Buy Value (₹)'},
                'yaxis': {'title': 'Sell Value (₹)'}
            }
        }
    
    return {
        'pnl_chart': pnl_chart,
        'delta_chart': delta_chart,
        'pnl_distribution_chart': pnl_distribution_chart,
        'buy_sell_chart': buy_sell_chart
    }