# Open MicroRail 技術選定・意思決定記録

| 項目 | 内容 |
| --- | --- |
| 文書ステータス | Proposed v0.1 |
| 最終更新日 | 2026-08-18 |
| 関連文書 | [`requirements.md`](requirements.md)、[`technical-requirements.md`](technical-requirements.md) |

## 1. 選定方針

技術は「論文へ近いか」だけでなく、公開データで意味を説明できること、再現できること、小規模に検証できることを優先する。GROSS、SUMO、RL frameworkを1つの巨大なruntimeへ結合せず、scenario generation、運行意味論、学習を交換可能な境界で分離する。

## 2. 決定一覧

| ID | 決定 | Status |
| --- | --- | --- |
| TD-001 | GROSSを固定commitの外部scenario generatorとして採用 | Proposed |
| TD-002 | SUMO 1.26.0をGROSS compatibility baselineとして固定 | Proposed |
| TD-003 | Canonical rail scenarioを統合境界にする | Accepted |
| TD-004 | 既定資源はsignal block/driveway proxyとする | Accepted |
| TD-005 | 学習用遷移は独自の決定論的離散事象simulator、SUMOは生成・shadow validationに使う | Proposed |
| TD-006 | CoreはPython 3.12＋uv | Accepted |
| TD-007 | GNN/DDQNはPyTorch＋PyTorch Geometricで実装 | Proposed |
| TD-008 | Gymnasiumはinterface boundaryとして採用 | Proposed |
| TD-009 | FCFSを必須baseline、MILPは後続optionalとする | Accepted |
| TD-010 | Parquet/JSON/NPZを役割別に利用し、raw XMLを保持 | Proposed |
| TD-011 | pytest＋Hypothesis＋Ruff＋mypyを品質基盤とする | Proposed |
| TD-012 | TensorBoard＋構造化resultを実験記録に使う | Proposed |
| TD-013 | DockerをGROSS再現環境に限定して採用 | Accepted |
| TD-014 | AWS/Terraformはscale-out補助でありcore dependencyにしない | Accepted |
| TD-015 | 外部入力と実行artifactを非信頼境界で扱う | Accepted |

## 3. 個別決定

### TD-001: GROSSを固定commitの外部scenario generatorとして採用

**Context**

GROSSはOSM・GTFSを対応付け、SUMO network、stop mapping、speed class別routeを7 stageで生成する。論文ではvanilla SUMO pipelineよりteleportと極端な遅延を減らしており、本プロジェクトの上流処理と合致する。公開repositoryの初期commitは`d1134079021eab78fb40fb1e30580809d396f00e`である。

**Decision**

- 当該commitを初期baselineとしてpinする。
- GROSSは別checkoutまたはcontainerとして実行し、出力をadapterで読む。
- GROSS sourceをcore packageへ混在させない。
- repositoryで明示的LICENSEを確認できるまで、sourceをvendor・改変再配布しない。

**Consequences**

- GROSS更新を意図せず取り込まない。
- output contractとversion migrationが必要になる。
- ライセンス確認は本格統合前のblockerとなる。

**Rejected alternatives**

- GROSS sourceを即時copyする: provenanceとlicenseが不明瞭になるため不採用。
- GROSSを再実装する: 初期scopeを超え、比較可能性も下がるため不採用。

### TD-002: SUMO 1.26.0をcompatibility baselineとして固定

**Context**

GROSS論文の実験はSUMO 1.26.0を用いる。一方、現行DockerfileはPPA `stable`を参照しversionを固定していない。SUMOのrail import・signal logicはversion間で変更されうる。

**Decision**

- 最初の再現profileはSUMO 1.26.0とする。
- image digest、`sumo --version`、GROSS commitをartifactへ記録する。
- 新SUMO versionへの更新は、同一fixture・同一snapshotによる差分試験を通して別profileとして行う。

**Consequences**

- 論文条件との比較が明確になる。
- security fixやrail bug fixを自動取得しないため、baselineとmaintenance profileを分ける必要がある。

### TD-003: Canonical rail scenarioを統合境界にする

**Context**

GROSS/SUMO XMLをsimulatorとlearning codeが直接参照すると、data formatと運行意味論が密結合し、変更理由を追跡しにくい。

