"""
Zerodha Authentication Example.

Demonstrates how to authenticate with Zerodha Kite Connect API
and generate access tokens for trading.
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from loguru import logger

from quantx.execution.brokers import ZerodhaBroker


def setup_logging():
    """Setup logging."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>",
        level="INFO"
    )


def save_session(session_data: dict, filename: str = "zerodha_session.json"):
    """Save session data to file."""
    filepath = Path(__file__).parent / filename
    with open(filepath, "w") as f:
        json.dump(session_data, f, indent=2)
    logger.info(f"✅ Session saved to: {filepath}")


def load_session(filename: str = "zerodha_session.json") -> dict:
    """Load session data from file."""
    filepath = Path(__file__).parent / filename
    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


def example_1_get_login_url():
    """Example 1: Get OAuth login URL."""
    print("\n" + "="*70)
    print("Example 1: Get OAuth Login URL")
    print("="*70 + "\n")
    
    # Replace with your actual API credentials
    config = {
        "api_key": "your_api_key_here",  # Get from https://kite.trade/
        "api_secret": "your_api_secret_here"
    }
    
    broker = ZerodhaBroker("zerodha", config)
    
    # Get login URL
    login_url = broker.get_login_url()
    
    print("📌 OAuth Authentication Steps:")
    print("\n1. Open this URL in your browser:")
    print(f"\n   {login_url}\n")
    print("2. Login with your Zerodha credentials")
    print("3. Complete 2FA (TOTP)")
    print("4. After login, you'll be redirected to your redirect URL")
    print("5. Copy the 'request_token' from the URL parameter")
    print("\n   Example redirect URL:")
    print("   https://your-redirect-url.com/?request_token=ABC123XYZ&action=login&status=success")
    print("\n6. Use the request_token in Example 2 to generate session")
    
    return login_url


def example_2_generate_session():
    """Example 2: Generate session with request token."""
    print("\n" + "="*70)
    print("Example 2: Generate Session with Request Token")
    print("="*70 + "\n")
    
    # Replace with your actual credentials
    config = {
        "api_key": "your_api_key_here",
        "api_secret": "your_api_secret_here"
    }
    
    broker = ZerodhaBroker("zerodha", config)
    
    # Get request token from user
    print("Enter the request_token from the OAuth callback URL:")
    request_token = input("> ").strip()
    
    if not request_token:
        print("❌ No request token provided")
        return
    
    try:
        # Generate session
        session_data = broker.generate_session(request_token)
        
        print("\n✅ Session generated successfully!")
        print(f"\n📌 Session Details:")
        print(f"   User ID: {session_data.get('user_id')}")
        print(f"   User Name: {session_data.get('user_name')}")
        print(f"   Email: {session_data.get('email')}")
        print(f"   Access Token: {session_data.get('access_token', '')[:30]}...")
        
        # Save session for future use
        save_data = {
            "api_key": config["api_key"],
            "api_secret": config["api_secret"],
            "access_token": session_data["access_token"],
            "user_id": session_data["user_id"],
            "login_time": session_data.get("login_time")
        }
        
        save_session(save_data)
        
        print("\n💾 Session saved! You can now use the access token for trading.")
        print("   Note: Access token is valid for 24 hours.")
        
        return session_data
        
    except Exception as e:
        print(f"\n❌ Failed to generate session: {e}")
        logger.error(f"Session generation error: {e}")


def example_3_connect_with_token():
    """Example 3: Connect using saved access token."""
    print("\n" + "="*70)
    print("Example 3: Connect with Saved Access Token")
    print("="*70 + "\n")
    
    # Load saved session
    session = load_session()
    
    if not session or "access_token" not in session:
        print("❌ No saved session found!")
        print("   Please complete Example 1 and 2 first to generate a session.")
        return
    
    # Create broker with access token
    config = {
        "api_key": session["api_key"],
        "api_secret": session["api_secret"],
        "access_token": session["access_token"],
        "user_id": session.get("user_id")
    }
    
    broker = ZerodhaBroker("zerodha", config)
    
    # Connect
    print("🔌 Connecting to Zerodha...")
    if broker.connect():
        print("\n✅ Connected successfully!")
        
        # Get account info
        try:
            account = broker.get_account()
            print(f"\n💰 Account Information:")
            print(f"   Available Cash: ₹{account.cash:,.2f}")
            print(f"   Equity: ₹{account.equity:,.2f}")
            print(f"   Buying Power: ₹{account.buying_power:,.2f}")
            
        except Exception as e:
            print(f"❌ Failed to get account info: {e}")
        
        # Disconnect
        broker.disconnect()
        print("\n✅ Disconnected")
    else:
        print("\n❌ Connection failed!")
        print("   Your access token may have expired (valid for 24 hours).")
        print("   Please run Example 1 and 2 again to generate a new token.")


