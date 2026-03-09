"""
Weekly Portfolio Tracker
Sends a weekly email summary of your stock portfolio.
Handles multiple currencies and converts everything to EUR.
"""

import os
import json
import yfinance as yf
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def load_portfolio():
    """Load portfolio from environment variable or local file"""
    # Try environment variable first (for GitHub Actions)
    portfolio_json = os.environ.get('PORTFOLIO_DATA')
    if portfolio_json:
        return json.loads(portfolio_json)
    
    # Otherwise load from local file (for testing)
    if os.path.exists('portfolio.json'):
        with open('portfolio.json', 'r') as f:
            return json.load(f)
    
    return {}

def get_exchange_rate(from_currency, to_currency='EUR'):
    """Get current exchange rate"""
    if from_currency == to_currency:
        return 1.0
    
    try:
        # Use Yahoo Finance forex data
        ticker = f"{from_currency}{to_currency}=X"
        data = yf.download(ticker, period='1d', progress=False)
        rate = data['Close'].iloc[-1]
        return float(rate)
    except:
        print(f"Warning: Could not fetch {from_currency} to {to_currency} rate, using 1.0")
        return 1.0

def fetch_stock_data(tickers):
    """Fetch current prices and weekly change for all tickers"""
    prices = {}
    weekly_changes = {}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            
            # Get current price
            hist = stock.history(period='7d')
            current_price = hist['Close'].iloc[-1]
            prices[ticker] = float(current_price)
            
            # Calculate weekly change
            if len(hist) >= 2:
                week_ago = hist['Close'].iloc[0]
                change_pct = ((current_price - week_ago) / week_ago) * 100
                weekly_changes[ticker] = float(change_pct)
            else:
                weekly_changes[ticker] = 0.0
            
            print(f"✓ {ticker}: {current_price:.2f}")
            
        except Exception as e:
            print(f"✗ {ticker}: Failed ({e})")
            prices[ticker] = None
            weekly_changes[ticker] = 0.0
    
    return prices, weekly_changes

def calculate_portfolio(portfolio, prices, weekly_changes):
    """Calculate portfolio value in EUR"""
    
    # Get exchange rates for all currencies needed
    exchange_rates = {}
    for ticker, data in portfolio.items():
        currency = data.get('currency', 'EUR')
        if currency not in exchange_rates:
            exchange_rates[currency] = get_exchange_rate(currency, 'EUR')
            print(f"Exchange rate {currency}/EUR: {exchange_rates[currency]:.4f}")
    
    holdings = []
    total_value_eur = 0
    total_cost_eur = 0
    
    for ticker, data in portfolio.items():
        shares = data['shares']
        buy_price = data['buy_price']
        currency = data.get('currency', 'EUR')
        current_price = prices.get(ticker)
        week_change = weekly_changes.get(ticker, 0)
        
        if current_price is None:
            continue
        
        # Convert to EUR
        rate = exchange_rates[currency]
        buy_price_eur = buy_price * rate
        current_price_eur = current_price * rate
        
        # Calculate values in EUR
        cost_basis_eur = shares * buy_price_eur
        current_value_eur = shares * current_price_eur
        profit_loss_eur = current_value_eur - cost_basis_eur
        profit_loss_pct = (profit_loss_eur / cost_basis_eur) * 100 if cost_basis_eur > 0 else 0
        
        holdings.append({
            'ticker': ticker,
            'shares': shares,
            'currency': currency,
            'buy_price': buy_price,
            'current_price': current_price,
            'buy_price_eur': buy_price_eur,
            'current_price_eur': current_price_eur,
            'current_value_eur': current_value_eur,
            'profit_loss_eur': profit_loss_eur,
            'profit_loss_pct': profit_loss_pct,
            'week_change': week_change
        })
        
        total_value_eur += current_value_eur
        total_cost_eur += cost_basis_eur
    
    total_profit_loss_eur = total_value_eur - total_cost_eur
    total_return_pct = (total_profit_loss_eur / total_cost_eur) * 100 if total_cost_eur > 0 else 0
    
    # Sort by value (largest first)
    holdings.sort(key=lambda x: x['current_value_eur'], reverse=True)
    
    return {
        'holdings': holdings,
        'total_value': total_value_eur,
        'total_cost': total_cost_eur,
        'total_profit_loss': total_profit_loss_eur,
        'total_return_pct': total_return_pct
    }

