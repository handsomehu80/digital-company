# game-for-my-children 数字公司优化计划

## 项目概况

**仓库**: https://github.com/handsomehu80/game-for-my-children  
**技术栈**: React 18 + Vite + React-Three-Fiber + Zustand  
**游戏类型**: 儿童教育冒险游戏（海上探险 + 知识答题战斗）  
**Commits**: 151 次  
**分支**: 3 个

## 核心玩法

- 两个孩子在海洋世界中冒险
- 4个海洋区域（东、西、南、北）+ 神秘海洋
- **答题战斗系统**: 答对知识题减少怪物HP，答错减少玩家HP
- 渐进式难度设计
- Boss战 + 岛屿探索 + 宝箱系统

## 当前系统架构

```
src/
├── components/game/     # 游戏组件
│   ├── Battle/         # 战斗系统UI
│   ├── Ocean/          # 海洋/关卡组件
│   └── UI/             # HUD, 菜单, 对话框
├── game/               # 核心游戏逻辑
│   ├── BattleEngine.ts # 战斗引擎
│   ├── OceanWorld.ts   # 世界/地图逻辑
│   └── ExplorationStateMachine.ts # 探索状态机
├── data/               # 数据配置
│   ├── oceans/         # 海洋区域定义
│   ├── monsters/       # Boss怪物配置
│   └── questions/      # 题库（按难度分类）
├── store/              # Zustand状态管理
│   └── gameStore.ts    # 主游戏状态
└── tests/              # 测试
```

## 数字公司待完成的任务

### P0 - 核心功能

- [ ] **多人联机对战系统**
  - WebSocket 联机通信
  - 房间匹配系统
  - 实时同步游戏状态
  - 战斗同步机制
  
- [ ] **题库扩充系统**
  - 当前题库结构验证
  - 新题目录入流程
  - 难度分级系统优化
  - 题目类型扩展（选择/判断/填空/连线）

### P1 - 重要功能

- [ ] **存档同步服务**
  - 云端存档
  - 多设备同步
  - 家长控制面板
  
- [ ] **成就系统**
  - 成就定义配置化
  - 成就解锁条件
  - 成就展示界面
  
- [ ] **音效与音乐**
  - 背景音乐
  - 战斗音效
  - UI音效

### P2 - 优化建议

- [ ] 儿童确认面板优化（大按钮 + 重复提示）
- [ ] 色盲/视力障碍支持
- [ ] 隐藏岛屿微弱发光提示
- [ ] SVG加载性能优化

## 技术债务

### P0 问题 (已识别)

- [x] P0-1: answerIndex 边界未检查 → 已修复
- [x] P0-2: encounter 逻辑不一致 → 已修复
- [x] P0-3: useEffect 闭包问题 → 已修复
- [x] P0-4: 岛屿解锁状态未验证 → 已修复
- [x] P0-5: null/undefined 处理不足 → 已修复

### P1 问题 (已识别)

- [ ] P1-1: localStorage 容量限制 → 需要处理
- [ ] P1-2: 钥匙掉落概率公平性（保底机制）→ 需要实现
- [ ] P1-3: retryCount 混淆 → 需要统一
- [ ] P1-4: visit-to-unlock 规则明确 → 需要文档化
- [ ] P1-5: 传送门生成种子系统 → 需要实现

## 数字公司开发计划

### Phase 1: 基础设施 (1周)

```
第1天:
- [ ] 克隆 game-for-my-children 到 digital-company 工作目录
- [ ] 设置开发环境
- [ ] 搭建数字公司 CI/CD

第2-3天:
- [ ] 实现 MarketResearcher 分析竞品（其他儿童教育游戏）
- [ ] 实现 ProjectManager 拆解多人对战需求
- [ ] 产出详细的技术方案文档

第4-5天:
- [ ] FrontendEngineer 设计联机架构
- [ ] BackendEngineer 搭建 WebSocket 服务器
- [ ] QA 制定测试计划
```

### Phase 2: 多人对战系统 (2-3周)

```
第1周:
- [ ] 设计房间系统（创建/加入/匹配）
- [ ] 实现基础 WebSocket 通信
- [ ] 同步玩家位置

第2周:
- [ ] 同步战斗状态
- [ ] 实现观战系统
- [ ] 处理断线重连

第3周:
- [ ] 压力测试
- [ ] 安全性检查
- [ ] 部署上线
```

### Phase 3: 题库扩充 (1-2周)

```
- [ ] 实现题库 CMS
- [ ] 题目录入工作流
- [ ] 自动难度评估
- [ ] 题目类型扩展
```

## 推荐的工作流

### 多人对战开发工作流

```
1. ProjectManager (PM):
   - 拆解任务: 房间系统 → 匹配 → 同步 → 测试
   - 产出: PRD + 任务看板

2. FrontendEngineer:
   - 联机UI开发
   - 状态同步逻辑
   - 实时对战界面

3. BackendEngineer:
   - WebSocket 服务器
   - 房间状态管理
   - 数据同步协议

4. QAEngineer:
   - 联机测试用例
   - 性能测试
   - 红蓝对抗审查
```

## 资源链接

- [CLAUDE.md](https://github.com/handsomehu80/game-for-my-children/blob/main/CLAUDE.md)
- [Ocean Exploration Design](./docs/ocean-exploration-design.md)
- [题库设计文档](./docs/question-bank-redesign.md)
