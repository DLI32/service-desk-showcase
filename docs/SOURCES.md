# 来源、证据与脱敏边界

仅依据下列指定本地材料逐份整理，没有读取它们引用的其他文件，也没有联网验证。表内文件名仅用于追溯，不收录原件。

| 代号 | 来源文件 |
|---|---|
| S1 | aliyun-ivr-spec-2026-11-11.md |
| S2 | 阿里云云联络中心IVR建造复盘-2026-11-12.md |
| S3 | 电话SLA-API自动刷新复盘-2026-11-13.md |
| S4 | jsm-sla-lifecycle-retrospective.md |
| S5 | RawData选段导出-联动实现总结.md |
| S6 | codex-cli-optimize.md |
| S7 | jsm-sla-showcase/SPEC.md |
| S8 | fabric_definition.py（原脚本，只参考思路） |
| S9 | patch_pbir.py（原脚本，只参考思路） |

## 输出与来源映射

| 输出 | 来源与整理范围 |
|---|---|
| README.md | S1–S9 的架构、用途与证据边界 |
| docs/01-aliyun-contact-center/ivr-guide.md | S1 话术和目标；S2 最终实现及验证 |
| docs/01-aliyun-contact-center/telephony-sla-api.md | S3 指标、刷新和排错；S2 电话入口背景 |
| docs/02-jira-jsm/sla-showcase.md | S7 设计规格；S4 生命周期中记录的 SLA 遗留；S6 较晚演示快照 |
| docs/02-jira-jsm/lifecycle-monitor.md | S4 数据模型、口径和验收 |
| docs/02-jira-jsm/csat.md | S6 指标及日期筛选要求；采集配置证据不足，明确保留缺口 |
| docs/02-jira-jsm/automation.md | S4 邮件、窗口法、自动关闭和自动填组 |
| docs/03-fabric/cli-pbir.md | S6 实施草稿；S8 长操作修正；S9 尚未实际补丁的状态；S5 选段导出 |
| docs/03-fabric/date-slicers.md | S6 模型与切片器方案；S8–S9 后续阻塞状态 |
| docs/03-fabric/trial-archive.md | S2–S4 到期与排程；S6 备份与回滚边界 |
| scripts/fabric/fabric_definition.py | S6、S8 思路重写；增加独立子命令、参数化、基线检查和受限错误输出 |
| scripts/fabric/patch_pbir.py | S6、S9 思路重写；参数校验、原值匹配、未改 payload 保持 |
| scripts/fabric/README.md | S6、S8–S9 加上本次脚本的实际参数 |
| LICENSE | 本次新增标准 MIT 文本，权利人标为项目贡献者 |
| .gitignore | 本次新增 Python、系统、私有配置与备份排除规则 |
| docs/SOURCES.md | 本次整理的来源映射与脱敏说明 |

## 脱敏规则

共处理八类信息，实际内容按上下文替换为占位符或直接省略：

1. 邮箱及收件身份 → `<EMAIL>`、`<COORDINATOR_EMAIL>`。
2. 电话、测试呼入、分机及白名单尾号 → `<PHONE>`、`<TEST_NUMBER>`；不保留局部号码。
3. 密钥、访问令牌、密码及访问密钥标识 → `<SECRET_REF>` 等；不保留任何真实值。
4. 云账号、登录名、RAM 身份、租户及组织标识 → `<ALIYUN_ACCOUNT>` 等。
5. 实例、工作区、报表、模型、Notebook、调度和流程标识 → 语义占位符。
6. Jira 站点、工单系统地址及个人域名 → `<JIRA_SITE_URL>`；不保留原域名。
7. 通话标识、工单键、自定义字段及页面/视觉对象标识 → 语义字段名或占位符，不保留真实对象编号。
8. 支持工单、订单、坐席工号、个人路径和实名主体信息 → 删除或泛化。

另一云平台的账号相关材料及对照内容本次全部省略。没有打包原始文件、报表定义备份、PDF 或截图。保留服务公共 API 地址、品牌、通用表名、日期、话术、指标和算法。

## 需要使用者复核的证据边界

- S7 同时写了 141 与 142 的样本总数；仅保留明确的 95/141 算式，不推断另一个数字含义。
- S4 的 82 单与 S6 的 87 单是不同快照；生命周期邮件 81 单包含待关闭项，与打开 76 单的集合不同。
- S6 是未实施方案；S9 明确记录模型门槛尚未通过。日期路线与 PBIR 补丁不能当作成功实施报告。
- CSAT 只有快照指标，邀请、采集和特殊状态处理需在自己的环境验证。
- 权限、免费额度、试用宽限和删除政策未经本次实时核实；需要部署时按实际环境复核。

## 截图来源

三张报表截图于 2026-11-15 在 Fabric 阅读视图截取（电话 SLA、JSM 看板总览、CSAT 与 VoC 分析），已逐张检查：不含邮箱、电话号码、个人姓名与真实通话标识。图片存于 docs/assets/。
