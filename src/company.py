"""
Digital Company Core - 数字公司核心引擎
负责协调多个数字员工完成复杂任务
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from .config import CompanyConfig, AgentConfig
from .agents.router import Router
from .memory.company_memory import CompanyMemory
from .workflows.orchestrator import WorkflowOrchestrator


class TaskResult:
    """任务执行结果"""
    def __init__(
        self,
        success: bool,
        output: Any = None,
        error: Optional[str] = None,
        agent_name: Optional[str] = None,
        duration: float = 0,
    ):
        self.success = success
        self.output = output
        self.error = error
        self.agent_name = agent_name
        self.duration = duration
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "agent": self.agent_name,
            "duration": self.duration,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def __str__(self) -> str:
        if self.success:
            return f"✅ {self.agent_name} 完成 ({self.duration:.1f}s):\n{self.output}"
        else:
            return f"❌ {self.agent_name} 失败:\n{self.error}"


class DigitalCompany:
    """
    数字公司核心类
    管理所有数字员工的生命周期和任务协调
    """
    
    def __init__(self, config: CompanyConfig):
        self.config = config
        self.name = config.company_name
        self.router = Router(config)
        self.memory = CompanyMemory(config)
        self.orchestrator = WorkflowOrchestrator(config)
        self.agents: Dict[str, Any] = {}
        self.task_history: List[TaskResult] = []
        
    async def start(self):
        """启动数字公司"""
        print(f"🏢 {self.name} 启动中...")
        
        # 初始化所有数字员工
        for agent_config in self.config.agents:
            await self._init_agent(agent_config)
            print(f"   ✓ {agent_config.chinese_name} ({agent_config.name}) - 就绪")
        
        print(f"\n📊 数字公司概况:")
        print(f"   - 员工总数: {len(self.agents)} 人")
        print(f"   - 部门: {set(a.department for a in self.config.agents)}")
        print()
    
    async def _init_agent(self, config: AgentConfig):
        """初始化单个数字员工"""
        # 延迟导入，避免循环依赖
        from .agents.base import BaseAgent
        
        agent = BaseAgent(config, self.config)
        self.agents[config.name] = agent
        
        # 如果启用了记忆，加载历史记忆
        if config.memory_enabled:
            await agent.load_memory(self.memory)
    
    async def execute(self, command: str) -> str:
        """
        执行CEO指令
        核心入口：分析任务 -> 路由到合适的Agent/Workflow -> 执行 -> 返回结果
        """
        print(f"\n🎯 CEO指令: {command}")
        
        # 1. 理解任务意图
        intent = await self.router.understand_intent(command)
        print(f"📌 任务分析: {intent}")
        
        # 2. 选择执行策略
        if intent["requires_multiple_agents"]:
            # 多Agent协作 -> 使用工作流
            return await self._execute_workflow(command, intent)
        elif intent["agent_type"]:
            # 单Agent执行
            return await self._execute_single(command, intent)
        else:
            # 简单任务 -> CEO助理直接处理
            return await self._execute_assistant(command)
    
    async def _execute_single(self, command: str, intent: Dict) -> str:
        """单Agent执行"""
        agent_name = intent["agent_type"]
        agent = self.agents.get(agent_name)
        
        if not agent:
            return f"❌ 找不到员工: {agent_name}"
        
        print(f"👤 分配给: {agent.config.chinese_name}")
        result = await agent.execute(command)
        
        self.task_history.append(result)
        
        # 存入记忆
        if agent.config.memory_enabled:
            await self.memory.store(
                key=f"task_{result.timestamp.isoformat()}",
                value=result.to_dict(),
            )
        
        return str(result)
    
    async def _execute_workflow(self, command: str, intent: Dict) -> str:
        """多Agent协作工作流执行"""
        departments = intent["departments"]
        
        print(f"👥 启动多部门协作: {departments}")
        
        # 选择合适的工作流
        workflow = self.orchestrator.select_workflow(intent)
        
        # 收集需要的Agent
        agents = []
        for dept in departments:
            dept_agents = self.config.get_agents_by_department(dept)
            for a in dept_agents:
                if a.name in self.agents:
                    agents.append(self.agents[a.name])
        
        print(f"📋 参与员工: {[a.config.chinese_name for a in agents]}")
        
        # 执行工作流
        result = await workflow.execute(agents, command)
        
        self.task_history.append(result)
        
        return str(result)
    
    async def _execute_assistant(self, command: str) -> str:
        """CEO助理直接处理简单任务"""
        # 使用所有Agent的集合智慧
        responses = await asyncio.gather(
            *[agent.execute(command) for agent in self.agents.values()],
            return_exceptions=True,
        )
        
        # 综合各方意见
        synthesis = self._synthesize_responses(command, responses)
        return synthesis
    
    def _synthesize_responses(self, command: str, responses: List) -> str:
        """综合多个Agent的响应"""
        valid_responses = [r for r in responses if isinstance(r, TaskResult) and r.success]
        
        if not valid_responses:
            return "❌ 暂时无法处理这个任务"
        
        # 简单拼接，后续可以优化为LLM综合
        result_parts = []
        for r in valid_responses[:3]:  # 最多取3个
            result_parts.append(f"**{r.agent_name}**: {r.output}")
        
        return "📊 多角度分析:\n\n" + "\n\n".join(result_parts)
    
    async def shutdown(self):
        """关闭数字公司"""
        print("🏢 数字公司关闭中...")
        
        # 保存所有记忆
        await self.memory.save_all()
        
        # 关闭所有Agent
        for agent in self.agents.values():
            await agent.shutdown()
        
        print("   ✓ 所有资源已释放")
    
    def get_status(self) -> Dict:
        """获取公司状态"""
        return {
            "name": self.name,
            "agents": {
                name: {
                    "status": "active",
                    "department": agent.config.department,
                    "memory_enabled": agent.config.memory_enabled,
                }
                for name, agent in self.agents.items()
            },
            "task_count": len(self.task_history),
            "memory_size": self.memory.size(),
        }
    
    def list_agents(self) -> List[str]:
        """列出所有Agent"""
        return [
            f"{a.config.chinese_name} ({a.config.name}) - {a.config.department}"
            for a in self.agents.values()
        ]
