# Mortal 582500 vs 298k：每模型 8000 局配对测试 / 8,000 games per model

[中文](#中文) · [English](#english)

## 中文

### 结论与下载建议

**如果只在这两个四人麻将 Mortal checkpoint 中选一个，本次测试推荐优先下载 [582500](https://huggingface.co/Yuchen1457/mortal-582500)。**在相同种子、四个座位轮换的 1 对 3 测试中，它的平均顺位、Rank PT 和四位率都优于 [298k](https://huggingface.co/VoidShine/mortal-298k)。这是本测试设置下的结果，不代表所有对手、规则或线上环境中的绝对强度。

| 模型 | 对局数 | 平均顺位 ↓ | 一位率 | 二位率 | 三位率 | 四位率 ↓ | Rank PT / 局 ↑ |
|---|---:|---:|---:|---:|---:|---:|---:|
| **582500** | 8000 | **2.497625** | 25.0375% | 24.7000% | 25.7250% | **24.5375%** | **+0.523125** |
| 298k | 8000 | 2.512375 | 25.1625% | 23.8875% | 25.5000% | 25.4500% | −0.961875 |

582500 的平均顺位低 **0.01475**，Rank PT 高 **1.485/局**，四位率低 **0.9125 个百分点**。它的一位率略低于 298k；推荐主要依据平均顺位、Rank PT 和四位率。

按 200 组配对批次重抽样，Rank PT 差值（582500 减 298k）的 **95% bootstrap 区间为 −0.962 至 +3.836**，包含 0。在「批次差值近似正态、未知均值和方差使用参考先验」的模型下，582500 的真实期望 Rank PT 更高的后验概率约 **88.4%**；贝叶斯 bootstrap 得到 **88.6%**。这说明目前证据倾向 582500，同时仍有不确定性；**88.4% 不是单局胜率**。

### 模型来源与下载

| 模型 | 来源与下载 | 本测试使用的权重 SHA-256 |
|---|---|---|
| 582500 | [Hugging Face 模型页](https://huggingface.co/Yuchen1457/mortal-582500) · [权重文件 `mortal_582500.pth`](https://huggingface.co/Yuchen1457/mortal-582500/blob/main/mortal_582500.pth) | `738e0d6e3c0ce9671629554ad39abd147d2ffbac676e80b194c83f2acc0fea20` |
| 298k | [Hugging Face 模型页](https://huggingface.co/VoidShine/mortal-298k) · [权重文件 `mortal_298k.pth`](https://huggingface.co/VoidShine/mortal-298k/blob/main/mortal_298k.pth) | `bfb3a6c072aa0bfd4171a9cdc77cb6c02ae42cde920843f9e5784394f23447d8` |

模型权重没有重新上传到本仓库；请到原作者页面下载，并遵守各自的许可证及说明。582500 是四人模型 checkpoint，需要兼容的 [Mortal 运行环境](https://github.com/Equim-chan/Mortal)，单独下载 `.pth` 不等于可直接运行的程序。

### 我做了什么

1. 在 Kaggle GPU 环境中固定 [Mortal 代码提交 `0cff2b5`](https://github.com/Equim-chan/Mortal/tree/0cff2b52982be5b1163aa9a62fb01f03ce91e0d2)，编译 `libriichi`，下载并校验两份模型权重。
2. 使用 `OneVsThree.py_vs_py`：582500 作一个挑战者、另三席为 298k；再交换方向。每个种子轮换四个座位。
3. 固定种子 **10000–11999**，每 10 个种子构成一组配对批次。前 1000 个种子及新增的后 1000 个种子互不重合；共 **200 组、每模型 8000 局、总计 16000 局**。双方使用相同的种子和 `KEY=9427144312314120477`。
4. 将前期交互式运行保存的 **115 条方向记录**作为 checkpoint 恢复到后台 Notebook。运行代码按「种子 + 挑战者」跳过已有记录，避免重复计数；最终得到 **400 条方向记录、200 组完整配对**。[Kaggle 完成版本](https://www.kaggle.com/code/ess666/mortal-582500-vs-298k-benchmark?scriptVersionId=352932090)显示 `BENCHMARK COMPLETE`。
5. 从 Kaggle 保存原始 JSONL 和 CSV；原始 JSONL 的 SHA-256 为 `9e09abc6d7eb373314f044faeeb7f6a1fe20ad6ac395fca4f5f581050c9d5fe9`。另制作标准 JSON、可复核的统计脚本和包含全部记录的离线 HTML 面板。

计分为一位 **+90**、二位 **+45**、三位 **0**、四位 **−135**，Rank PT 是这些分数的每局平均值。试跑种子 `9900` 不计入正式结果。统计以配对批次为重抽样单位，避免把相同种子及座位轮换的对局都当成独立样本。

### 仓库文件

| 文件 | 内容 |
|---|---|
| [`index.html`](index.html) | 自带完整 400 条记录的离线交互面板，可下载 JSONL/CSV，也可导入其他 JSONL |
| [`data/mortal_benchmark_results.jsonl`](data/mortal_benchmark_results.jsonl) | Kaggle 原始输出，逐行 JSON；**分析的原始依据** |
| [`data/mortal_benchmark_results.json`](data/mortal_benchmark_results.json) | 相同 400 条记录组成的标准 JSON 数组 |
| [`data/mortal_benchmark_summary.csv`](data/mortal_benchmark_summary.csv) | Kaggle 原始汇总 CSV |
| [`data/summary.json`](data/summary.json) | 完整指标、差值区间及模型条件下的优势概率 |
| [`notebooks/kaggle_8000_each_with_checkpoint.ipynb`](notebooks/kaggle_8000_each_with_checkpoint.ipynb) | 此次 Kaggle 后台运行的代码，保留 115 条 checkpoint 恢复逻辑 |
| [`analysis/recompute.py`](analysis/recompute.py) | 校验哈希、批次与 CSV，重新计算所有统计值 |

### 如何复核

下载整个仓库后，双击 `index.html` 可在 Chrome 等浏览器中查看离线面板。也可以运行：

```bash
python -m pip install -r requirements.txt
python analysis/recompute.py
```

脚本会校验 **400 条记录、200 组配对、每模型 8000 局**，并生成 `data/summary.json`。如需在 Kaggle 重新跑 Notebook，请在 Notebook 设置中开启 **GPU 和 Internet**。随附 Notebook 的第五个代码单元含这次的 115 条 checkpoint；完全从零开始的新实验需要移除该恢复块，并使用新的、不重叠的种子范围。相同种子的重复运行不能视为新增独立证据。

本结果只覆盖这个四人 1 对 3 离线评估，不能直接换算为雀魂段位、通用 Elo 或对其他模型的优势。

## English

### Result and download recommendation

**If choosing between these two four-player Mortal checkpoints, this benchmark favors downloading [582500](https://huggingface.co/Yuchen1457/mortal-582500) first.** With matched seeds and four-seat rotation in a one-versus-three arena, it achieved a better average rank, higher Rank PT, and lower fourth-place rate than [298k](https://huggingface.co/VoidShine/mortal-298k). This recommendation applies to the tested protocol; it is not a claim of universal superiority against every opponent or in online play.

| Model | Games | Mean rank ↓ | 1st | 2nd | 3rd | 4th ↓ | Rank PT / game ↑ |
|---|---:|---:|---:|---:|---:|---:|---:|
| **582500** | 8000 | **2.497625** | 25.0375% | 24.7000% | 25.7250% | **24.5375%** | **+0.523125** |
| 298k | 8000 | 2.512375 | 25.1625% | 23.8875% | 25.5000% | 25.4500% | −0.961875 |

The observed 582500 minus 298k Rank PT difference is **+1.485 per game**. Its 95% paired-batch bootstrap interval is **−0.962 to +3.836**, so the interval still includes zero. Under an approximately normal batch-difference model with a reference prior for unknown mean and variance, the posterior probability that 582500 has a higher expected Rank PT is **88.4%**; a Bayesian bootstrap gives **88.6%**. These are probabilities about the expected metric under this protocol, **not single-game win rates**. The 582500 first-place rate is slightly lower; its overall average rank, Rank PT, and fourth-place rate drive the recommendation.

### Model sources

| Model | Original source and checkpoint | Checkpoint SHA-256 used here |
|---|---|---|
| 582500 | [Model page](https://huggingface.co/Yuchen1457/mortal-582500) · [`mortal_582500.pth`](https://huggingface.co/Yuchen1457/mortal-582500/blob/main/mortal_582500.pth) | `738e0d6e3c0ce9671629554ad39abd147d2ffbac676e80b194c83f2acc0fea20` |
| 298k | [Model page](https://huggingface.co/VoidShine/mortal-298k) · [`mortal_298k.pth`](https://huggingface.co/VoidShine/mortal-298k/blob/main/mortal_298k.pth) | `bfb3a6c072aa0bfd4171a9cdc77cb6c02ae42cde920843f9e5784394f23447d8` |

The model weights are linked to their original publishers and are not redistributed here. Check each model's license and documentation. The 582500 checkpoint needs a compatible [Mortal runtime](https://github.com/Equim-chan/Mortal); the `.pth` file is not a standalone executable.

### What was done

1. On Kaggle GPU, pinned [Mortal commit `0cff2b5`](https://github.com/Equim-chan/Mortal/tree/0cff2b52982be5b1163aa9a62fb01f03ce91e0d2), built `libriichi`, and downloaded and SHA-256-checked both model weights.
2. Ran `OneVsThree.py_vs_py` in both directions: one 582500 challenger versus three 298k opponents, then one 298k challenger versus three 582500 opponents. Every seed rotates through four seats.
3. Used fixed seeds **10000–11999**, grouped into **200 paired batches** of ten seeds. Seeds 10000–10999 and the additional 11000–11999 do not overlap. This yields **8000 games per model, 16000 total**, with the same seed set and `KEY=9427144312314120477` in both directions.
4. Restored **115 previously saved direction records** into the background Kaggle run. The notebook skips existing seed-and-challenger keys, preventing duplicates. Its [completed Kaggle version](https://www.kaggle.com/code/ess666/mortal-582500-vs-298k-benchmark?scriptVersionId=352932090) reports `BENCHMARK COMPLETE`, with 400 direction records and 200 complete pairs.
5. Preserved the original JSONL and CSV, converted the 400 records to a standard JSON array, built an offline dashboard, and added a reproducible analysis script. The original JSONL SHA-256 is `9e09abc6d7eb373314f044faeeb7f6a1fe20ad6ac395fca4f5f581050c9d5fe9`.

Rank PT scores are **+90 / +45 / 0 / −135** for first through fourth. Pilot seed `9900` is excluded. Resampling uses paired batches as units to account for the shared seeds and seat rotations.

### Files and reproduction

| File | Purpose |
|---|---|
| [`index.html`](index.html) | Offline dashboard with all records embedded; supports JSONL/CSV downloads and JSONL import |
| [`data/mortal_benchmark_results.jsonl`](data/mortal_benchmark_results.jsonl) | **Original Kaggle JSONL**, the source of truth |
| [`data/mortal_benchmark_results.json`](data/mortal_benchmark_results.json) | Standard JSON array of the same 400 records |
| [`data/mortal_benchmark_summary.csv`](data/mortal_benchmark_summary.csv) | Original Kaggle summary CSV |
| [`data/summary.json`](data/summary.json) | Metrics, intervals, and model-conditional probability |
| [`notebooks/kaggle_8000_each_with_checkpoint.ipynb`](notebooks/kaggle_8000_each_with_checkpoint.ipynb) | Kaggle run source, including the 115-record checkpoint restoration |
| [`analysis/recompute.py`](analysis/recompute.py) | Validates and recomputes the published numbers |

Download the repository and open `index.html` locally, or run:

```bash
python -m pip install -r requirements.txt
python analysis/recompute.py
```

The script validates all **400 records, 200 paired batches, and 8000 games per model**. To rerun the Kaggle notebook, enable **GPU and Internet**. Its fifth code cell embeds the original 115-record checkpoint; for a genuinely fresh experiment, remove that restoration block and use a new, nonoverlapping seed range. Repeating the same seeds is not new independent evidence.

This offline four-player, one-versus-three result should not be read as a Mahjong Soul rank, a general Elo rating, or proof of superiority over other models.