**Decision**

- 版付きのCanonical rail scenarioを定義する。
- GROSS ID、GTFS ID、OSM ID、provenance、assumptionを保持する。
- simulatorはCanonical modelだけを読み、GROSS XML parserをimportしない。

**Consequences**

- schema設計とmigration costが発生する。
- synthetic fixtureと実データを同じsimulatorで比較できる。
- 将来、別のscenario generatorへ交換しやすい。

### TD-004: 既定資源はsignal block/driveway proxyとする

**Context**

MicroRailのnodeは実軌道回路だが、GTFS/OSM/GROSSは通常その境界を提供しない。SUMOはrail signalが保護するblock、driveway、bidi/flank conflictを表現し、`railsignal-block-output`で出力できる。

**Decision**

- MVPの`open_block` profileではsignal blockまたはdrivewayを排他資源とする。
- `track_circuit`という名称は、外部データで実境界を検証した場合に限る。
- signal/switch/platform等で機械分割した場合は`synthetic_section`と呼ぶ。

**Consequences**

- MicroRail-inspired implementationであり、track-circuit-level reproductionではない。
- 公開データで説明可能な粒度を保てる。
- section releaseの容量効果はMicroRailと異なる可能性があり、感度分析が必要になる。

**Rejected alternative**

- OSM nodeまたはSUMO edgeを一律に軌道回路と呼ぶ: 物理・保安上の意味が成立しないため禁止。

### TD-005: 独自離散事象simulatorを学習に用い、SUMOはshadow validationに使う

**Context**

MicroRailはdecision momentでのみ遷移する離散事象simulatorを用いる。SUMO/TraCIをstep-by-stepで直接学習loopに入れると、process I/Oと細粒度time-stepのcostが大きく、MicroRailの状態遷移・予約規則と差が出る。一方、SUMOはrail signal、driveway、走行挙動を持つため検証価値が高い。

**Decision**

- 学習とbaselineは、Canonical model上の決定論的event simulatorで実行する。
- SUMOはGROSS scenario generation、resource discovery、nominal traversal、shadow/differential validationに使う。
- TraCI controlは将来のvalidation/online-control experimentへ隔離する。

**Consequences**

- 高速でunit test可能な環境を作れる。
- simulator semanticsを自分で正しく実装・検証する責任が生じる。
- SUMOとの差分を継続的に測らなければ、現実性を過大評価する恐れがある。

**Revisit condition**

SUMO/libsumoでdecision-event driven controlを十分高速かつ同一意味論で実装できることがbenchmarkで示された場合、runtime backendの追加を再検討する。

### TD-006: CoreはPython 3.12＋uv

**Context**

既存方針はPython environmentとcommandをuvへ統一している。学習・GIS・XML・testing ecosystemの互換性も高い。

**Decision**

- Python `>=3.12,<3.13`を初期範囲とする。
- dependency add/removeは`uv add`/`uv remove`、実行は`uv run`、再現実行は`uv sync --frozen`を使う。
- GROSS container内のPython環境はcoreと分離する。

**Consequences**

- local/CIの再現手順を簡潔にできる。
- PyTorch/PyG platform compatibilityをGate 0で確認する必要がある。

### TD-007: PyTorch＋PyTorch GeometricでGNN-DDQNを実装

**Context**

MicroRail原実装はTensorFlow 2.7.0だが、これは論文結果のdata置換に必須ではない。本プロジェクトにはgraph data処理、可変サイズgraph、独自masked Q headが必要である。

**Decision**

- neural networkとDDQN updateにはPyTorch 2系を使用する。
- graph batch/message passingにはPyTorch Geometric 2系を使用する。
- exact versionはcompatibility spike後に`uv.lock`へ固定する。
- stable-baselines3やRLlibへ問題を押し込まず、masked variable-action DDQNは小さなcustom training loopで実装する。

**Consequences**

- graph/action固有のlogicを明示的にtestできる。
- training infrastructureを自前保守する必要がある。
- TensorFlow版とのparameter-level reproductionは対象外になる。

### TD-008: Gymnasiumをinterface boundaryとして採用

**Context**

