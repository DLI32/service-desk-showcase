# 通用 Fabric 定义脚本

来源思路：S6、S8、S9，见 [来源映射](../../docs/SOURCES.md)。本次重写为无固定账号、资源标识和安装路径的 Python 标准库脚本。需要 Python 3.9 或以上；联网子命令还需要已登录且权限正确的 Azure CLI。本次只做离线验证，没有运行联网子命令。

## 私有工作目录

所有备份、计划与候选 JSON 留在仓库外。以下环境变量由使用者在自己的终端设置；没有默认资源值：`WORKSPACE_ID`、`REPORT_ID`、`MODEL_ID`、`NOTEBOOK_ID`、`PRIVATE_DIR`。`PRIVATE_DIR` 必须指向已创建的私有目录。可用 `--az /path/to/az` 指定 CLI。

从仓库根目录运行：

```bash
python3 scripts/fabric/fabric_definition.py --help
python3 scripts/fabric/patch_pbir.py --help

python3 scripts/fabric/fabric_definition.py get reports \
  --workspace "${WORKSPACE_ID}" --item "${REPORT_ID}" \
  --output "${PRIVATE_DIR}/report-before.json"
```

`kind` 支持 `reports`、`semanticModels`、`notebooks`；分别使用 PBIR、默认模型格式、ipynb。输出采用独占创建，不覆盖已有文件。定义、Notebook 源码与输出可能含私密信息，不能将其直接公开。

## 离线比较与补丁

```bash
python3 scripts/fabric/fabric_definition.py compare \
  "${PRIVATE_DIR}/report-before.json" "${PRIVATE_DIR}/report-candidate.json"

python3 scripts/fabric/patch_pbir.py \
  --source "${PRIVATE_DIR}/report-before.json" \
  --plan "${PRIVATE_DIR}/patch-plan.json" \
  --output "${PRIVATE_DIR}/report-candidate.json"
```

计划格式仅示意，需从自己的定义确认 part 路径、属性及旧值：

```json
[
  {
    "part": "definition/pages/<PAGE_ID>/visuals/<VISUAL_ID>/visual.json",
    "keys": ["position", "x"],
    "old": 20,
    "new": 40
  }
]
```

字符串 keys 表示对象属性，整数表示数组索引。仅修改现有属性，旧值及其 JSON 类型必须匹配；禁止同一属性重复修改。不修改输入文件，未选中的 part payload 原样保留。脚本不负责新增视觉对象、修复引用或验证 PBIR schema。

`compare` 按 part 路径比较解码 payload 的 SHA-256；JSON 排序规范化，文本/二进制按原字节。相同退出码为 0，有差异为 1，输入错误为 2。比较仅覆盖 payload，不比较定义外层元数据；差异输出可能含私有 part 路径，分享日志前需脱敏。

## 部署与读回：会修改远端

先按 [CLI 路线](../../docs/03-fabric/cli-pbir.md) 完成备份、模型门槛及候选审阅，再执行：

```bash
python3 scripts/fabric/fabric_definition.py update reports \
  --workspace "${WORKSPACE_ID}" --item "${REPORT_ID}" \
  --input "${PRIVATE_DIR}/report-candidate.json" \
  --baseline "${PRIVATE_DIR}/report-before.json" \
  --readback "${PRIVATE_DIR}/report-readback.json"
```

提交前会重新读取远端并比较 baseline，发现 payload 变化就停止。检查与提交之间仍可能发生并发修改，不能替代协作锁或变更窗口。应使用与该目标对应的最新 baseline；脚本不会从文件推断它属于哪个目标。

脚本提交完整 definition，按同源 operation 标识轮询，更新完成后独立 getDefinition 并保存读回。默认请求超时为六十秒、轮询总时限为三十分钟，可由 `--timeout` / `--poll-timeout` 调整。拒绝跟随 HTTP 重定向，不输出访问令牌、API 响应正文或认证 stderr。

异常时不自动重试提交或回滚；尤其是提交超时，先从私有服务记录检查是否已执行。读回有差异时退出码为 2，需要审阅服务端规范化或内容变化；部署成功也要额外验证模型处理、数据、页面交互及导出。

回滚使用原定义作为 input、当前最新定义作为 baseline，选择全新的 readback 路径；先报表再模型。脚本不备份或恢复数据、凭据、容量、连接或排程。
