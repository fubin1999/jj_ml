# GlycaPep-PD 心血管风险分析

## 项目结构

- `src/`：全部分析代码，包括 Jupyter notebooks、R 脚本、Quarto 文档和独立实验。
- `data/`：原始输入数据（Excel 文件及 `mono.csv`、`multi.csv`、`cvrisk.csv`），不写入清洗数据或分析结果。
- `results/data/`：清洗后数据、训练/测试集、预测结果和模型比较表。
- `results/figures/`：主分析图表。
- `results/experiments/age_gender/`：年龄与性别增量实验结果及说明。
- `results/reports/`：Quarto 渲染的报告。
- `renv/`、`renv.lock`：R 环境依赖；`requirements.txt`：Python 分析依赖。

## 运行分析

安装 Python 依赖：

```bash
python -m pip install -r requirements.txt
```

Jupyter notebooks 的工作目录为 `src/`：

```bash
cd src
jupyter lab
```

先运行 `clean.ipynb`，将原始输入清洗并划分为 `results/data/train.csv`、`test1.csv`、`test2.csv`；其余 notebooks 从该目录读取数据，并将输出保存到 `results/`。

R 脚本从项目根目录运行。需要启用已有的 renv 环境时，先在 R 中运行 `source("src/activate.R")`，再运行 `source("src/diagnosis.R")` 或 `source("src/cvrist.R")`。

从项目根目录渲染 Quarto 报告，报告保存到 `results/reports/`：

```bash
quarto render
```

年龄与性别增量实验：

```bash
python src/experiments/age_gender/run.py
python src/experiments/age_gender/plot_roc.py
```

实验会读取 `results/data/` 中的训练/测试集，输出保存到 `results/experiments/age_gender/`。详细结果见该目录的 README。

原始数据和主分析结果沿用本地文件，不纳入版本控制。
