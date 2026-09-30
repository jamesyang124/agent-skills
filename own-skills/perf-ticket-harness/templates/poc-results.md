# {{TICKET}} — POC：{{design}}（結果）

日期：{{date}}。程式：`docs/perf-poc-shared/{{slug}}/poc-{{design}}/`（獨立程式，**不動 {{repo}}**；用與 prod 相同的 {{libs + versions}}）。Runner：`run-poc.sh`，原始數據 `runs/run-NN`。
對照的其他方案見 `solution-candidates.md`。

## 機制（POC 實作的就是 prod 要做的形狀）

```
{{request side : one op}}
{{worker side  : lock → replay leftover → atomic swap → one statement → clear}}
```

## 數據（本機 Docker；{{duration}}／run；{{pods}} 個模擬 pod）

| run | 場景 | producers | interval | 吸收 ops/s | request p50 / p99 ms | flush 次數 | 每次 flush entities | batch stmt mean / max ms | **lost** | 等鎖取樣 |
|---|---|---|---|---|---|---|---|---|---|---|

對照 H0 現況（`findings-*.md`）：{{one sentence}}

### 崩潰恢復
{{hand-planted leftover batch → replay result}}

### 對照：{{simplest competing design}}（同一支 POC 的 `-mode direct`）

| run | 方案 | producers | 吞吐 /s | request p50 / p95 / p99 ms | stmt mean / max ms | 等鎖取樣 | lost |
|---|---|---|---|---|---|---|---|

### 有人握著那一列 N 秒時

| | {{competing design}} | {{chosen design}} |
|---|---|---|
| handler 吞吐 | | |
| handler p99 | | |
| stmt max | | |
| lost | | |

### 這輪 bench 抓到的設計規則（prod 實作必須遵守）

1. {{e.g. flush statement timeout < lock TTL — run-NN double-counted without it}}
2. {{e.g. blocked worker parks the batch and retries; never cancel-and-drop}}

## 吞吐上限在哪

## 代價（要接受的）

| 項目 | 內容 |
|---|---|
| 回應值 | |
| 顯示落後 | |
| 暫存層掛掉 | |
| 稽核 / revision | |
| 新背景元件 | |
| 相鄰路徑 | |

## 若要進 {{repo}}（尚未做，等決定）

- files / config / start point / verification via the same bench

## 還沒回答的
