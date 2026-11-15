# Automation 规则要点

来源：S4；都是当时项目级实践，不承诺适用于所有套餐与工作流。站点用 `<JIRA_SITE_URL>`，协调员收件人用 `<COORDINATOR_EMAIL>`。

## 提醒不破坏闲置证据

跟进提醒只发邮件，不加评论或提及；评论可能刷新 `updated`，让规则自己抹掉闲置证据。报表覆盖 Incident 与 Service request；首期提醒仅覆盖 Incident。

历史每天 09:00（Asia/Shanghai）运行六条规则：

| 规则 | 窗口/动作 |
|---|---|
| 每日协调员汇总 | 一封汇总所有需跟进问题单 |
| 我方闲置首提醒 | 一至两天，通知处理人 |
| 我方闲置升级 | 四至五天，通知处理人并抄送协调员 |
| 等客户首提醒 | 两至三天，通知处理人 |
| 等客户升级 | 五至六天，通知处理人并抄送协调员 |
| 自动关闭 | Resolved 满七天，转 Closed |

用半开窗口表达精确时间范围，例如：

```jql
project = "<PROJECT_KEY>"
AND status = "In Progress"
AND updated > -2d AND updated <= -1d
```

这只是一个状态的窗口示意。实际状态集合、类型名和终态排除条件先在搜索里验数。按天触发、updated 不变时，每档通常只命中一次；手动重跑、延迟、停机补跑可能重复或漏发，窗口法不提供持久去重保证。

自动关闭应按进入 Resolved 的时间核对满七天，不能未经验证就把 `updated` 当作解决时间。还要验证工作流允许转换、执行者权限、重开后的重新计时及运行审计；源材料只列了首跑计划，没有首跑成功证明。

## 分层汇总邮件

总口径 Lookup → 按状态分别 Lookup → 变量渲染 → 拼成一封 HTML 邮件。列为工单链接、摘要、处理人、闲置天数；链接由 `<JIRA_SITE_URL>` 与当前工单键构造。

- Resolved 往往已有 resolution，不要让全局 `resolution = Unresolved` 排除待关闭单。
- 当时变量中的 `{{#if}}` 导致整段空白，纯迭代模板可用；某段为空时显示零张与空表。
- 当时用 `{{updated.diff(now).days}}` 得到正的闲置天数；在目标环境先验证方向和单位。
- 经办人为空要明确表示“未分配”。摘要进入 HTML 前应采用模板引擎支持的转义方式。
- 审计 Success 不能证明邮件内容正确；实际查看到件、分段数、链接和正负天数。

## 按 Service 自动填解决组

开单时按 Service 路由 Assignment group。历史映射包括 M365 → Infra-M365、VPN → Infra-Network、Laptop → Infra-DeskSide、Citrix → Infra-Server、Workday → APP-Workday、Web App / Portal → APP-Web App。

Opening group 表示报障人所属组，Assignment group 表示解决责任组，两者不能互相替代。字段标识用 `<OPENING_GROUP_FIELD>`、`<ASSIGNMENT_GROUP_FIELD>`，不要复制别人的自定义字段编号。验证时看字段实际结果与工单历史中的自动化留痕。

配额与动作计费以目标环境为准，不照搬历史套餐数。先试运行、查邮件，再观察正常排程；仅修改规则配置不代表已经持续运行成功。
