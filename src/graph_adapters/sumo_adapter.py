vimport sumolib
import torch
from torch_geometric.data import Data

# 1. final.net.xml.gz からネットワーク構造を直接読み込む (.gzのままでOK!)
net = sumolib.net.readNet("working_scenario/sumo/final.net.xml.gz")

# 2. 全エッジ（線路）を取得し、ID -> インデックスの辞書を作成
edges = net.getEdges()
edge_id_to_idx = {edge.getID(): i for i, edge in enumerate(edges)}

# 3. エッジ同士の接続関係（トポロジー）から PyG の edge_index を作成
from_nodes = []
to_nodes = []

for edge in edges:
    src_idx = edge_id_to_idx[edge.getID()]
    # このエッジから直接進める次のエッジ（Outgoing Edges）を取得
    for outgoing_edge in edge.getOutgoing():
        out_id = outgoing_edge.getID()
        if out_id in edge_id_to_idx:
            dst_idx = edge_id_to_idx[out_id]
            from_nodes.append(src_idx)
            to_nodes.append(dst_idx)

edge_index = torch.tensor([from_nodes, to_nodes], dtype=torch.long)

# 4. 初期状態のノード特徴量 x (例: 占有フラグ [0.0] のダミー)
x = torch.zeros((len(edges), 1), dtype=torch.float)

# 5. PyG Graph オブジェクトの完成！
graph_data = Data(x=x, edge_index=edge_index)

print("✅ 最速 PyG グラフ構築完了!")
print(f"・ノード数 (SUMO Edges): {graph_data.num_nodes}")
print(f"・エッジ数 (Connections): {graph_data.num_edges}")