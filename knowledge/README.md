# STARGO 知识库(项目本地副本)

本目录是 AI 客服大脑的检索源,内容**镜像自你的 Notion 外贸知识库**(2026-06-03 源)。
`knowledge.obsidian_path` 默认指向本目录。检索器按第一层文件夹作为 category。

> 数据口径:价格、认证、交期、装柜数、Warranty 条款等任何**对客引用前必须 Nick 人工确认**。
> 本系统的 `risk_controller` 会强制把含价格/运费/认证/交期/代理/付款的回复转人工。

## 目录结构

```
company/   公司介绍、企业核心事实卡(合同主体、产品矩阵、贸易条款)
products/  产品分类 + 63 款车型总表
battery/   电压/电池化学配置、电池质保
prices/    报价说明(⚠️ 具体出厂价为内部数据,默认不入库 —— 见 prices/README.md)
shipping/  港口/陆口、交期、MOQ、锂电海运危险品合规
export/    各国认证矩阵(目的国强制认证 + STARGO 持证情况)
sample/    MOQ 与样品政策
scripts/   询盘回复 SOP(13 场景)、经销商/代理话术
faq/       认证与质保常见问答
rules/     禁止承诺规则 + 报价拆分规则(对客安全底线)
```

## 同步来源
- Notion:STARGO 外贸知识库 `374ceb31-d667-813d-9f82-e81595cf3a01`
- 原始:本地 Obsidian `STARGO_RAG_外贸知识库工作区`

> 本副本仅含**对客可用**的资料 + 安全规则。完整 63 车型详细参数、内部成本价、
> 利润系数等仍以 Notion 为准,按需同步。
