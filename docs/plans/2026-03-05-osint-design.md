# Tobacco Situation Monitor V0.1 设计文档（全国案件动态 OSINT）

## 1. 目标与范围

### 1.1 目标
在 **2 周内**交付可运行的 V0.1：每小时自动监测全国公开网页中的烟草案件动态，生成结构化线索并支持人工复核与基础告警。

### 1.2 范围内（In Scope）
- 仅采集公开网页（新闻/通报/公告）
- 全国范围烟草相关网站（先从省级/地市级官网开始）
- 每小时调度抓取
- 规则驱动识别“案件动态”
- 基础风险分级（高/中/低）
- 看板查询与人工复核

### 1.3 范围外（Out of Scope）
- 登录区、付费内容、非公开数据
- 个人隐私数据深度采集
- 复杂网络关系图谱与高级模型推理
- 全自动执法决策（仅做线索支持）

---

## 2. 架构设计

采用 **四层架构**，优先保证稳定采集和可解释性：

1. **Source Registry（源管理）**  
   维护站点、栏目 URL、解析规则、健康状态。

2. **Ingestion Pipeline（采集管道）**  
   定时调度 → 列表抓取 → 详情抓取 → 清洗 → 去重入库。

3. **Intel Engine（情报引擎）**  
   关键词/正则分类、案件类型标签、风险打分。

4. **Ops Dashboard（运营看板）**  
   线索浏览、筛选、统计、告警记录、人工复核。

**设计原则**：先做“可跑、可查、可复核”，再逐步增强智能化。

---

## 3. 模块拆分与数据流

### 3.1 核心模块
- `source_manager`：源站配置、启停、健康监控
- `scheduler`：每小时任务触发
- `fetcher`：列表页/详情页抓取（超时、重试）
- `parser`：标题、时间、正文、来源抽取
- `deduper`：URL Hash + Content Hash 去重
- `classifier`：是否案件动态 + 案件类型标签
- `scorer`：风险评分与分级
- `review_queue`：低置信度线索待人工确认
- `dashboard_api`：查询、统计、复核、告警 API

### 3.2 数据流
1. 调度器按小时拉起抓取任务
2. 按源站规则抓列表页，提取候选链接
3. 抓详情并清洗正文
4. 去重后写入原始文章表
5. 分类+打标签+打分生成线索
6. 高分触发告警，中低分进入复核队列
7. 复核结论反哺规则库

---

## 4. 数据模型（V0.1）

### 4.1 `sources`
- `id`
- `name`
- `region`
- `base_url`
- `list_url`
- `parser_type`
- `enabled`
- `last_crawled_at`
- `health_status`

### 4.2 `raw_articles`
- `id`
- `source_id`
- `url`
- `url_hash`
- `title`
- `published_at`
- `content_raw`
- `content_clean`
- `fetched_at`
- `content_hash`

### 4.3 `case_intels`
- `id`
- `article_id`
- `is_case_related`（bool）
- `case_type`
- `province`
- `city`
- `event_date`
- `keywords_hit`
- `risk_score`
- `risk_level`
- `status`（new/reviewed/ignored）
- `created_at`

### 4.4 `alerts`
- `id`
- `intel_id`
- `alert_type`
- `sent_to`
- `sent_at`
- `ack_status`

### 4.5 `review_logs`
- `id`
- `intel_id`
- `reviewer`
- `action`（confirm/reject/edit）
- `comment`
- `created_at`

---

## 5. API 草案

- `GET /api/intels`：按时间/省份/风险/案件类型筛选
- `GET /api/intels/:id`：线索详情（原文 + 结构化信息 + 告警记录）
- `POST /api/intels/:id/review`：人工复核提交
- `GET /api/dashboard/summary`：总览统计
- `POST /api/crawl/run`：手动触发采集（调试）
- `GET /api/sources/health`：源站健康状态

---

## 6. 异常处理

- 站点超时：重试 3 次，失败标记 degraded
- 解析失败：记录 `parse_error`，不阻塞全局
- 重复内容：URL+内容双重去重
- 误报控制：低置信度默认进入复核
- 任务堆积：单源隔离，避免拖垮整轮调度

---

## 7. 验收标准

- 每小时任务 24h 执行成功率 ≥ 95%
- 首批 30~50 源站稳定抓取
- 去重有效（明显重复不重复入线索）
- 案件识别人工抽检准确率 ≥ 75%
- 看板支持筛选、详情、复核、统计

---

## 8. 两周里程碑

- **D1-D2**：源站清单、规则模板、数据库初始化
- **D3-D5**：抓取/解析/去重链路贯通
- **D6-D8**：分类打分、告警、复核流
- **D9-D10**：看板 API + 前端首屏
- **D11-D12**：稳定性修复、回归抽检
- **D13-D14**：试运行、参数调优、V0.1 发布

---

## 9. 后续演进（V0.2+）

- 混合方案：规则 + 大模型抽取
- 跨源事件聚类（同案多源合并）
- 地图热区与时间序列趋势
- 半自动规则学习与维护提示
