from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from binance.client import Client
import main  # Import the main module with trading logic

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TradeParams(BaseModel):
    currency: str
    amount: float
    top: float
    bottom: float

@app.get("/balance")
async def get_balance():
    client = Client(main.api_key, main.api_secret, testnet=True)
    balances = main.get_account_balance(client)
    return {"balance": balances.get('USDT', 0)}

@app.post("/trade")
async def start_trade(params: TradeParams):
    client = Client(main.api_key, main.api_secret, testnet=True)
    symbol = main.get_symbol(params.currency)
    try:
        main.flexible_range_buy_strategy(client, symbol, params.amount, params.top, params.bottom)
        return {"message": "Trade executed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