標準`reset`/`step` APIはbaseline、random policy、checker、将来のalgorithm比較に有用だが、rail graphとcandidate action数は可変である。

**Decision**

- domain simulatorから独立したGymnasium adapterを作る。
- experimentごとにmax node/edge/actionを決め、paddingとmaskで固定spaceへ変換する。
- PyG変換はlearning adapterで行う。

**Consequences**

- Gymnasium ecosystemのvalidationを使える。
- 上限設定とpadding overheadが生じる。
- 上限超過をtruncateせずエラーにする必要がある。

### TD-009: FCFSを必須baseline、MILPは後続optionalとする

**Context**

MicroRailはFCFSとRECIFE-MILPを比較する。RECIFE/CPLEXの導入はlicense、model移植、計算資源の負担が大きい。まずsimulatorとmaskの正しさを検証する必要がある。

**Decision**

- MVPはFCFS、random-valid、nominal-onlyをbaselineとする。
- FCFSは学習方策と同一候補・同一maskを利用する。
- MILPはCanonical schemaと制約が安定した後の別milestoneとする。
- MILPなしで「最適またはnear-optimal」と主張しない。

**Consequences**

- 早期にend-to-end比較できる。
- 初期段階ではoptimality gapを評価できない。

### TD-010: Parquet・JSON・NPZを役割別に利用する

**Decision**

| Data | Format | 理由 |
| --- | --- | --- |
| Raw GTFS/OSM/GROSS | 原形式を保持 | 証拠性と再処理 |
| Manifest/config/schema | JSONまたはYAML | 人間可読・版管理 |
| Train/stop/metric tables | Parquet | 型、圧縮、集計効率 |
| Graph arrays | NPZ＋JSON metadata | language-neutralで軽量 |
| Model/checkpoint | PyTorch native | framework state保持 |
| Event/log | JSONL、集計後Parquet | streamingと分析 |

pickleだけを長期Canonical formatとして採用しない。PyTorch checkpointは実行用artifactであり、データ交換形式ではない。

### TD-011: pytest＋Hypothesis＋Ruff＋mypy

**Decision**

- pytest: unit/integration test
- Hypothesis: event ordering、reservation exclusivity、route invariantのproperty test
- Ruff: format/lint/import check
- mypy: public/domain interfaceのstatic type check

新tool導入前に既存repositoryのtoolingを監査し、同等toolがある場合は重複導入しない。

### TD-012: TensorBoard＋構造化resultで実験記録

**Context**

学習曲線だけでなく、scenario別の失敗・遅延・maskをpaired analysisする必要がある。初期段階でMLflow server等を運用する利益は小さい。

**Decision**

- training scalarとhistogramはTensorBoardへ出力する。
- 最終的な研究集計の正本はParquet/JSON manifestとする。
- model registry/MLflow/W&Bは複数実験者・remote trackingが必要になった時点で再検討する。

### TD-013: DockerをGROSS再現環境に限定して採用

**Decision**

- GROSSのC++、SUMO、system libraryはDocker imageで固定する。
- core Python開発はuv環境を正本とする。
- 全開発を1つの巨大containerへ閉じ込めない。
- GROSS wrapper imageはbase digestとpackage versionを記録する。

**Consequences**

- system-level dependencyとML dependencyの変更を分離できる。
- localにDockerとLinux-compatible executionが必要になる。

### TD-014: AWS/Terraformはscale-out補助とする

**Decision**

- tiny fixtureと回廊smoke testはlocal/CI CPUで実行する。
- 地域・全国GROSS runやmulti-seed trainingだけをAWS候補とする。
- 初期候補はCPU `m7i-flex.xlarge`、encrypted gp3 100 GiB、SSM、SSHなし。
- instance/EBS変更はCloudWatchによるpeak RAM/disk/CPU/I/O測定後に決める。
- Terraformはreproducible infrastructureに使うが、明示依頼なしにapply/destroyしない。

### TD-015: 外部入力と実行artifactを非信頼境界で扱う

**Context**

本systemはXML/GZIP/ZIP/YAML/NPZ/Parquet、外部path/URI、GROSS container、PyTorch checkpointを扱う。hash固定だけではXXE、decompression bomb、path traversal、SSRF、unsafe deserialization、resource exhaustion、artifact発行元のなりすましを防げない。

