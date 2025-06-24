
# app.py

import pandas as pd
import numpy as np
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import yfinance as yf
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# =====================
# Funções Auxiliares
# =====================

def get_ibov_spot():
    ibov = yf.Ticker("^BVSP")
    return ibov.history(period="1d").iloc[-1]['Close']

def get_win_futuro():
    win = yf.Ticker("WIN=F")  # Se não funcionar, substituir por outra fonte
    return win.history(period="1d").iloc[-1]['Close']

def get_taxa_juros():
    # Taxa de DI aproximada via CDI anual – pode ser substituída por API
    return 0.1325  # 13,25% a.a.

def get_taxa_aluguel():
    return 0.015  # 1,5% a.a. estimado para carteira Ibovespa

def calcular_preco_futuro_justo(spot, juros, aluguel, dias):
    r = juros
    k = aluguel
    t = dias / 252
    return spot * np.exp((r - k) * t)

def identificar_mispricing(futuro_obs, futuro_justo):
    diff = futuro_obs - futuro_justo
    if diff > 100:  # Arbitragem por financiamento
        return 'Venda Futuro / Compra Spot', diff
    elif diff < -100:  # Arbitragem por reversão
        return 'Compra Futuro / Venda Spot', diff
    else:
        return 'Sem Arbitragem', diff

# =====================
# Rota Principal
# =====================

@app.route("/")
def index():
    try:
        spot = get_ibov_spot()
        futuro = get_win_futuro()
        juros = get_taxa_juros()
        aluguel = get_taxa_aluguel()
        dias = 15  # aproximado até vencimento

        futuro_justo = calcular_preco_futuro_justo(spot, juros, aluguel, dias)
        sinal, mispricing = identificar_mispricing(futuro, futuro_justo)

        dados = {
            "spot": round(spot, 2),
            "futuro": round(futuro, 2),
            "futuro_justo": round(futuro_justo, 2),
            "sinal": sinal,
            "mispricing": round(mispricing, 2)
        }

        return render_template("index.html", dados=dados)

    except Exception as e:
        return f"Erro: {e}"

# =====================
# API para dados JSON
# =====================

@app.route("/api/mispricing")
def api_mispricing():
    spot = get_ibov_spot()
    futuro = get_win_futuro()
    juros = get_taxa_juros()
    aluguel = get_taxa_aluguel()
    dias = 15
    futuro_justo = calcular_preco_futuro_justo(spot, juros, aluguel, dias)
    sinal, mispricing = identificar_mispricing(futuro, futuro_justo)
    return jsonify({
        "spot": round(spot, 2),
        "futuro": round(futuro, 2),
        "futuro_justo": round(futuro_justo, 2),
        "sinal": sinal,
        "mispricing": round(mispricing, 2)
    })

# =====================
# Run
# =====================

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
