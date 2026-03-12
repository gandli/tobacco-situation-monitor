# Tobacco Situation Monitor - Web Frontend

烟草执法态势感知系统前端 - React + TypeScript + Tailwind CSS

## 技术栈

- **框架**: React 19 + TypeScript 5.9
- **构建工具**: Vite 7
- **样式**: Tailwind CSS 4
- **图表**: Recharts
- **路由**: React Router 7
- **图标**: Lucide React

## 功能模块

### 仪表板 (Dashboard)
- 统计卡片展示关键指标
- 趋势分析图表
- 平台分布统计
- 最近线索列表

### 线索管理 (Clues)
- 线索列表浏览
- 多维度筛选（平台、风险等级、状态）
- 线索详情查看
- 风险评分可视化

### 案件管理 (Cases)
- 案件详情展示
- 证据材料管理
- 涉案方信息
- 处置时间线

### 关系图谱 (Graph)
- 商家-物流-人员关联可视化
- 节点交互
- 关系类型说明

## 开发指南

### 环境要求
- Node.js 20+
- npm 10+

### 安装依赖
```bash
npm install
```

### 本地开发
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 代码检查
```bash
npm run lint
```

## 部署

### Cloudflare Pages
项目已配置Cloudflare Pages部署：

1. 构建命令: `npm run build`
2. 输出目录: `dist`
3. Node.js版本: 20

### 手动部署
```bash
npm run build
# 将 dist 目录部署到任何静态托管服务
```

## 项目结构

```
src/
├── components/          # 可复用组件
│   ├── cases/          # 案件相关组件
│   ├── clues/          # 线索相关组件
│   ├── common/         # 通用组件
│   ├── dashboard/      # 仪表板组件
│   └── graph/          # 图谱组件
├── data/               # 模拟数据
├── pages/              # 页面组件
├── types/              # TypeScript类型定义
└── utils/              # 工具函数
```

## TypeScript 配置

项目启用严格的TypeScript配置：
- `strict: true`
- `noUnusedLocals: true`
- `noUnusedParameters: true`
- `noFallthroughCasesInSwitch: true`

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

MIT License