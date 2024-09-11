import argparse
import time
import os
from binance.client import Client
from binance.exceptions import BinanceAPIException

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def get_symbol(base_currency):
    return f"{base_currency.upper()}USDT"

def flexible_range_buy_strategy(client, symbol, amount, top, bottom):
    print(f"\nWatching {symbol} with boundaries: Top ${top:.2f}, Bottom ${bottom:.2f}")
    print("=" * 50)
    
    last_price = None
    
    while True:
        try:
            # Get the latest price
            ticker = client.get_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            
            # Calculate quantity based on amount
            quantity = amount / current_price
            
            # Determine color based on price movement
            if last_price is not None:
                if current_price > last_price:
                    color = GREEN
                elif current_price < last_price:
                    color = RED
                else:
                    color = RESET
            else:
                color = RESET
            
            # Print current status
            print(f"Top: ${top:.2f} | Current: {color}${current_price:.2f}{RESET} | Bottom: ${bottom:.2f}", end='\r')
            
            last_price = current_price
            
            if current_price <= bottom or current_price >= top:
                # Place a real market buy order on testnet
                order = client.create_order(
                    symbol=symbol,
                    side=Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_MARKET,
                    quoteOrderQty=amount  # Use quoteOrderQty for amount-based orders
                )
                
                # Debug print with detailed information
                print("\n" + "="*50)
                print("TRADE EXECUTED ON TESTNET")
                print("="*50)
                print(f"Symbol: {order['symbol']}")
                print(f"Type: {order['type']}")
                print(f"Side: {order['side']}")
                print(f"Quantity: {order['executedQty']}")
                print(f"Price: ${float(order['cummulativeQuoteQty']) / float(order['executedQty']):.2f}")
                print(f"Total cost: ${order['cummulativeQuoteQty']}")
                print(f"Reason: {'Bottom boundary reached' if current_price <= bottom else 'Top boundary reached'}")
                print(f"Boundary hit: {'Bottom' if current_price <= bottom else 'Top'}")
                print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(order['transactTime']/1000))}")
                print(f"Order ID: {order['orderId']}")
                print("="*50 + "\n")
                
                break

            time.sleep(1)  # Wait for 1 second before next price check

        except BinanceAPIException as e:
            print(f"\nAn error occurred: {e}")
            break

def get_account_balance(client):
    account = client.get_account()
    balances = account['balances']
    return {asset['asset']: float(asset['free']) for asset in balances if asset['asset'] == 'USDT'}

def display_balance(client):
    balances = get_account_balance(client)
    print("\nAccount Balance (USDT):")
    print("=======================")
    if 'USDT' in balances:
        print(f"USDT: {balances['USDT']:.2f}")
    else:
        print("No USDT balance found.")
    print("=======================\n")

def main():
    parser = argparse.ArgumentParser(description="Binance Testnet Tool")
    parser.add_argument("--show-balance", action="store_true", help="Display account balance")
    parser.add_argument("--currency", type=str, help="Base currency (e.g., BTC, ETH)")
    parser.add_argument("--amount", type=float, help="Amount in USDT to buy")
    parser.add_argument("--top", type=float, help="Upper price boundary")
    parser.add_argument("--bottom", type=float, help="Lower price boundary")

    args = parser.parse_args()

    # Read API keys from environment variables
    api_key = os.environ.get('BINANCE_TESTNET_API_KEY')
    api_secret = os.environ.get('BINANCE_TESTNET_SECRET_KEY')

    if not api_key or not api_secret:
        print("Error: BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_SECRET_KEY must be set in the environment.")
        return

    # Initialize Binance client
    client = Client(api_key, api_secret, testnet=True)

    if args.show_balance:
        display_balance(client)
    elif all([args.currency, args.amount, args.top, args.bottom]):
        symbol = get_symbol(args.currency)
        print(f"Strategy parameters:")
        print(f"Trading Pair: {symbol}")
        print(f"Amount to spend: ${args.amount}")
        print(f"Top boundary: ${args.top}")
        print(f"Bottom boundary: ${args.bottom}")
        print("Starting simulation...")
        flexible_range_buy_strategy(client, symbol, args.amount, args.top, args.bottom)
    else:
        parser.print_help()
        print("\nError: For trading strategy, all of --currency, --amount, --top, and --bottom must be provided.")

if __name__ == "__main__":
    main()
