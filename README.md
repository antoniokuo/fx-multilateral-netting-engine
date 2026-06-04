# FX Multilateral Netting Engine

## Overview
A backend settlement engine designed to optimise multi-party, multi-currency debt networks. By utilising multilateral netting (graph-based minimum cash flow algorithms), this system calculates the absolute minimum number of transactions required to settle complex financial obligations.

## Architectural Constraints
* **Language:** Python 3.13+ (Strictly Typed via `mypy`)
* **Precision:** `decimal.Decimal` (Zero floating-point arithmetic)
* **Design Pattern:** Event Sourced / Immutable Dataclasses / Hexagonal Architecture
* **Testing:** TDD via `pytest`

## Status
🚧 **Under Active Development (Core Routing Engine)** 🚧
