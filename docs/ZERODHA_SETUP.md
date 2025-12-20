# Zerodha Setup Guide

**Date**: December 19, 2025  
**Purpose**: Guide for setting up Zerodha Kite Connect API for live trading

---

## 📋 Prerequisites

- **Zerodha Demat Account** - Active trading account
- **2FA Enabled** - TOTP (Time-based One-Time Password) is mandatory
- **Python 3.11+** - With QuantX installed

---

## 🔑 Step 1: Get API Credentials

### 1.1 Create Kite Connect App

1. Go to [https://kite.trade/](https://kite.trade/)
2. Login with your Zerodha credentials
3. Navigate to **"My Apps"**
4. Click **"Create new app"**

### 1.2 Fill App Details

- **App name**: Your app name (e.g., "QuantX Trading")
- **Type**: Select "Connect"
- **Redirect URL**: Can be your local URL or any HTTPS URL
  - Example: `https://127.0.0.1:5000/callback`
  - Or: `https://your website.com/callback`

### 1.3 Get Credentials

After creating the app, you'll receive:
- **API Key** - Public identifier (keep this)
- **API Secret** - Secret key (keep this secure!)

> ⚠️ **Never share your API Secret** with anyone or commit it to version control!

---

## 🔐 Step 2: Enable 2FA (TOTP)

Zerodha requires TOTP for API access:

1. Login to [kite.zerodha.com](https://kite.zerodha.com)
2. Go to **Settings** → **Security**
3. Enable **TOTP** (use apps like Google Authenticator, Authy)
4. Save your TOTP secret key (optional, for automation)

---

## 🚀 Step 3: Install Dependencies

```bash
cd /Users/adii/Builds/Algo-Trading/QuantX

# Install kiteconnect package
pip install kiteconnect

# Or if using poetry
poetry add kiteconnect
```

---

## 🔧 Step 4: Authentication Flow

### 4.1 Interactive Authentication (Recommended for First Time)

```bash
# Run the authentication example
PYTHONPATH="$(pwd)/src" python examples/live/zerodha_authentication.py
```

Choose option **4** for complete interactive flow.

### 4.2 Manual Authentication

#### Step 1: Get Login URL

```python
from quantx.execution.brokers import ZerodhaBroker

config = {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret"
}

broker = ZerodhaBroker("zerodha", config)
login_url = broker.get_login_url()
print(login_url)
```

#### Step 2: Login via Browser

1. Open the login URL in browser
2. Enter Zerodha credentials
3. Complete 2FA (TOTP)
4. You'll be redirected to your redirect URL

#### Step 3: Extract Request Token

From redirect URL:
```
https://your-redirect-url.com/?request_token=ABC123XYZ&action=login&status=success
```

Copy the `request_token` value.

#### Step 4: Generate Session

```python
session_data = broker.generate_session(request_token)
access_token = session_data["access_token"]

# Save this token!
print(f"Access Token: {access_token}")
```

### 4.3 Connect with Saved Token

```python
config = {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "access_token": "your_saved_access_token"
}

broker = ZerodhaBroker("zerodha", config)
broker.connect()  # ✅ Connected!
```

---

## 💾 Step 5: Save Session

The access token is valid for **24 hours**. Save it for reuse:

```python
import json

session_data = {
    "api_key": config["api_key"],
    "api_secret": config["api_secret"],
    "access_token": access_token,
    "user_id": session_data["user_id"]
}

# Save to file
with open("zerodha_session.json", "w") as f:
    json.dump(session_data, f)
```

> ⚠️ **Security**: Keep session file secure! Add to `.gitignore`

---

## 📊 Step 6: Test Connection

```bash
# Run trading example
PYTHONPATH="$(pwd)/src" python examples/live/zerodha_trading.py
```

Choose option **1** to fetch market quotes.

If successful, you're ready to trade! 🎉

---

## 🔄 Daily Workflow

Since access tokens expire after 24 hours:

### Option 1: Manual Renewal (Recommended for Security)
1. Run authentication example daily
2. Complete OAuth flow
3. Get new access token

### Option 2: Automated Renewal (Advanced)
- Store TOTP secret securely
- Use automation to generate new tokens
- **Not recommended** for security reasons

---

## 🎯 Usage Examples

### Get Market Quotes

```python
broker = ZerodhaBroker("zerodha", config)
broker.connect()

quote = broker.get_quote("NSE:INFY")
print(f"Last Price: ₹{quote['last']}")

broker.disconnect()
```

### Place Market Order

```python
from quantx.execution.brokers import Order, OrderType, OrderSide

order = Order(
    order_id="",
    symbol="NSE:INFY",
    side=OrderSide.BUY,
    order_type=OrderType.MARKET,
    quantity=1
)

order_id = broker.place_order(order)
print(f"Order placed: {order_id}")
```

### View Positions

```python
positions = broker.get_positions()

for pos in positions:
    print(f"{pos.symbol}: {pos.quantity} @ ₹{pos.average_price}")
    print(f"P&L: ₹{pos.unrealized_pnl:+.2f}")
```

### Get Account Info

```python
account = broker.get_account()

print(f"Cash: ₹{account.cash:,.2f}")
print(f"Equity: ₹{account.equity:,.2f}")
print(f"P&L: ₹{account.unrealized_pnl:+,.2f}")
```

---

## 🛡️ Security Best Practices

### 1. Protect API Credentials

```bash
# Add to .gitignore
echo "zerodha_session.json" >> .gitignore
echo ".env" >> .gitignore
```

### 2. Use Environment Variables

```bash
# .env file
ZERODHA_API_KEY=your_api_key
ZERODHA_API_SECRET=your_api_secret
ZERODHA_ACCESS_TOKEN=your_access_token
```

```python
from dotenv import load_dotenv
import os

load_dotenv()

config = {
    "api_key": os.getenv("ZERODHA_API_KEY"),
    "api_secret": os.getenv("ZERODHA_API_SECRET"),
    "access_token": os.getenv("ZERODHA_ACCESS_TOKEN")
}
```

### 3. Rate Limiting

Zerodha has rate limits:
- **3 requests/second** for login API
- **10 requests/second** for order API
- No limit on market data

The `ZerodhaBroker` class handles this automatically.

### 4. Error Handling

Always wrap broker calls in try-except:

```python
try:
    broker.connect()
    # ... trading operations ...
except ConnectionError:
    print("Failed to connect")
except Exception as e:
    print(f"Error: {e}")
finally:
    broker.disconnect()
```

---

## 📝 Symbol Format

Zerodha uses `EXCHANGE:SYMBOL` format:

### Equity (Cash)
- NSE: `NSE:INFY`, `NSE:TCS`, `NSE:RELIANCE`
- BSE: `BSE:INFY`, `BSE:TCS`

### Futures & Options
- NFO: `NFO:NIFTY24DECFUT`, `NFO:BANKNIFTY24DEC50000CE`

### Currency
- CDS: `CDS:USDINR24DECFUT`

### Commodities
- MCX: `MCX:GOLD24DECFUT`

---

## ⚠️ Important Notes

### Trading Hours
- **NSE Equity**: 9:15 AM - 3:30 PM IST
- **Pre-market**: 9:00 AM - 9:15 AM IST
- **After-market**: 3:40 PM - 4:00 PM IST

### Margins
- **MIS (Intraday)**: Higher leverage, must square-off by 3:20 PM
- **CNC (Delivery)**: Full payment required, can hold overnight
- **NRML (F&O)**: For futures and options

### Order Types
- **MARKET**: Executes at best available price
- **LIMIT**: Executes at specified price or better
- **SL (Stop-Loss)**: Triggers at stop price, becomes market order
- **SL-M (Stop-Loss Market)**: Stop-loss with limit price

---

## 🐛 Troubleshooting

### Issue 1: "Invalid API Key"
- **Solution**: Check API key is correct, no extra spaces

### Issue 2: "Token is invalid or has expired"
- **Solution**: Generate new access token (valid for 24 hours only)

### Issue 3: "Insufficient funds"
- **Solution**: Ensure sufficient margin/cash in account

### Issue 4: "Trigger price not within range"
- **Solution**: For stop orders, trigger price must be within daily limits

### Issue 5: "Cannot trade outside  market hours"
- **Solution**: Wait for market hours (9:15 AM - 3:30 PM IST)

---

## 📚 Additional Resources

### Official Documentation
- [Kite Connect API Docs](https://kite.trade/docs/connect/v3/)
- [Python Client Docs](https://kite.trade/docs/pykiteconnect/v4/)

### QuantX Examples
- `examples/live/zerodha_authentication.py` - Authentication flow
- `examples/live/zerodha_trading.py` - Trading operations

### Support
- Zerodha Support: [https://support.zerodha.com/](https://support.zerodha.com/)
- Kite Connect Forum: [https://tradingqna.com/tag/kiteconnect](https://tradingqna.com/tag/kiteconnect)

---

## ✅ Checklist

Before live trading:

- [ ] Zerodha account active with funds
- [ ] 2FA (TOTP) enabled
- [ ] API app created on kite.trade
- [ ] API credentials saved securely
- [ ] kiteconnect package installed
- [ ] Authentication successful
- [ ] Test with small orders first
- [ ] Understand margin requirements
- [ ] Know trading hours

---

**Status**: Ready for Indian Market Trading (NSE/BSE) 🇮🇳  
**Last Updated**: December 19, 2025  
**Zerodha Broker**: Fully Integrated ✅
