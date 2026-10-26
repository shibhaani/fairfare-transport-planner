"""FairFare: an educational transport-affordability prototype."""
import csv
import os
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder="static")


def affordability(monthly_income: float, monthly_transport_cost: float) -> dict:
    """Return the share of income spent on transport; values must be non-negative."""
    income = float(monthly_income)
    cost = float(monthly_transport_cost)
    if income <= 0:
        raise ValueError("monthly_income must be greater than zero")
    if cost < 0:
        raise ValueError("monthly_transport_cost cannot be negative")
    share = (cost / income) * 100
    if share >= 15:
        band = "high"
    elif share >= 8:
        band = "moderate"
    else:
        band = "lower"
    return {
        "monthly_income": round(income, 2),
        "monthly_transport_cost": round(cost, 2),
        "transport_share_percent": round(share, 2),
        "illustrative_band": band,
        "note": "Illustrative indicator only; bands are not official policy thresholds."
    }


def subsidy_scenario(monthly_transport_cost: float, hypothetical_support: float) -> dict:
    """Model a hypothetical support amount without making eligibility decisions."""
    cost = float(monthly_transport_cost)
    support = float(hypothetical_support)
    if cost < 0 or support < 0:
        raise ValueError("cost and support must be non-negative")
    applied = min(cost, support)
    coverage = (applied / cost * 100) if cost else 0.0
    return {
        "monthly_transport_cost": round(cost, 2),
        "hypothetical_support": round(support, 2),
        "estimated_remaining_cost": round(max(0.0, cost - support), 2),
        "cost_covered_percent": round(coverage, 2),
        "note": "Hypothetical scenario only; not an official benefit or eligibility decision."
    }


@app.get("/")
def index():
    return send_from_directory(ROOT / "static", "index.html")


@app.get("/api/sample-data")
def sample_data():
    rows = []
    with (ROOT / "data" / "sample_commuters.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return jsonify({"data_type": "synthetic illustrative data", "records": rows})


@app.post("/api/affordability")
def calculate_affordability():
    body = request.get_json(silent=True) or {}
    try:
        result = affordability(body["monthly_income"], body["monthly_transport_cost"])
        return jsonify(result)
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify({"error": str(exc) or "Invalid input"}), 400


@app.post("/api/scenario")
def calculate_scenario():
    body = request.get_json(silent=True) or {}
    try:
        result = subsidy_scenario(body["monthly_transport_cost"], body["hypothetical_support"])
        return jsonify(result)
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify({"error": str(exc) or "Invalid input"}), 400


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)
