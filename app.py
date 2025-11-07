
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import math
import os

app = FastAPI(title="Grana Segura Surebet", version="1.0.0")

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")


class SurebetRequest(BaseModel):
    odds: List[float]
    stake: float


def calculate_surebet(odds: List[float], stake: float):
    # Filtra odds válidas (>0)
    odds = [o for o in odds if o and o > 1]
    if len(odds) < 2:
        raise ValueError("Precisamos de pelo menos 2 odds para calcular a surebet.")

    inv_sum = sum(1.0 / o for o in odds)
    arb_percent = inv_sum * 100  # soma das probabilidades implícitas

    result = {
        "odds": odds,
        "stake": stake,
        "is_surebet": inv_sum < 1.0,
        "arb_factor": inv_sum,
        "arb_percent": round(arb_percent, 4),
    }

    # Distribuição por stake fixa
    bets = [(stake * (1.0 / o)) / inv_sum for o in odds]
    bets_rounded = [round(b, 2) for b in bets]

    # Lucro em cada cenário
    payouts = [round(bets[i] * odds[i], 2) for i in range(len(odds))]
    min_payout = min(payouts)
    lucro_liquido = round(min_payout - stake, 2)

    if stake > 0:
        lucro_percentual = round((lucro_liquido / stake) * 100, 2)
    else:
        lucro_percentual = 0.0

    result.update(
        {
            "bets": bets_rounded,
            "payouts": payouts,
            "min_payout": min_payout,
            "lucro_liquido": lucro_liquido,
            "lucro_percentual": lucro_percentual,
        }
    )
    return result


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse(content="<h1>Grana Segura Surebet</h1>", status_code=200)


@app.get("/status")
async def status():
    return {"status": "online", "nome": "Grana Segura Surebet", "versao": "1.0.0"}


@app.post("/grana-segura")
async def grana_segura(req: SurebetRequest):
    try:
        data = calculate_surebet(req.odds, req.stake)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Para rodar localmente: uvicorn app:app --reload --host 0.0.0.0 --port 8000
