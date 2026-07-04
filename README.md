# FX Multilateral Netting & Supply Chain Settlement Engine

![CI Pipeline](https://github.com/antoniokuo/fx-multilateral-netting-engine/actions/workflows/ci.yml/badge.svg)
![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)

## ⚡ Executive Summary

Rooted in **quantitative analysis and international trade procurement**, this system bridges the gap between physical logistical realities and high-performance backend infrastructure.

It is an enterprise-grade, stateful multilateral netting engine designed to optimise high-density procurement networks and cross-border financial ledgers. Bypassing standard CRUD bottlenecks, the microservice applies topological graph theory to resolve highly fragmented, bilateral debt matrices into mathematically minimal, zero-sum cleared networks.

## 🏗️ Core Architectural Capabilities

* **Hexagonal Architecture (Ports & Adapters):** Strictly isolates the pure mathematical domain from external volatility. The FastAPI web layer acts solely as an input port, while the SQLite database functions as an output adapter, ensuring the core O(N) engine remains entirely framework-agnostic.
* **Linear Graph Routing (O(N)):** Abandons traditional memory-shifting array mutations in favour of a strictly typed Two-Pointer Traversal algorithm, ensuring minimal CPU cycle waste.
* **Autonomous Arbitrage Detection (O(V × E)):** Implements a mathematically transformed Bellman-Ford algorithm, utilising negative natural logarithms (`-math.log(rate)`) to detect risk-free arbitrage loops and structural pricing inefficiencies before execution.
* **Ephemeral Execution Log:** Integrates `SQLModel` and `SQLite` to generate a real-time, stateful execution log per container lifecycle. This fulfills structural audit requirements for the duration of the deployment instance, designed to be hot-swapped with a managed cloud database in production.
* **Cloud-Native Idempotency:** Protects against distributed state failure and duplicate network retries by enforcing strict `Idempotency-Key` headers, physically bypassing the calculation engine if a duplicate state is detected.
* **Temporal Strategy Pattern:** Abstracts external FX rate APIs via dependency injection, enforcing strict Banker's Rounding (`ROUND_HALF_EVEN`) to eliminate microscopic floating-point precision drift.

## 📊 Hardware Telemetry & Empirical Performance

Algorithmic theory requires physical proof. The engine features a built-in stochastic data generator and hardware profiler (`tracemalloc` and high-resolution `perf_counter`) to verify its physical constraints on legacy consumer hardware (2017 Intel MacBook Air, 8GB RAM).

*Note: Metrics represent pure in-memory algorithmic compute, strictly isolating the O(N) engine from database I/O latency.*

| Metric | Result | System Implication |
| :--- | :--- | :--- |
| **Graph Volume** | 1,000,000 edges (transactions) | Capable of ingesting massive, highly fragmented procurement datasets |
| **Compute Latency** | 5.9 seconds | High-throughput O(N) single-thread execution single-thread execution via Two-Pointer Traversal |
| **Peak RAM** | 18.78 MB | Strict memory partitioning preventing cross-currency arithmetic bleed |

## 🛡️ Enterprise Governance & TDD

This repository enforces strict, automated CI/CD pipeline constraints via GitHub Actions, ensuring the codebase is structurally verified and production-ready before deployment:

* **Test-Driven Development (TDD):** A rigorous `pytest` suite enforcing strict financial invariants (Zero-Sum execution, lossless graph reduction, and empty-ledger boundary states).
* **Static Typing:** `mypy` enforced strictly across all execution paths to prevent runtime type-drift.
* **Code Formatting:** `ruff` configuration locking PEP-8 standards and syntax integrity.

## 🚀 Infrastructure & Deployment

The system is fully containerised via a multi-stage Docker build, optimising image footprint and ensuring strict environment parity across local machines, AWS EC2, or Azure container registries.


### Production Deployment (Docker)
```bash
# 1. Build the production image
docker build -t fx-netting-engine .

# 2. Deploy the microservice with persistent local storage
docker run -d -p 8000:8000 fx-netting-engine
```

### Local Development Environment
For active development or algorithmic modification, the engine runs natively on Python 3.13+.

```bash
# 1. Initialise the isolated environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Execute the verification suite
python3 -m pytest
ruff check src tests
mypy src tests

# 3. Boot the local ASGI server
uvicorn src.api:app --reload
```

## 🔌 API Contract Reference

**`POST /api/v1/netting/clear`**

**Required Header:** `Idempotency-Key: <uuid-v4>`

```json
{
  "base_currency": "GBP",
  "transactions": [
    {
      "id": "e4b29c1d-1234-4567-89ab-cdef01234567",
      "timestamp": "2026-06-14T10:00:00Z",
      "debtor": "TSMC_Fab_1",
      "creditor": "ASML_Holding",
      "currency": "EUR",
      "amount": "1500000.00"
    }
  ]
}
```

**Expected Response (`200 OK`)**
```json
{
  "status": "success",
  "balances": {
    "EUR": {
      "TSMC_Fab_1": "-1500000.00",
      "ASML_Holding": "1500000.00"
    }
  },
  "cached": false
}
```

### Live API Testing
Once the local server or Docker container is running, access the interactive Swagger UI documentation at:
👉 **`http://localhost:8000/docs`**

Alternatively, execute a direct settlement request via terminal:
```bash
curl -X POST "http://localhost:8000/api/v1/netting/clear" \
     -H "Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000" \
     -H "Content-Type: application/json" \
     -d '{
           "base_currency": "GBP",
           "transactions": [
             {
               "id": "e4b29c1d-1234-4567-89ab-cdef01234567",
               "timestamp": "2026-06-14T10:00:00Z",
               "debtor": "TSMC_Fab_1",
               "creditor": "ASML_Holding",
               "currency": "EUR",
               "amount": "1500000.00"
             }
           ]
         }'
```

---
*For a comprehensive breakdown of systemic trade-offs, algorithms, and architectural compromises, please refer to the [Architecture Decision Records (ADRs)](architecture_decision_record.md).*