def example_4_complete_flow():
    """Example 4: Complete authentication flow (interactive)."""
    print("\n" + "="*70)
    print("Example 4: Complete Authentication Flow")
    print("="*70 + "\n")
    
    print("This will guide you through the complete OAuth flow.\n")
    
    # Get API credentials
    print("Step 1: Enter your Zerodha API credentials")
    print("(Get these from https://kite.trade/ -> My Apps)\n")
    
    api_key = input("API Key: ").strip()
    api_secret = input("API Secret: ").strip()
    
    if not api_key or not api_secret:
        print("\n❌ API credentials required!")
        return
    
    config = {
        "api_key": api_key,
        "api_secret": api_secret
    }
    
    broker = ZerodhaBroker("zerodha", config)
    
    # Step 2: Get login URL
    print("\n" + "-"*70)
    print("Step 2: OAuth Login")
    print("-"*70 + "\n")
    
    login_url = broker.get_login_url()
    print(f"Open this URL in your browser:\n\n{login_url}\n")
    print("After logging in, copy the 'request_token' from the redirect URL.")
    
    request_token = input("\nEnter request_token: ").strip()
    
    if not request_token:
        print("❌ Request token required!")
        return
    
    # Step 3: Generate session
    print("\n" + "-"*70)
    print("Step 3: Generating Session")
    print("-"*70 + "\n")
    
    try:
        session_data = broker.generate_session(request_token)
        
        print("✅ Session generated!")
        print(f"\nUser: {session_data.get('user_name')}")
        print(f"Email: {session_data.get('email')}")
        
        # Step 4: Save session
        save_data = {
            "api_key": api_key,
            "api_secret": api_secret,
            "access_token": session_data["access_token"],
            "user_id": session_data["user_id"]
        }
        
        save_session(save_data)
        
        # Step 5: Test connection
        print("\n" + "-"*70)
        print("Step 4: Testing Connection")
        print("-"*70 + "\n")
        
        if broker.connect():
            print("✅ Connected successfully!")
            
            try:
                account = broker.get_account()
                print(f"\n💰 Your Account:")
                print(f"   Cash: ₹{account.cash:,.2f}")
                print(f"   Equity: ₹{account.equity:,.2f}")
                
            except Exception as e:
                print(f"⚠️  Could not fetch account: {e}")
            
            broker.disconnect()
        
        print("\n" + "="*70)
        print("🎉 Authentication Complete!")
        print("="*70)
        print("\nYou can now use Zerodha for trading.")
        print("The access token has been saved and will be valid for 24 hours.")
        print("\nNext: Run the trading examples to start trading!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Authentication error: {e}")


def main():
    """Run authentication examples."""
    setup_logging()
    
    print("\n" + "="*70)
    print(" " * 18 + "Zerodha Authentication Examples")
    print("="*70)
    
    print("\nChoose an option:")
    print("\n1. Get OAuth Login URL")
    print("2. Generate Session with Request Token")
    print("3. Connect with Saved Token")
    print("4. Complete Authentication Flow (Interactive)")
    print("0. Exit")
    
    choice = input("\nEnter choice (0-4): ").strip()
    
    if choice == "1":
        example_1_get_login_url()
    elif choice == "2":
        example_2_generate_session()
    elif choice == "3":
        example_3_connect_with_token()
    elif choice == "4":
        example_4_complete_flow()
    elif choice == "0":
        print("\n👋 Goodbye!")
    else:
        print("\n❌ Invalid choice!")
    
    print()


if __name__ == "__main__":
    main()
