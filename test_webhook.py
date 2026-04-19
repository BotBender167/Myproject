#!/usr/bin/env python3
"""
Sentinel Logistics — Webhook Simulator
=======================================
Simulates real-time Zomato order arrivals for demo/presentation purposes.

Usage:
  python test_webhook.py           # Fire 1 order (default)
  python test_webhook.py --burst 5 # Fire 5 orders with 2s gaps
  python test_webhook.py --loop    # Fire continuously until Ctrl+C

Presentation Script:
  1. Open the Sentinel Dashboard at http://localhost:5173
  2. Navigate to "Overview" — watch the Terminal and map
  3. Run: python test_webhook.py
  4. Point out:
       - Terminal immediately logs "[SYSTEM] Fetching data..." (Phase 1 processing)
       - 1.5–3.0s pause — "The system is fetching live Weather + Traffic data"
       - Terminal logs [WEATHER] / [TRAFFIC] / Risk Assessment lines (Phase 2 enrichment)
       - Map pin drops (map.flyTo triggers) + stat counters increment
"""

import json
import sys
import time
import uuid
import random
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── Config ────────────────────────────────────────────────────────────────────

WEBHOOK_URL = "http://localhost:8000/api/webhook/zomato"

# Realistic Patiala geo-bounds (Punjab, India)
LAT_MIN, LAT_MAX = 30.3100, 30.3800
LNG_MIN, LNG_MAX = 76.3500, 76.4300

ADDRESSES = [
    "Model Town, Patiala",
    "Urban Estate Phase 1, Patiala",
    "Rajbaha Road, Near Civil Lines",
    "22 No. Phatak, Old City",
    "Leela Bhawan Market, Patiala",
    "Punjabi University Campus, Patiala",
    "Bhupindra Road, Patiala",
    "Sanauri Adda, Bypass Road",
    "Tripuri Town, Near Bus Stand",
    "Sector 12, Urban Estate, Patiala",
]

# ── ANSI Colors ───────────────────────────────────────────────────────────────

R  = "\033[91m"   # Red
Y  = "\033[93m"   # Yellow / Amber
G  = "\033[92m"   # Green
C  = "\033[96m"   # Cyan
DIM = "\033[2m"   # Dim
B  = "\033[1m"    # Bold
RST = "\033[0m"   # Reset


def banner():
    print(f"""
{Y}{B}+======================================================+
|        SENTINEL LOGISTICS -- WEBHOOK SIMULATOR       |
|          Smart Lag Demo  *  v2.1  *  Patiala         |
+======================================================+{RST}
{DIM}  Backend  : {WEBHOOK_URL}
  Dashboard : http://localhost:5173
{RST}""")


# ── Core ──────────────────────────────────────────────────────────────────────

def build_payload() -> dict:
    return {
        "order_id": f"ZOM-{uuid.uuid4().hex[:6].upper()}",
        "delivery_address": random.choice(ADDRESSES),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "lat": round(random.uniform(LAT_MIN, LAT_MAX), 5),
        "lng": round(random.uniform(LNG_MIN, LNG_MAX), 5),
    }


