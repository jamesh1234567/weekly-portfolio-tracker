"""
Weekly Portfolio Tracker - Simple Version
Gets stock prices, calculates portfolio value, sends email.
"""

import os
import json
import yfinance as yf
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

def load_portfolio():
    """Load portfolio from environment or file"""
    portfolio_json = os.environ.get('PORTFOLIO_DATA')
    if portfolio_json:
        return json.loads(portfolio_json)
    
    if os.path.exists('portfolio.json'):
        with open('portfolio.json', 'r') as f:
            return json.load(f)
    
    return {}

def get_exchange_rate(currency):
    """Get exchange rate to EUR"""
    if currency == 'EUR':
        return 1.0
    
    try:
        ticker = f"{currency}EUR=X"
 '''       data = yf.download(ticker, period='1d', progress=False)
        return float(data['Close'].iloc[-1])
    except:
        return 1.0'''
        data = yf.download(ticker, period='5d', progress=False)['Close'].dropna()
        return float(data.iloc[-1].squeeze())
    except:
        raise

def calculate_portfolio(portfolio):
    """Calculate total value and profit/loss"""
    holdings = []
    total_value = 0
    total_cost = 0
    
    for ticker, data in portfolio.items():
        try:
            # Get price data for last 7 days
            stock = yf.Ticker(ticker)
          #  hist = stock.history(period='7d')
            hist = stock.history(period='7d').dropna(subset=['Close'])
            if hist.empty:
                raise ValueError("no price data")
            current_price = float(hist['Close'].iloc[-1])
            
            # Calculate weekly change
            if len(hist) >= 2:
                week_ago = hist['Close'].iloc[0]
                week_change = ((current_price - week_ago) / week_ago) * 100
            else:
                week_change = 0.0
            
            # Convert to EUR
            currency = data.get('currency', 'EUR')
            rate = get_exchange_rate(currency)
            
            # Calculate values
            shares = data['shares']
            buy_price_eur = data['buy_price'] * rate
            current_price_eur = current_price * rate
            value_eur = shares * current_price_eur
            cost_eur = shares * buy_price_eur
            profit_eur = value_eur - cost_eur
            profit_pct = (profit_eur / cost_eur) * 100
            
            holdings.append({
                'ticker': ticker,
                'shares': shares,
                'price_eur': current_price_eur,
                'value_eur': value_eur,
                'profit_eur': profit_eur,
                'profit_pct': profit_pct,
                'week_change': week_change
            })
            
            total_value += value_eur
            total_cost += cost_eur
            
            print(f"{ticker}: €{current_price_eur:.2f} ({week_change:+.1f}% this week)")
            
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            continue
    
    total_profit = total_value - total_cost
    #total_return = (total_profit / total_cost) * 100
    total_return = (total_profit / total_cost) * 100 if total_cost else 0.0
    
    return holdings, total_value, total_profit, total_return

def create_email(holdings, total_value, total_profit, total_return):
    """Create simple HTML email"""
    
    # Build table rows
    rows = ""
    for h in holdings:
        color = "#90EE90" if h['profit_eur'] >= 0 else "#FFB6C1"
        week_color = "green" if h['week_change'] >= 0 else "red"
        rows += f"""
        <tr style="background-color: {color};">
            <td>{h['ticker']}</td>
            <td>{h['shares']}</td>
            <td>€{h['price_eur']:.2f}</td>
            <td>€{h['value_eur']:.2f}</td>
            <td>€{h['profit_eur']:+.2f} ({h['profit_pct']:+.1f}%)</td>
            <td style="color: {week_color};">{h['week_change']:+.1f}%</td>
        </tr>
        """
    
    html = f"""
    <html>
    <body style="font-family: Arial;">
        <h2>Portfolio Update - {datetime.now().strftime('%B %d, %Y')}</h2>
        
        <p><strong>Total Value:</strong> €{total_value:,.2f}</p>
        <p><strong>Profit/Loss:</strong> €{total_profit:+,.2f} ({total_return:+.1f}%)</p>
        
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #ddd;">
                <th>Ticker</th>
                <th>Shares</th>
                <th>Price</th>
                <th>Value</th>
                <th>Profit/Loss</th>
                <th>7-Day Change</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """
    
    return html

def send_email(subject, html):
    """Send email via Gmail"""
    email_from = os.environ.get('EMAIL_FROM')
    email_to = os.environ.get('EMAIL_TO')
    password = os.environ.get('EMAIL_PASSWORD')
    
    msg = MIMEText(html, 'html')
    msg['Subject'] = subject
    msg['From'] = email_from
    msg['To'] = email_to
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_from, password)
        smtp.send_message(msg)
    
    print("Email sent!")

def main():
    print("Portfolio Tracker")
    print("=" * 40)
    
    # Load portfolio
    portfolio = load_portfolio()
    print(f"Loaded {len(portfolio)} holdings\n")
    
    # Calculate values
    holdings, total_value, total_profit, total_return = calculate_portfolio(portfolio)
    
    # Print summary
    print("\n" + "=" * 40)
    print(f"Total Value: €{total_value:,.2f}")
    print(f"Profit/Loss: €{total_profit:+,.2f} ({total_return:+.1f}%)")
    print("=" * 40)
    
    # Send email
    subject = f"Portfolio: €{total_profit:+.0f} ({total_return:+.1f}%)"
    html = create_email(holdings, total_value, total_profit, total_return)
    send_email(subject, html)

if __name__ == "__main__":
    main()
