# ab 29.09.2026
項目ごとにまとめる。優先順位/CS関連/Railway technical stackの3項目
## 優先順位
1. DISPLIBの内容と、それに基づくGNNの設計確認から

## CS関連

### AWS MLOps/LLMOps/XAIなど
- MLOpsに関してはGNN+DRLが一周できてから、好奇心掻き立てられるが今は保留。

## railway technical stack
### SMA 
- Taktfahrplanの内容・anschlussmöglichkeitを補償するときに使えるかも

### DISPLIB
- [ ] jsonファイルのスキーマ確認するところから

# Previous
## 31.07.2026 
### SUMO
WSL（開発・可視化）
  SUMO stable + sumo-gui / netedit
  Python + uv + PyTorch Geometric
  TraCIで状態・行動・報酬をデバッグ

Docker（再現・学習）
  同じSUMO version
  同じuv.lock / Python依存
  headless sumo + 学習スクリプト
  → EC2 / AWS Batchへそのまま移植

## 23.07.2026
### シナリオ
1. 遅延シナリオをどう定義しているか、確認しアイディアを整理
2. switch malfunctionのみ対象、継続時間を定義していることが分かった
3. 遅延の原因が入っているgtfs-rtの内容を絞り込んでシナリオ生成してみる？
4. gtfs-rtの内容からDresdenに限らず原因が定義できそうか見てみる。[gtfs_rt.md](../gtfs_rt.md)

| Step | Guiding Question |
|------|-------------------|
| **1. Concrete Experience** | **What did I try?** |
| **2. Reflective Observation** | **What happened?** |
| **3. Abstract Conceptualization** | **What did I learn?** |
| **4. Active Experimentation** | **What will I try next?** |