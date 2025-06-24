
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import yfinance as yf
from flask import Flask, render_template, jsonify

app = Flask(__name__)

def get_ibov_spot():
    ibov = yf.Ticker("^BVSP")
    data = ibov.history(period="1d")
    if data.empty:
        raise ValueError("Não foi possível obter dados do IBOV")
    return data.iloc[-1]["Close"]

def get_win_futuro_simulado(spot):
    # Como fallback, simulamos um prêmio de 250 pontos sobre o spot
    return spot + 250

def get_taxa_juros():
    return 0.1325  # CDI anual estimado

def get_taxa_aluguel():
    return 0.015  # Estimativa do aluguel

def calcular_preco_futuro_justo(spot, juros, aluguel, dias):
    t = dias / 252
    return spot * np.exp((juros - aluguel) * t)

def identificar_mispricing(futuro_obs, futuro_justo):
    diff = futuro_obs - futuro_justo
    if diff > 100:
        return 'Venda Futuro / Compra Spot', diff
    elif diff < -100:
        return 'Compra Futuro / Venda Spot', diff
    else:
        return 'Sem Arbitragem', diff

@app.route("/")
def index():
    try:
        spot = get_ibov_spot()
        futuro = get_win_futuro_simulado(spot)
        juros = get_taxa_juros()
        aluguel = get_taxa_aluguel()
        dias = 15

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

@app.route("/api/mispricing")
def api_mispricing():
    try:
        spot = get_ibov_spot()
        futuro = get_win_futuro_simulado(spot)
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
    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
