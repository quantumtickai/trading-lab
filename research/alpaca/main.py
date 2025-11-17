from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Alpaca credentials
APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID", "")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY", "")
APCA_BASE_URL = os.getenv("APCA_BASE_URL", "https://paper-api.alpaca.markets")


@app.get("/")
def root():
    """Basic status endpoint"""
    return {
        "status": "running",
        "message": "Alpaca Bridge API is active",
        "endpoints": ["/", "/check-env", "/tv-webhook"]
    }


@app.get("/check-env")
def check_env():
    """Verify environment variables are set"""
    return {
        "apca_api_key_id_set": bool(APCA_API_KEY_ID),
        "apca_api_secret_key_set": bool(APCA_API_SECRET_KEY),
        "apca_base_url": APCA_BASE_URL
    }


def place_order(symbol: str, qty: int, side: str) -> dict:
    """
    Place a market order with Alpaca.
    
    Args:
        symbol: Stock ticker (e.g., "SPY")
        qty: Number of shares
        side: "buy" or "sell"
    
    Returns:
        Alpaca API response as dict
    
    Raises:
        Exception with details if order fails
    """
    url = f"{APCA_BASE_URL}/v2/orders"
    
    headers = {
        "APCA-API-KEY-ID": APCA_API_KEY_ID,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY,
        "Content-Type": "application/json"
    }
    
    # Determine if this is a crypto symbol
    is_crypto = symbol.endswith("USD") and len(symbol) > 3
    
    payload = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": "market",
        "time_in_force": "gtc" if is_crypto else "day"
    }
    
    print(f"\n{'='*60}")
    print(f"PLACING ORDER: {side.upper()} {qty} shares of {symbol}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"{'='*60}\n")
    
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Alpaca Response Status: {response.status_code}")
    print(f"Alpaca Response Body: {response.text}\n")
    
    if response.status_code not in [200, 201]:
        error_detail = response.text
        raise Exception(
            f"Alpaca order failed (status {response.status_code}): {error_detail}"
        )
    
    return response.json()


@app.post("/tv-webhook")
async def tv_webhook(request: Request):
    """
    Webhook endpoint for TradingView alerts.
    Expects JSON: {"action": "buy"|"sell", "symbol": "TICKER", "qty": NUMBER}
    """
    
    # Read raw body
    raw_body = await request.body()
    raw_text = raw_body.decode("utf-8")
    
    print("\n" + "="*60)
    print("INCOMING WEBHOOK")
    print("="*60)
    print(f"Raw body: {raw_text}")
    print("="*60 + "\n")
    
    # Ignore empty bodies
    if not raw_text.strip():
        print("Ignoring: Empty body\n")
        return JSONResponse({
            "status": "ignored",
            "reason": "empty body"
        })
    
    # Ignore non-JSON text (e.g., TradingView status strings)
    if not raw_text.strip().startswith("{"):
        print(f"Ignoring: Non-JSON text: {raw_text}\n")
        return JSONResponse({
            "status": "ignored",
            "reason": "non-json text",
            "received": raw_text
        })
    
    # Parse JSON
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}\n")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "reason": "invalid json",
                "details": str(e)
            }
        )
    
    print(f"Parsed payload: {json.dumps(payload, indent=2)}\n")
    
    # Extract fields
    action = payload.get("action", "").lower()
    symbol = payload.get("symbol", "").upper()
    qty = payload.get("qty", 0)
    
    # Validate action
    if action not in ["buy", "sell"]:
        print(f"Invalid action: {action}\n")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "reason": "invalid action",
                "received_action": action
            }
        )
    
    # Check for placeholder symbol
    if symbol == "{{TICKER}}" or not symbol:
        print(f"Ignoring: Placeholder or empty symbol: {symbol}\n")
        return JSONResponse({
            "status": "ignored",
            "reason": "placeholder or empty symbol",
            "symbol": symbol
        })
    
    # Validate quantity
    try:
        qty = int(qty)
        if qty <= 0:
            raise ValueError("Quantity must be positive")
    except (ValueError, TypeError) as e:
        print(f"Invalid quantity: {qty} - {e}\n")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "reason": "invalid quantity",
                "received_qty": qty
            }
        )
    
    # Check if crypto symbol
    is_crypto = symbol.endswith("USD") and len(symbol) > 3
    
    if is_crypto:
        print(f"CRYPTO DETECTED: {symbol}")
        print("Note: Crypto trading requires account approval and uses time_in_force='gtc'")
        print("For testing, we'll log the signal only.\n")
        
        return JSONResponse({
            "status": "crypto_signal_logged",
            "action": action,
            "symbol": symbol,
            "qty": qty,
            "note": "Crypto orders require account approval. Signal logged but not executed."
        })
    
    # Place order for stocks/ETFs
    try:
        alpaca_response = place_order(symbol, qty, action)
        
        return JSONResponse({
            "status": "order_sent",
            "action": action,
            "symbol": symbol,
            "qty": qty,
            "alpaca_response": alpaca_response
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"ERROR placing order: {error_msg}\n")
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "reason": "alpaca_order_failed",
                "details": error_msg,
                "symbol": symbol,
                "action": action,
                "qty": qty
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)