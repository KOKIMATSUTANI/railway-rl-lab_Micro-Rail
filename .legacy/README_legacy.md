# Dresden Rail Analytics Lab

A research-oriented project for analyzing railway infrastructure and timetable data in the Dresden (VVO) region.

This project explores how geospatial railway data from OpenStreetMap / OpenRailwayMap and timetable data from GTFS can be combined into a unified graph-based representation for downstream analysis, visualization, and machine learning tasks.

The current focus is on:

- Extracting and validating railway infrastructure data using Overpass API
- Processing GTFS timetable data for temporal modeling
- Building graph representations of railway networks
- Experimenting with reinforcement learning (RL) and graph neural networks (GNNs)
- Developing visualization tools for spatial and temporal analysis




# Railway-RL-Lab

A research-oriented project combining **Reinforcement Learning (RL)**, **Graph Neural Networks (GNNs)**, and **geospatial railway infrastructure data**.

This project explores how railway infrastructure data (OpenStreetMap / OpenRailwayMap + GTFS) can be transformed into graph-based representations and used for simulation, analysis, and reinforcement learning environments.

---

## 🚆 Project Goals

* Extract railway infrastructure data from **OpenStreetMap / OpenRailwayMap (Overpass API)**
* Integrate **GTFS timetable data**
* Build a **graph representation of railway networks**
* Apply:

  * Reinforcement Learning (RL)
  * Graph Neural Networks (GNNs)
* Visualize railway systems and learned behaviors
* Optionally deploy with **Docker + AWS CI/CD pipelines**

---

## 🧠 System Overview

```
data/raw → ingestion → processing → graph (GN / GIS) → RL / GNN → visualization
```

Key idea:

> Convert real-world railway infrastructure into a learnable graph environment.

---

## 📁 Project Structure

```
src/
├── gtfs/             # Data acquisition (GTFS-rt)
├── overpass/         # Raw Overpass API experiments
├── processing/       # Parsing, graph building, feature engineering
├── gis/              # GeoJSON / PostGIS integration
├── rl/               # Reinforcement learning environment & training
├── gnn/              # Graph neural network models
├── visualization/    # Maps, dashboards, TensorBoard logging
├── utils/            # Utilities & helpers
```

```
data/
├── raw/              # Raw API outputs (Overpass, GTFS)
├── processed/        # Cleaned datasets
└── exports/          # Final outputs (GeoJSON, Parquet, etc.)
```

---

## Data
### 1. OpenRailwaymap 
### 2. GTFS
### 3. GTFS-rt

## Future Work

### priority 2
- Optimize Docker image size by separating research and runtime dependencies.
- Reduce container startup time for cloud deployment.
- Improve dependency management for production environments. 

## ⚙️ Setup

### 1. Install dependencies

Using `uv` (recommended):

```bash
uv sync
```

or manually:

```bash
pip install -r requirements.txt
```

---

### 2. Activate environment (optional)

```bash
source .venv/bin/activate
```

or simply:

```bash
uv run python
```

---

## 📊 Data Exploration
### jq installation
``` bash
sudo apt update
sudo apt install jq
```

### Quick inspection with `jq`

```bash
jq '.elements | length' data/raw/dresden_railway.json
jq -r '.elements[].tags.railway // empty' data/raw/dresden_railway.json | sort | uniq -c
```

---

### JupyterLab

```bash
uv add --dev jupyterlab
uv run jupyter lab
```

---

## 🗺 Example Notebook

Explore Dresden railway infrastructure:

```
notebooks/dresden_explorer.ipynb
```

---

## 🧪 Overpass Experiments

Example scripts:

* `src/overpass/railway_dresden.py`
* `src/overpass/railway_test_tokyo.py`

These scripts query railway infrastructure data from OpenStreetMap using Overpass API.

---

## 🐳 Docker (optional)

```bash
docker-compose up --build
```

Used for environment reproducibility and future ML scaling.

---

## ☁️ Future Extensions

* PostGIS integration for spatial queries
* AWS-based CI/CD pipeline
* Distributed training for RL/GNN models
* Real-time visualization dashboard

---

## 📌 Notes

* `data/raw/` is not versioned (large geospatial datasets)
* `.venv/` is managed by `uv`
* Experiments in `overpass/` are used for validation and exploration before productionizing into `src/`

---

## 🚀 Vision

This project aims to bridge:

* Railway infrastructure systems
* Graph-based machine learning
* Reinforcement learning environments
* Real-world geospatial data pipelines

into a unified experimental research framework.


## Roadmap

- [x] Graph construction
- [x] Graph encoder
- [x] Q-network
- [ ] Railway environment
- [ ] Replay buffer
- [ ] DDQN training


# 2026.Oct.26 added 

```text 
# Current Status (after integrating GROSS/now updateing) 
## 1. Infrastructure Data Download (OSM)
## 2. Timetable Date Download (GTFS) 
## 3. Graph Network design (GNN)
### 3.1. Designing OSM and GTFS Combined Network on SUMO (GROSS)
### 3.2. extracting signal and switch data and depict on SUMO
### 3.3. inferring Track Circuit based on Ril 420
## 4. Define Trip and Route based on GTFS in Graph

## 5. 
## 6. 

# Current Status (before integrating GROSS/legacy)
## 1. Infrastructure Modeling
- [x] Overpass query development for the Dresden railway network
- [x] GeoJSON-based railway data validation
- [x] Automated OpenStreetMap data acquisition via Overpass API
- [x] Railway infrastructure preprocessing
- [x] Station metadata extraction
- [x] Signal and switch extraction

## 2. Operational Data

### 2.1 GTFS Static
- [x] GTFS Static ingestion

### 2.2 GTFS Realtime
- [x] GTFS Realtime ingestion  
- [x] Docker containerization 
- [x] AWS Fargate deployment
- [x] Automated GTFS-Realtime data collection with AWS (Fargate&EventBridge) 
- [ ] Data preprocessing for generating Graph 


## 4. Graph Construction
- [x] Prototype graph generation (dummy data)
- [ ] Graph generation with real railway data (PyTorch Geometric)

## 5. AI Models
- [x] Prototype reinforcement learning environment
- [ ] GNN implementation
- [ ] RL environment with real railway network
- [ ] Reward function design
- [ ] GNN + RL integration
- [ ] Training & evaluation
```