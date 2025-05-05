import pandas as pd
import numpy as np
import os
from typing import List, Dict

def process_kite_data(file_path: str) -> Dict:
    """
    Process Kite Zerodha XLSX or CSV file
    
    Expected columns:
    Symbol, ISIN, Quantity, Buy Value, Sell Value, Realized P&L, Realized P&L Pct.,
    Previous Closing Price, Open Quantity, Open Quantity Type, Open Value, 
    Unrealized P&L, Unrealized P&L Pct.
    
    Returns a dictionary with processed data
    """
    # Check file extension and read accordingly
    if file_path.lower().endswith('.xlsx'):
        df = pd.read_excel(file_path)
    elif file_path.lower().endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide XLSX or CSV file.")
    
    # Ensure all required columns exist
    required_columns = [
        'Symbol', 'ISIN', 'Quantity', 'Buy Value', 'Sell Value', 
        'Realized P&L', 'Realized P&L Pct.'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in Kite data file")
    
    # Calculate summary statistics
    summary = {
        'total_pnl': df['Realized P&L'].sum(),
        'total_buy_value': df['Buy Value'].sum(),
        'total_sell_value': df['Sell Value'].sum(),
        'avg_pnl_pct': df['Realized P&L Pct.'].mean()
    }
    
    # Get top 5 best and worst performing stocks
    df_sorted = df.sort_values('Realized P&L', ascending=False)
    
    top_5 = df_sorted.head(5).to_dict('records')
    bottom_5 = df_sorted.tail(5).to_dict('records')
    
    # Create per-stock summary
    stocks_summary = {}
    for _, row in df.iterrows():
        symbol = row['Symbol']
        stocks_summary[symbol] = {
            'realized_pnl': row['Realized P&L'],
            'realized_pnl_pct': row['Realized P&L Pct.'],
            'buy_value': row['Buy Value'],
            'sell_value': row['Sell Value']
        }
    
    return {
        'summary': summary,
        'top_5': top_5,
        'bottom_5': bottom_5,
        'stocks_summary': stocks_summary,
        'raw_data': df.to_dict('records')
    }

def process_tradingview_data(file_paths: List[str]) -> Dict:
    """
    Process TradingView CSV files
    
    Expected a list of CSVs, one per stock
    Returns a dictionary with processed data
    """
    all_tradingview_data = {}
    
    for file_path in file_paths:
        # Get stock symbol from filename (assuming format like 'RELIANCE.csv')
        symbol = os.path.basename(file_path).split('.')[0]
        
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Check if required columns exist (different variations possible)
        # Typically: timestamp, action (buy/sell), quantity, price
        valid_cols = False
        
        # Check for common column patterns
        if all(col in df.columns for col in ['Date', 'Action', 'Quantity', 'Price']):
            date_col, action_col, qty_col, price_col = 'Date', 'Action', 'Quantity', 'Price'
            valid_cols = True
        elif all(col in df.columns for col in ['Time', 'Side', 'Amount', 'Price']):
            date_col, action_col, qty_col, price_col = 'Time', 'Side', 'Amount', 'Price'
            valid_cols = True
        elif all(col in df.columns for col in ['date', 'type', 'quantity', 'price']):
            date_col, action_col, qty_col, price_col = 'date', 'type', 'quantity', 'price'
            valid_cols = True
            
        if not valid_cols:
            # Try to infer columns based on data types and names
            date_candidates = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            action_candidates = [col for col in df.columns if 'action' in col.lower() or 'type' in col.lower() or 'side' in col.lower()]
            qty_candidates = [col for col in df.columns if 'qty' in col.lower() or 'quantity' in col.lower() or 'amount' in col.lower()]
            price_candidates = [col for col in df.columns if 'price' in col.lower()]
            
            if date_candidates and action_candidates and qty_candidates and price_candidates:
                date_col = date_candidates[0]
                action_col = action_candidates[0]
                qty_col = qty_candidates[0]
                price_col = price_candidates[0]
                valid_cols = True
        
        if not valid_cols:
            raise ValueError(f"Could not identify required columns in TradingView file: {file_path}")
        
        # Process data
        buy_trades = df[df[action_col].str.lower().isin(['buy', 'b'])]
        sell_trades = df[df[action_col].str.lower().isin(['sell', 's'])]
        
        # Calculate PnL
        total_buy_value = (buy_trades[qty_col] * buy_trades[price_col]).sum()
        total_sell_value = (sell_trades[qty_col] * sell_trades[price_col]).sum()
        
        # Realized PnL
        realized_pnl = total_sell_value - total_buy_value
        
        # Realized PnL percentage
        realized_pnl_pct = (realized_pnl / total_buy_value * 100) if total_buy_value > 0 else 0
        
        # Store processed data
        all_tradingview_data[symbol] = {
            'realized_pnl': realized_pnl,
            'realized_pnl_pct': realized_pnl_pct,
            'buy_value': total_buy_value,
            'sell_value': total_sell_value,
            'raw_data': df.to_dict('records')
        }
    
    # Create summary statistics
    total_pnl = sum(data['realized_pnl'] for data in all_tradingview_data.values())
    total_buy_value = sum(data['buy_value'] for data in all_tradingview_data.values())
    total_sell_value = sum(data['sell_value'] for data in all_tradingview_data.values())
    
    summary = {
        'total_pnl': total_pnl,
        'total_buy_value': total_buy_value,
        'total_sell_value': total_sell_value,
        'avg_pnl_pct': np.mean([data['realized_pnl_pct'] for data in all_tradingview_data.values()])
    }
    
    return {
        'summary': summary,
        'stocks_data': all_tradingview_data
    }

def calculate_deltas(kite_data: Dict, tradingview_data: Dict) -> pd.DataFrame:
    """
    Calculate deltas between Kite and TradingView data
    
    Returns a DataFrame with the comparison results
    """
    # Create a DataFrame to store the comparison
    delta_data = []
    
    # Get all unique symbols
    all_symbols = set(kite_data['stocks_summary'].keys()) | set(tradingview_data['stocks_data'].keys())
    
    for symbol in all_symbols:
        kite_pnl = kite_data['stocks_summary'].get(symbol, {}).get('realized_pnl', 0)
        tv_pnl = tradingview_data['stocks_data'].get(symbol, {}).get('realized_pnl', 0)
        
        delta = kite_pnl - tv_pnl
        delta_pct = 100 * (delta / abs(kite_pnl)) if kite_pnl != 0 else float('inf')
        
        delta_data.append({
            'Symbol': symbol,
            'Kite_PnL': kite_pnl,
            'TradingView_PnL': tv_pnl,
            'Delta': delta,
            'Delta_Pct': delta_pct
        })
    
    # Convert to DataFrame and sort by absolute delta
    df_delta = pd.DataFrame(delta_data)
    df_delta = df_delta.sort_values('Delta', key=abs, ascending=False)
    
    return df_delta