def create_html_email(summary):
    """Create HTML email"""
    
    holdings = summary['holdings']
    total_value = summary['total_value']
    total_profit_loss = summary['total_profit_loss']
    total_return_pct = summary['total_return_pct']
    
    # Status color
    status_color = "#2ECC71" if total_profit_loss >= 0 else "#E74C3C"
    status_emoji = "📈" if total_profit_loss >= 0 else "📉"
    
    # Build table rows
    rows_html = ""
    for h in holdings:
        row_color = "#D5F5E3" if h['profit_loss_eur'] >= 0 else "#FADBD8"
        week_color = "#2ECC71" if h['week_change'] >= 0 else "#E74C3C"
        
        # Show original currency in parentheses if not EUR
        price_display = f"€{h['current_price_eur']:.2f}"
        if h['currency'] != 'EUR':
            price_display += f" ({h['currency']}{h['current_price']:.2f})"
        
        rows_html += f"""
        <tr style="background-color: {row_color};">
            <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">{h['ticker']}</td>
            <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">{h['shares']}</td>
            <td style="padding: 12px; border: 1px solid #ddd; text-align: right;">{price_display}</td>
            <td style="padding: 12px; border: 1px solid #ddd; text-align: right;">€{h['current_value_eur']:.2f}</td>
            <td style="padding: 12px; border: 1px solid #ddd; text-align: right; font-weight: bold;">
                €{h['profit_loss_eur']:+.2f} ({h['profit_loss_pct']:+.1f}%)
            </td>
            <td style="padding: 12px; border: 1px solid #ddd; text-align: right; color: {week_color};">
                {h['week_change']:+.1f}%
            </td>
        </tr>
        """
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
            
            <div style="background: {status_color}; color: white; padding: 30px; border-radius: 10px; text-align: center;">
                <h1>{status_emoji} Weekly Portfolio Update</h1>
                <p>{datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 5px solid {status_color};">
                <h2>Summary</h2>
                <p style="font-size: 28px; font-weight: bold; color: {status_color}; margin: 10px 0;">
                    €{total_value:,.2f}
                </p>
                <p style="font-size: 20px; color: {status_color};">
                    €{total_profit_loss:+,.2f} ({total_return_pct:+.2f}%)
                </p>
            </div>
            
            <h2>Holdings</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th style="background: #34495E; color: white; padding: 12px; text-align: left;">Ticker</th>
                        <th style="background: #34495E; color: white; padding: 12px; text-align: center;">Shares</th>
                        <th style="background: #34495E; color: white; padding: 12px; text-align: right;">Price</th>
                        <th style="background: #34495E; color: white; padding: 12px; text-align: right;">Value</th>
                        <th style="background: #34495E; color: white; padding: 12px; text-align: right;">Gain/Loss</th>
                        <th style="background: #34495E; color: white; padding: 12px; text-align: right;">7-Day</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            
            <p style="text-align: center; color: #999; font-size: 12px; margin-top: 30px;">
                Generated {datetime.now().strftime('%I:%M %p')} • Data from Yahoo Finance
            </p>
        </div>
    </body>
    </html>
    """
    
    return html

def send_email(subject, html, email_config):
    """Send email via Gmail"""
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = email_config['from']
    msg['To'] = email_config['to']
    msg.attach(MIMEText(html, 'html'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_config['from'], email_config['password'])
            smtp.send_message(msg)
        print("✓ Email sent!")
        return True
    except Exception as e:
        print(f"✗ Email failed: {e}")
        return False

def main():
    """Main function"""
    print("="*60)
    print("Weekly Portfolio Tracker")
    print("="*60)
    
    # Load portfolio
    portfolio = load_portfolio()
    if not portfolio:
        print("Error: No portfolio found")
        return
    
    print(f"Loaded {len(portfolio)} holdings\n")
    
    # Get email config
    email_config = {
        'from': os.environ.get('EMAIL_FROM', ''),
        'to': os.environ.get('EMAIL_TO', ''),
        'password': os.environ.get('EMAIL_PASSWORD', '')
    }
    
    # Fetch data
    tickers = list(portfolio.keys())
    print("Fetching prices...")
    prices, weekly_changes = fetch_stock_data(tickers)
    print()
    
    # Calculate portfolio
    print("Calculating portfolio value...")
    summary = calculate_portfolio(portfolio, prices, weekly_changes)
    
    # Print summary
    print("="*60)
    print(f"Total Value:    €{summary['total_value']:,.2f}")
    print(f"Profit/Loss:    €{summary['total_profit_loss']:+,.2f} ({summary['total_return_pct']:+.2f}%)")
    print("="*60)
    
    # Create and send email
    subject = f"Portfolio: €{summary['total_profit_loss']:+,.2f} ({summary['total_return_pct']:+.1f}%)"
    html = create_html_email(summary)
    
    if email_config['from'] and email_config['password']:
        send_email(subject, html, email_config)
    else:
        print("\nEmail config missing - skipping send")

if __name__ == "__main__":
    main()