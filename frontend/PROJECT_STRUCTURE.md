# 行政智能体管理系统 - 前端项目

基于 React 18 + TypeScript + Ant Design + Vite + Zustand 构建的现代化管理系统前端。

## 技术栈

- **框架**: React 18
- **语言**: TypeScript
- **构建工具**: Vite
- **UI组件库**: Ant Design 5 + Ant Design Pro Components
- **状态管理**: Zustand
- **路由**: React Router DOM 7
- **HTTP客户端**: Axios
- **数据请求**: TanStack Query (React Query)
- **图表**: ECharts
- **拖拽**: dnd-kit

## 项目结构

```
src/
├── assets/          # 静态资源
│   ├── images/      # 图片资源
│   └── styles/      # 全局样式
├── components/      # 通用组件
│   ├── Loading.tsx
│   └── PrivateRoute.tsx
├── constants/       # 常量定义
│   └── index.ts
├── hooks/          # 自定义Hooks
├── layouts/        # 布局组件
│   └── BasicLayout.tsx
├── pages/          # 页面组件
│   ├── Dashboard.tsx
│   └── Login.tsx
├── services/       # API服务
│   └── auth.ts
├── stores/         # Zustand状态管理
│   ├── app.ts
│   ├── auth.ts
│   └── index.ts
├── types/          # TypeScript类型定义
│   └── index.ts
├── utils/          # 工具函数
│   ├── http.ts
│   └── index.ts
├── App.tsx         # 根组件
├── main.tsx        # 入口文件
└── vite-env.d.ts   # Vite环境变量类型
```

## 开发指南

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

### 代码检查

```bash
npm run lint
```

## 环境变量

- `.env.development` - 开发环境配置
- `.env.production` - 生产环境配置

### 可用环境变量

- `VITE_API_BASE_URL` - API基础URL
- `VITE_APP_TITLE` - 应用标题

## 核心功能

### 1. 路由配置

使用 React Router DOM 7 进行路由管理，支持：
- 路由守卫（PrivateRoute）
- 嵌套路由
- 路由懒加载

### 2. 状态管理

使用 Zustand 进行状态管理：
- `useAuthStore` - 用户认证状态
- `useAppStore` - 应用全局状态

### 3. HTTP请求

封装的 HTTP 客户端特性：
- 自动添加认证token
- 统一错误处理
- 请求/响应拦截器
- TypeScript类型支持

### 4. 工具函数

- `storage` - 本地存储封装
- `formatDate` - 日期格式化
- `debounce` - 防抖
- `throttle` - 节流

## 代码规范

- 使用 ESLint 进行代码检查
- 使用 TypeScript 严格模式
- 遵循 React Hooks 规范
- 组件使用函数式组件

## 待完成功能

以下功能将由 frontend-dev 完成：

1. Ant Design 主题配置
2. Zustand 持久化配置优化
3. 通用组件封装（表格、表单、弹窗等）
4. 侧边栏导航菜单
5. 顶部导航栏
6. 用户管理页面
7. 系统设置页面

## 注意事项

1. 所有API请求都会自动添加 `/api` 前缀
2. 开发环境下API请求会代理到 `http://localhost:8000`
3. 使用路径别名 `@` 指向 `src` 目录
4. 所有页面组件应放在 `pages` 目录
5. 可复用组件应放在 `components` 目录