**Decision**

- parser、archive、path/URI、subprocess、checkpoint、redactionを共通boundary moduleへ集約し、版付き`SecurityLimits`で有限上限を必須にする。
- XMLの外部entity/DTD/network access、unsafe YAML tag、NPZ pickle、未信頼PyTorch full checkpointを既定で拒否する。
- GROSSは取得stageと処理stageを分け、処理stageは最小権限・read-only raw・resource limit・原則networkなしで実行する。
- hashは完全性確認として使い、外部配布artifactの真正性にはtrusted manifest、署名またはCI provenanceを別途要求する。
- security negative fixtureとredaction testを品質gateへ含める。

**Consequences**

- 大規模入力には測定に基づくlimit profileの調整が必要になる。
- 完全な学習再開checkpointは信頼済み生成物に限定され、外部modelはweights-only inference経路を使う。
- adapterごとの場当たり的な検証を避け、拒否理由とテストを共通化できる。


## 4. Library選定

| 用途 | 採用候補 | 採用理由 | 初期非採用 |
| --- | --- | --- | --- |
| XML/GZIP | Python stdlib＋`lxml` | SUMO XMLのstream parse、namespace、性能 | DOMへ全件load |
| Validation | Pydantic v2＋JSON Schema | typed boundaryと人間可読error | 無型dictの受け渡し |
| Table | NumPy、pandas、PyArrow | 集計とParquet | CSVを長期正本にすること |
| Operational graph | NetworkX | 小規模構築・検証・deadlock graph | 学習tensorをNetworkXだけで保持 |
| GNN | PyTorch Geometric | PyTorch統合、message passing、batch | TensorFlow 2.7の新規固定 |
| Environment | Gymnasium | API標準化とchecker | simulator logicをenvironment wrapperへ直書き |
| Config | YAML＋Pydantic validation | 読みやすさと型検証 | Hydraの早期導入 |
| CLI | `argparse`または既存CLI framework | dependency最小化 | GUIを先に作ること |
| Logging | stdlib logging＋JSON formatter | dependency最小・構造化 | ad-hoc `print`のみ |
| Visualization | Matplotlib/Seaborn | 再現可能な静的図 | dashboardを研究coreにすること |

## 5. Version固定ルール

- `uv.lock`、GROSS commit、container digest、SUMO versionを同じexperiment manifestへ記録する。
- exact package versionをMarkdownだけに置かず、機械可読lockを正本にする。
- source data URLが更新型の場合、download後のhashとsnapshot copyを正本にする。
- dependency updateは同一tiny fixtureと少なくとも1つのopen-data smoke scenarioで差分確認する。
- graph/action/reward/schemaに影響するupdateは新しいexperiment series IDを付ける。

## 6. 再検討が必要な条件

| 決定 | Revisit condition |
| --- | --- |
| signal block proxy | 信頼できるtrack-circuit/interlocking open dataが入手できたとき |
| custom simulator | libsumo backendが同じdecision semanticsで十分高速・testableになったとき |
| PyTorch/PyG | 既存repositoryに検証済みTensorFlow implementationがあり、移行costが利益を上回るとき |
| custom DDQN loop | variable graph/action maskを正しく扱う成熟libraryが、必要なdebug visibilityを提供するとき |
| TensorBoard only | remote team、model registry、experiment access controlが必要になったとき |
| FCFS only | Canonical constraintsが安定し、open-source MILP baselineを公平に構築できるとき |
| AWS candidate size | 実測peak resourceが継続的に70–80%を超える、または大幅に余るとき |

## 7. 参照

- [GROSS repository at the pinned commit](https://github.com/ethz-coss/GROSS/tree/d1134079021eab78fb40fb1e30580809d396f00e)
- [SUMO railway documentation](https://sumo.dlr.de/docs/Simulation/Railways.html)
- [SUMO GTFS tutorial](https://sumo.dlr.de/docs/Tutorials/GTFS.html)
- [GTFS Schedule Reference](https://gtfs.org/documentation/schedule/reference/)
- [PyTorch Geometric documentation](https://pytorch-geometric.readthedocs.io/)
