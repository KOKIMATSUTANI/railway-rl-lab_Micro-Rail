## ⭐ Interesting References

### attention 
- Veličković, P., Cucurull, G., Casanova, A., Romero, A., Lio, P., Bengio, Y., 2017. Graph attention networks. arXiv preprint https://arxiv.org/abs/1710.10903

- Kool, W., Van Hoof, H., Welling, M., 2018. Attention, learn to solve routing problems! arXiv preprint https://arxiv.org/abs/1803.08475  

## 📖 To Read
- 

## ✅ Read
- 

# Experiential Learning Cycle

| Step | Guiding Question |
|------|-------------------|
| **1. Concrete Experience** | **What did I try?** |
| **2. Reflective Observation** | **What happened?** |
| **3. Abstract Conceptualization** | **What did I learn?** |
| **4. Active Experimentation** | **What will I try next?** |


# ideas
```mermaid
flowchart TD
    A[Passenger-Aware Reinforcement Learning]
    --> B[Sensitivity Analysis]
    --> C[Robustness Analysis]
    --> D[Identification of Performance Degradation]
    --> E[Diagnostic Experiments]

    E --> F[Uncertainty / Distribution Shift]
    F --> F1[Robust RL]
    F --> F2[Distributionally Robust Optimization<br/>DRO]

    E --> G[Insufficient State Information / Partial Observability]
    G --> G1[State Representation Redesign]
    G --> G2[Memory-Based Methods]

    E --> H[Insufficient Modeling of Future Dynamics]
    H --> H1[World Models]
    H --> H2[Model-Based Reinforcement Learning]

    E --> I[Misalignment between Reward and Evaluation Metrics]
    I --> I1[Reward Function Redesign]

    E --> J[Inadequate or Excessive Action Space]
    J --> J1[Action Space Redesign]
    J --> J2[Action Masking]

    E --> K[Insufficient Representation Capacity]
    K --> K1[Deep Reinforcement Learning]
    K --> K2[Graph Neural Networks<br/>GNNs]

    E --> L[Computational Complexity of Combinatorial Optimization]
    L --> L1[MILP]
    L --> L2[Heuristics]
    L --> L3[QUBO]
    L --> L4[Quantum Optimization]
```