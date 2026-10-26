# Open Railway Intelligence
An Open-Source AI Framework for Railway Traffic Management 

## Table of Contents

- [Project Overview](#project-overview)
- [Motivation](#motivation)
- [Repository Structure](#repository-structure)
- [Current Status](#current-status)  
Last Update on 26.Oct.2026
- [Future Direction](#future-direction)
- [Reference](#references)
- [Data Sources](#data-sources)

## Project Overview
- Collect railway infrastructure data (e.g., tracks, switches, signals, and platforms) from OpenStreetMap (OSM).
- Integrate timetable and real-time operational data from GTFS and GTFS-Realtime.
- Construct a dynamic railway graph by combining static infrastructure and real-time operational information.
- Develop intelligent railway traffic management using machine learning, with a primary focus on reinforcement learning.
- Build an open, extensible, and reproducible framework for railway traffic optimization.
## Motivation

Railway delays remain one of the biggest challenges in modern railway operations, particularly in Germany.

This project aims to investigate how modern AI techniques can support railway traffic management by combining:

- **OpenStreetMap (OSM)** for railway infrastructure.
- **GTFS-Realtime** for dynamic operational information.
- **AWS Cloud Services** for scalable and practical deployment.
- **Graph Neural Networks (GNNs)** for railway network representation.
- **Reinforcement Learning (RL)** for traffic optimization.




## Repository Structure
```text
.
├── AGENTS.md
├── CLAUDE.md
├── LICENSE.txt
├── README.md
├── data
│   ├── scenarios
│   │   └── sachsen-anhalt
│   └── total_lane.py
├── displib
│   ├── Format_swi_1.json
│   └── swi_1.json
├── docker
│   ├── Dockerfile
│   ├── Dockerfile.gtfs_rt_ingest
│   └── docker-compose.yml
├── docs
│   ├── CLAUDE.md
│   ├── IaC.md
│   ├── architecture.md
│   ├── claude-code-implementation.md
│   ├── graph.md
│   ├── gtfs_rt.md
│   ├── japanese
│   │   └── jp_idea.md
│   ├── license.md
│   ├── osm.md
│   ├── requirements.md
│   ├── rl.md
│   ├── scenario.md
│   ├── sumo.md
│   ├── technical-requirements.md
│   ├── technology-decisions.md
│   └── todo_ideas.md
├── logs
│   └── ingest_gtfs_rt.log
├── pyproject.toml
├── scripts
│   ├── init_project.sh
│   └── run_gtfs_rt_ingestion.sh
├── src
│   ├── __init__.py
│   ├── gnn
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   └── graph_state_encoder.py
│   ├── gtfs_rt
│   │   ├── extract_delay_snapshot.py
│   │   └── ingest_gtfs_rt.py
│   ├── rl
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── agent.py
│   │   ├── q_network.py
│   │   └── railway_env.py
│   ├── train.py
│   └── visualisation
│       ├── __pycache__
│       └── plot_biederitz_gerwisch.py
├── terraform
│   ├── main.tf
│   ├── outputs.tf
│   ├── terraform.tf
│   ├── terraform.tfstate
│   ├── terraform.tfstate.backup
│   └── variables.tf
├── tests
│   ├── __pycache__
│   │   └── conftest.cpython-313-pytest-9.1.1.pyc
│   ├── conftest.py
│   └── src
│       └── unit
└── uv.lock

```

## Current Status
## 1. GROSS-Based Railway Scenario Generation
- [x] Acquire GTFS Static data
- [x] Acquire OpenStreetMap (OSM) data
- [x] Generate a railway scenario using GROSS
- [x] Inspect and validate the generated scenario in the SUMO GUI
- [ ] Extract signal and switch information from the GROSS-generated scenario
- [ ] Infer track circuit boundaries and topology

## 2. Graph Neural Network (GNN)
- [ ] Construct a track-circuit-level graph using PyTorch Geometric
- [ ] Identify and extract the applicable features from the 12-feature set used in MicroRail

## 3. Reinforcement Learning (RL)
- [ ] Design the RL environment using Gymnasium
- [ ] Define the action space
- [ ] Implement action masking
- [ ] Design the reward function
- [ ] Visualize training metrics and evaluate agent performance using TensorBoard

## Future Direction 
The ultimate goal is to build an open-source platform for intelligent railway traffic management that can contribute to reducing delays in real-world railway operations while remaining extensible to future technologies.

## ideas
- DISPLIB (Train Dispatching benchmark library)
- railML (an open-source railway markup language designed to facilitate seamless communication among diverse railway applications)
- Deutsche Bahn API (German Railway API)
- Multi Agent Deep Reinforcement Learning (MADRL)
- Quantum Computing / Quantum Machine Leaning (QML)
- Mix Integer Linier Programming (MILP) 
- Long Short-Term Memory (LSTM)

# References
## References
- Fouladi, A., Okhrin, O., & Bešinović, N. (2026). *Real-time microscopic train rescheduling using graph neural network based reinforcement learning*. SSRN Preprint. https://doi.org/10.2139/ssrn.6604465
- Juri Penell, Damian Dailisan (2026). *GROSS: German Rail Open-Source SUMO Scenario*. arxiv link https://arxiv.org/abs/2606.03282
- About railML https://www.railml.org/en/about-railml


# License
This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.

