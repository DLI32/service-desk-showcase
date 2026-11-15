# Fabric CLI 与 PBIR 管理路线

来源：S6、S8、S9；选段导出部分来源 S5。S6 是方案草稿，S8 记录部分修正。更新（2026-11-14）：模型与报表 updateDefinition 已在演示环境成功应用并读回比对通过（各推两次，0 差异），20 个日期切片器已上线；下文的流程步骤仍适用。

## 定义管理路线

1. 建立当前数据与筛选上下文的基线，导出模型、报表、Notebook 定义到仓库外。
2. 检查模型格式、兼容级别、存储模式与关系支持；先过模型门槛。
3. 本地只改明确 parts。TMDL 是定义格式，definition API 是传输接口，可以配合。
4. 部署前再次导出，与编辑起点比较，发现并发修改则合并后重验。
5. 提交完整 definition；只改局部不等于只提交部分 parts。
6. 长操作完成后独立读取结果；更新后再 getDefinition 读回，逐 part 比较。
7. 模型必要的处理/刷新及验数完成后再改报表；定义成功不代表数据已计算或页面正确。

通用命令模式：

```bash
fab api -X post "workspaces/${WORKSPACE_ID}/reports/${REPORT_ID}/getDefinition" -i '{"format":"PBIR"}'
```

`fab` 与 `az` 用自己的安装位置；同名命令可能来自其他工具，先确认可执行文件。通用重写脚本见 [scripts/fabric](../../scripts/fabric/README.md)，没有固定工作区或账号。

## 长操作与读回

历史响应的 Location 指向跳转主机，直接套用固定 API 地址检查会失败。重写脚本使用 `x-ms-operation-id` 在同一公共 API 源轮询；不会把访问令牌跟随到任意跳转地址。get 操作成功后取 `/result`，update 只等待完成，再发独立 get 读回。轮询超时不自动重提，先检查原操作状态。

哈希前对 JSON 规范化，对非 JSON 保持原字节。服务端可能补默认属性或规范化文本，差异需要检查，不自动回滚。

## PBIR 局部修改

| part 模式 | 用途 |
|---|---|
| definition/report.json | 报表配置与资源引用，优先保留 |
| definition/pages/pages.json | 页顺序，不增删页就不动 |
| definition/pages/<PAGE_ID>/page.json | 页面尺寸与背景 |
| definition/pages/<PAGE_ID>/visuals/<VISUAL_ID>/visual.json | 布局、样式、字段绑定与交互 |
| StaticResources/... | 主题、图标等资源；新增须进入 parts |

`patch_pbir.py` 只替换已存在且原值匹配的属性。计划中的 part 与 keys 必须来自自己的定义；它不生成切片器、不验证完整 PBIR schema，也不猜格式属性路径。

复制整个 visual 可能连带筛选、排序、钻取、同步组和交互。新增对象需要唯一名称、匹配路径、正确字段绑定并清理旧引用；复制切片器不等于跨页同步。

## Raw Data 选段导出

历史成功路线：日期切片器筛选工单键 → Power BI 按钮 → Power Automate → 参数化 Notebook → 两份 CSV。不是把开始/结束日期直接传给 Notebook，而是传当前选中的键集合，事件行同步按键过滤。

1. 在按钮 data 区先放工单键，再从视觉内嵌 Edit 创建流。
2. 检查触发器 schema 与真实点击正文，确认含 `Power BI values`。当时“创建时无字段”的旧流原地修复失败，最终换绑新流。
3. 在触发器后放 Apply to each，遍历 `triggerBody()?['entity']?['Power BI values']`；循环内读工单键，作为当时的 schema 锚定做法。
4. Select 提取键列表，再用 Compose 先构造完整请求体，HTTP Body 只引用其输出；避免直接拼含动态令牌的半成品 JSON。
5. POST 模式：`/v1/workspaces/<WORKSPACE_ID>/items/<NOTEBOOK_ID>/jobs/instances?jobType=RunNotebook`。

参数请求体模式：

```json
{"executionData":{"parameters":{"export_keys":{"value":"<SELECTED_KEYS>","type":"string"}}}}
```

Notebook 参数语义：空字符串为全量，逗号分隔键为指定集合，`__NONE__` 为合法空选段。空选段输出仅表头；解析失败或触发器缺字段必须失败，不能误变全量。公开项目不附带实际流定义或 CSV。

当时验收：选段十单产出十行验证数据与三十二行事件；全量十九行与七十行；空选段两文件仅表头。三种场景均应真点击验证。连接器曾在约一分钟后报错，但 Notebook 已成功执行；这是历史观测，不能将所有连接器失败都当作正常，须联合检查提交、Monitor、产物时间与行集。

回滚时先恢复报表，再恢复模型，避免报表引用已移除字段。定义备份不含数据、凭据或排程。导出链路应保留旧绑定与恢复步骤，并用全量点击复验。
