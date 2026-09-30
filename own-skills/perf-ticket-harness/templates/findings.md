# {{TICKET}} — {{symptom}}：本機重現與數據（H0 baseline）

日期：{{date}}。Bench：`docs/perf-poc-shared/{{slug}}/`（run-01～run-NN，原始數據在 `runs/run-NN/`）。
Stack：{{repo}} `{{sha}}` + {{stack components}}，本機 Docker。**本機數字只證明機制，不預測 prod 延遲**（本機 {{local rate}}，prod 這條路徑約 {{prod rate}}）。

## 結論（一句話）

{{One sentence: what the flagged statement is, who emits it, and what the measured mechanism is. Every noun here must be backed by a run below.}}

## 六個 run

| run | 場景 | conc | blocker | {{flag}} | ok/sent | **lost** | {{stmt}} mean ms | {{stmt}} max ms | stddev | Lock 取樣占比 | 最大排隊深度 | req p50 / p95 / max ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | uniform screen | | – | | | | | | | | | |
| 02 | uniform | | – | | | | | | | | | |
| 03 | **hotspot** | | – | | | | | | | | | |
| 04 | hotspot | | row N s | | | | | | | | | |
| 05 | uniform | | index N s | | | | | | | | | |
| 06 | hotspot | | – | {{flag off}} | | | | | | | | |

每個 run 都是：reset 計數 → N 次請求（uniform 隨機打 M 個 entity；hotspot 全打同一個）→ `pg_stat_statements` / `pg_stat_activity` 取樣 / 副作用表列數 / Σ counter。

## 三個問題的答案

**(a) 這條 SQL 是不是 {{endpoint}} 產的？** {{answer + run numbers}}. 每一次請求在 DB 端實際是：

| 每次請求 | 次數 | 來源 |
|---|---|---|
| | | |

**(b) 同 entity 併發時會不會排隊、排隊佔多少？** {{answer with mean/stddev/lock% deltas between uniform and hotspot runs}}

**(c) 有外部持鎖者時，exec time 會不會被灌水而 rows 不變？** {{answer; note which lock levels show in pg_stat_statements exec time and which do not}}

## 對報表的更正

1. {{attribution correction with file:line}}
2. {{cumulative vs weekly / identical max = one event}}
3. {{marginal cost per call arithmetic}}

## 候選方案（只列名，看完數據再決定）

| | 對 (b) 排隊 | 對 (b) 丟計數 | 對 {{side effect}} | 備註 |
|---|---|---|---|---|
| | | | | |

## 向 SRE 要的 prod 數據

1. 該 statement 的 `pg_stat_statements` 每日快照（calls, total, mean, min, max, stddev, rows），報週 delta，註明上次 reset 日期。
2. Performance Insights 該 SQL digest 的 wait events；若還在保留期，找 max 那次的時間窗。
3. {{side-effect tables}} 每日列數與大小。

## Bench 的已知限制

- {{cache config differences}}
- {{row-size / data-shape differences}}
- {{error counts and why they do not affect the lost calculation}}
- {{repeatability evidence: two runs with the same seed}}
