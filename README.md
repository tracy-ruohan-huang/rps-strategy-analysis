# Rock-Paper-Scissors Strategy Analysis

A statistical analysis of strategies in Rock-Paper-Scissors through large-scale simulation.

This repository contains the code and data for the paper:

**Ruohan Huang, "Adapt to Win: A Statistical Analysis on Strategies in Rock-Paper-Scissors,"** *American Journal of Student Research*, Vol. 2, No. 4, December 2024.
DOI: [10.70251/HYJR2348.24129148](https://doi.org/10.70251/HYJR2348.24129148)

## Overview

Nine strategies were tested in round-robin Rock-Paper-Scissors tournaments: Random, Constant, Sequential, Mirror, Exclusion, Reaction, Reverse Mirror, Probability-Weighted, and Multi-Round Observation.

- 45 unique pairings (including self-pairings)
- 10 to 1,000 rounds per matchup
- Performance tracked with moving averages, CUSUM, and decay-weighted metrics

**Key finding:** Multi-Round Observation achieved the highest mean overall win rate (46.98%) — adaptive strategies that leverage historical patterns outperform static ones.

## Repository Structure

- `src/main/python/` — Simulation and analysis code
  - `RPS_RoundRobin_Simulator.py` — Main round-robin tournament simulator
  - `RPS_RoundRobin_CUSUM.py`, `RPS_RoundRobin_CUSUM_MV.py` — CUSUM change-point analysis
  - `RPS_RoundRobin_Stat_FED.py` — Statistical analysis
  - `RPSGame2Players.py`, `RPSGameXPlayers.py`, `RPSStrategy2Players.py` — Game engines
  - `data_analysis/`, `data_collection/`, `data_processing/`, `data_simulation/` — Pipeline stages
- `data/` — Raw and processed datasets, simulation outputs
- `results/` — Analysis results, summary tables, figures
- `docs/` — Research notes and paper figures

## Requirements

- Python 3.x
- `pandas`, `numpy`, `matplotlib`, `scipy`, `tqdm`

## Usage

```bash
cd src/main/python
python RPS_RoundRobin_Simulator.py
```

## License

MIT License — see [LICENSE](LICENSE).
