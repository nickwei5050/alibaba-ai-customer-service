# 禁止承诺规则 + 报价拆分规则(对客安全底线)

这些规则与 `src/stargo/entity/rules.py` 的确定性检查相对应。`risk_controller`
会强制执行:凡命中以下话题,一律转人工(Nick)确认,不自动发送。

## 报价拆分(硬性结构)
任何报价必须拆分为:

```
Bare vehicle price      裸车价
+ Battery price         电池价
= Total EXW factory price   出厂总价
```

之后才谈运费:**Exact shipping cost requires destination country, destination
port, quantity and battery type.**

## 没有以下信息,不允许生成最终运费 / CIF 报价
- 客户国家 (destination country)
- 目的港 (destination port)
- 数量 (quantity)
- 电池配置 (battery option / chemistry / voltage)

缺任一项 → 只能**引导客户补充信息**,不得给出运费或 CIF 数字。

## 绝不自动做(一律转人工)
最终报价 · FOB/CIF 价 · 运费金额 · 折扣/降价 · 经销/代理/独家合作 · 付款条款 ·
交期承诺 · 证书保证 · 清关承诺 · 售后赔偿 · 客户投诉处理。

## 绝不编造
- 不编造价格(仅 Nick 确认后的价格可用)
- 不编造运费
- 不承诺未持有的认证(只说 STARGO 实际持有的证)
- 不承诺清关
- 不许诺比市场更快的交期
- 不自动答应独家/代理(须 Nick + 律师确认)

## 价格沟通纪律
- **Never send just a number** — 但本系统更进一步:**价格一律转人工**。
- 永远不要直接降价;用规格调整 / 批量 / 账期回应"价格太高"。
- 内部成本价、利润系数、加价公式**绝不写入对客回复**。

## 诈骗红旗(命中则提醒人工核查)
大单+零细节 · 大单要 PayPal · LC 软条款 · 拒透露公司信息 · 收货地址≠付款方。

> source: Notion 报价模板(internal_only)/ 询盘 SOP / 认证矩阵