def fire(payload: dict, idx: int = 1, total: int = 1) -> bool:
    """
    POST a single order to the webhook. Returns True on success.
    """
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        WEBHOOK_URL, data=data,
        headers={"Content-Type": "application/json",
                 "User-Agent": "Sentinel-Webhook-Simulator/2.1"},
        method="POST",
    )

    prefix = f"[{idx}/{total}]" if total > 1 else "[ORDER]"
    print(f"{Y}{'-' * 56}{RST}")
    print(f"{B}{prefix} Dispatching {C}{payload['order_id']}{RST}")
    print(f"  {DIM}Coords  : {payload['lat']}, {payload['lng']}{RST}")
    print(f"  {DIM}Address : {payload['delivery_address']}{RST}")
    print(f"  {DIM}Time    : {payload['timestamp']}{RST}")
    print()
    print(f"  {DIM}>> Waiting for Smart Lag pipeline (1.5-3.0s)...{RST}")

    try:
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=30) as resp:
            elapsed = time.time() - t0
            body    = json.loads(resp.read().decode("utf-8"))

            label = body.get("ml_risk", {}).get("label", "?")
            score = body.get("ml_risk", {}).get("score", 0)
            lag   = body.get("lag_seconds", elapsed)
            rec   = body.get("ml_risk", {}).get("recommendation", "")

            risk_color = R if label == "High" else Y if label == "Medium" else G

            print(f"\n  {G}[OK] Pipeline complete in {elapsed:.2f}s  (simulated lag: {lag}s){RST}")
            print(f"  {B}Risk Label  :{RST} {risk_color}{B}{label}{RST}")
            print(f"  {B}Risk Score  :{RST} {risk_color}{score * 100:.1f}%{RST}")
            print(f"  {B}Reason      :{RST} {DIM}{body.get('ml_risk', {}).get('reason', '')}{RST}")
            print(f"  {B}Rec         :{RST} {DIM}{rec}{RST}")
            print(f"  {B}Stop ID     :{RST} #{body.get('stop_id')}")
            env = body.get("enriched_environment", {})
            print(f"  {B}Weather     :{RST} {env.get('weather_condition')}  "
                  f"{B}Traffic:{RST} {env.get('traffic_density', 0):.2f}  "
                  f"{B}Light:{RST} {env.get('ambient_light')}")
            return True

    except urllib.error.HTTPError as e:
        print(f"\n  {R}[FAIL] HTTP {e.code}: {e.reason}{RST}")
        try:
            print(f"  {DIM}{e.read().decode('utf-8')[:200]}{RST}")
        except Exception:
            pass
        return False

    except urllib.error.URLError as e:
        print(f"\n  {R}[FAIL] Connection failed -- is uvicorn running on port 8000?{RST}")
        print(f"  {DIM}{e.reason}{RST}")
        return False

    except Exception as e:
        print(f"\n  {R}[FAIL] Unexpected error: {e}{RST}")
        return False


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Sentinel Logistics Webhook Simulator — Smart Lag Demo"
    )
    parser.add_argument(
        "--burst", type=int, default=1, metavar="N",
        help="Fire N orders in sequence (default: 1)"
    )
    parser.add_argument(
        "--gap", type=float, default=2.0, metavar="SECONDS",
        help="Gap between burst orders in seconds (default: 2.0)"
    )
    parser.add_argument(
        "--loop", action="store_true",
        help="Keep firing orders every --gap seconds until Ctrl+C"
    )
    args = parser.parse_args()

    banner()

    successes = 0
    failures  = 0

    if args.loop:
        print(f"{Y}  LOOP MODE -- Ctrl+C to stop{RST}\n")
        count = 0
        try:
            while True:
                count += 1
                p = build_payload()
                ok = fire(p, count, "inf")
                if ok:
                    successes += 1
                else:
                    failures += 1
                print()
                time.sleep(args.gap)
        except KeyboardInterrupt:
            print(f"\n{Y}  Loop stopped after {count} orders.{RST}")

    else:
        n = max(1, args.burst)
        for i in range(1, n + 1):
            p  = build_payload()
            ok = fire(p, i, n)
            if ok:
                successes += 1
            else:
                failures += 1
            if i < n:
                print(f"\n  {DIM}Waiting {args.gap}s before next order…{RST}\n")
                time.sleep(args.gap)

    # Summary
    print(f"\n{Y}{'=' * 56}{RST}")
    print(f"  {B}Summary:{RST}  {G}{successes} succeeded{RST}  "
          f"{'  ' + R + str(failures) + ' failed' + RST if failures else ''}")
    print(f"  {DIM}Check the Sentinel Dashboard at http://localhost:5173{RST}")
    print(f"{Y}{'=' * 56}{RST}\n")


if __name__ == "__main__":
    main()
