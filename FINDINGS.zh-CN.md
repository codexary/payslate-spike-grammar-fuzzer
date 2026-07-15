[English](FINDINGS.md) | 简体中文

# 语法生成与字节变异的实验结果

本记录对应 2026 年 7 月 16 日的实验。输入均为合成数据，检查均在本地运行。以下每条命令分别为两种策略分配 1,000 个候选文件：

```sh
python3 compare.py --budget 1000 --seed 120012
python3 compare.py --budget 1000 --seed 1
python3 compare.py --budget 1000 --seed 2
```

命令使用 Python 3.12.13 运行，全部八项单元测试通过。

| 种子 | 每种策略的预算 | 已覆盖 / 全部语法备选项 | 语法通过数 | 变异通过数 | 语法拒绝类别数 | 变异拒绝类别数 |
| --- | --- | --- | --- | --- | --- | --- |
| 120012 | 1,000 | 89 / 89 | 506 | 64 | 1 | 8 |
| 1 | 1,000 | 89 / 89 | 502 | 51 | 1 | 7 |
| 2 | 1,000 | 89 / 89 | 466 | 47 | 1 | 6 |

按上述命令顺序，原始输出如下：

```json
{"seed": 120012, "budget": 1000, "grammar_alternatives_covered": 89, "grammar_alternatives_total": 89, "grammar_accepted": 506, "mutation_accepted": 64, "grammar_distinct_rejections": 1, "mutation_distinct_rejections": 8}
{"seed": 1, "budget": 1000, "grammar_alternatives_covered": 89, "grammar_alternatives_total": 89, "grammar_accepted": 502, "mutation_accepted": 51, "grammar_distinct_rejections": 1, "mutation_distinct_rejections": 7}
{"seed": 2, "budget": 1000, "grammar_alternatives_covered": 89, "grammar_alternatives_total": 89, "grammar_accepted": 466, "mutation_accepted": 47, "grammar_distinct_rejections": 1, "mutation_distinct_rejections": 6}
```

语法生成的候选文件中，46.6–50.6% 通过了完整的本地解析和字段校验。变异文件较少到达这一阶段，通过率为 4.7–6.4%。这支持用有界语法提供能够通过入口校验、用于更深层测试的输入，但不能据此判断两种策略在产品内部实际执行到了哪里。

每次运行都选中过全部 89 个语法备选项，但这不代表覆盖了所有组合，更不代表产品代码覆盖率。语法策略唯一触发的拒绝类别是 `unknown_header`，来自语法里的可选额外列。ADR 0003 要求拒绝这些列，因此 CSV 结构有效并不意味着文件一定会被接受。真实导出常带这类列，团队应当核对产品是否真按这条规则处理，以及这条规则还该不该保留。

变异触发了更多语法本身没有设计去生成的拒绝类别。重放相同的变异序列后，三次运行都出现了 UTF-8、未知表头、列数、日期、时间和节假日值错误；种子 120012 和 1 还出现了单独 CR 错误，种子 120012 出现了表头分隔符错误。对已被接受的文件做少量变异，可以在保留周围结构的同时破坏某个字段；不过一至三次字节操作也可能影响多个字段。这里的原始文件是通过本地检查的逼真合成样本，没有使用真实工资数据。统计只记录每个文件最先报告的拒绝原因，不能用来衡量不同的内部执行路径。

产品测试应同时保留语法生成和对已接受文件的变异。前者提供多种受支持的格式，较容易通过校验；后者补充语法规则以外的畸形输入。最终应根据产品的 HTTP 响应判定结果，并在产品边界验证节假日标志等解析值。本地检查只是可达性的近似指标，不能替代产品判定；本实验没有发送任何 HTTP 请求。

三个随机种子和一个变异原始文件只能支持有限的比较。两种策略的候选文件预算相同，但文件长度、执行时间和不重复文件的数量并未控制。因此这些结果不能说明缺陷发现能力、吞吐量或生产环境的接受率。关于引号内换行策略及其他与产品可能不同的地方，参见 [README](README.zh-CN.md)。
