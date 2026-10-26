import torch
from torch_geometric.data import Data

# ==========================
# Node Feature
# ==========================
# 例:
# [delay(sec), is_platform, degree]

x = torch.tensor([
    [120.0, 1.0, 2.0],   # Dresden Hbf
    [ 30.0, 1.0, 2.0],   # Dresden Mitte
    [  0.0, 1.0, 1.0],   # Dresden Neustadt
], dtype=torch.float)

# ==========================
# Edge
# ==========================
# Hbf <-> Mitte <-> Neustadt

edge_index = torch.tensor([
    [0, 1, 1, 2],
    [1, 0, 2, 1]
], dtype=torch.long)

data = Data(
    x=x,
    edge_index=edge_index
)

print(data)