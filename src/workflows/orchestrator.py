"""
Workflow Orchestrator - 工作流编排器
根据任务意图选择合适的工作流并执行
"""

import asyncio
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

from ..company import TaskResult
from ..config import CompanyConfig


class BaseWorkflow(ABC):
    """工作流基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, agents: List, task: str) -> TaskResult:
        """执行工作流"""
        pass


class SequentialWorkflow(BaseWorkflow):
    """
    顺序工作流
    Agent按顺序一个接一个执行
    """
    
    def __init__(self, steps: List[Dict]):
        super().__init__("sequential", "顺序执行工作流")
        self.steps = steps  # [{"agent": agent, "task": "任务描述"}]
    
    async def execute(self, agents: List, task: str) -> TaskResult:
        """顺序执行"""
        results = []
        start_time = asyncio.get_event_loop().time()
        
        for step in self.steps:
            agent = step.get("agent")
            step_task = step.get("task", task)
            
            if agent:
                result = await agent.execute(step_task)
                results.append(result)
                
                if not result.success:
                    return TaskResult(
                        success=False,
                        error=f"步骤 {step['name']} 失败: {result.error}",
                        agent_name=self.name,
                        duration=asyncio.get_event_loop().time() - start_time,
                    )
        
        # 汇总结果
        summary = "\n\n".join([
            f"**{r.agent_name}**: {r.output}"
            for r in results if r.success
        ])
        
        return TaskResult(
            success=True,
            output=summary,
            agent_name=self.name,
            duration=asyncio.get_event_loop().time() - start_time,
        )


class ParallelWorkflow(BaseWorkflow):
    """
    并行工作流
    多个Agent同时执行任务
    """
    
    def __init__(self, agents: List, task_key: str = "task"):
        super().__init__("parallel", "并行执行工作流")
        self.agents = agents
        self.task_key = task_key
    
    async def execute(self, agents: List, task: str) -> TaskResult:
        """并行执行"""
        # 使用所有传入的agents并行执行
        coroutines = [agent.execute(task) for agent in (agents or self.agents)]
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # 处理结果
        valid_results = [r for r in results if isinstance(r, TaskResult) and r.success]
        failed = [r for r in results if isinstance(r, Exception)]
        
        if failed:
            error_msg = "\n".join([str(e) for e in failed])
            return TaskResult(
                success=False,
                error=f"部分任务失败: {error_msg}",
                agent_name=self.name,
            )
        
        summary = "\n\n".join([
            f"**{r.agent_name}**: {r.output}"
            for r in valid_results
        ])
        
        return TaskResult(
            success=True,
            output=summary,
            agent_name=self.name,
        )


class HandoffWorkflow(BaseWorkflow):
    """
    交接工作流
    Agent之间进行任务交接，类似真实公司的转交流程
    """
    
    def __init__(self, handoffs: List[Dict]):
        # handoffs: [{"from": agent1, "to": agent2, "task": "转交时的任务描述"}]
        super().__init__("handoff", "交接执行工作流")
        self.handoffs = handoffs
    
    async def execute(self, agents: List, task: str) -> TaskResult:
        """执行交接"""
        current_task = task
        results = []
        
        for handoff in self.handoffs:
            from_agent = handoff.get("from")
            to_agent = handoff.get("to")
            handoff_task = handoff.get("task", current_task)
            
            if from_agent:
                result = await from_agent.execute(handoff_task)
                results.append(result)
                current_task = result.output  # 将结果传递给下一个Agent
            
            if to_agent:
                # 接收方根据上一方结果继续执行
                result = await to_agent.execute(current_task)
                results.append(result)
        
        summary = "\n\n".join([
            f"**{r.agent_name}**: {r.output[:500]}..."
            for r in results if r.success
        ])
        
        return TaskResult(
            success=True,
            output=summary,
            agent_name=self.name,
        )


class GroupCollaborationWorkflow(BaseWorkflow):
    """
    群体协作工作流
    类似MetaGPT的软件公司模式：PM -> Architect -> Engineer
    """
    
    def __init__(
        self,
        roles: List[Dict],
        # roles: [
        #   {"role": "PM", "agent": agent, "task": "任务"},
        #   {"role": "Architect", "agent": agent, "task": "任务"},
        # ]
    ):
        super().__init__("group", "群体协作工作流")
        self.roles = roles
    
    async def execute(self, agents: List, task: str) -> TaskResult:
        """执行群体协作"""
        context = {"original_task": task, "shared_knowledge": {}}
        
        for role_info in self.roles:
            role_name = role_info.get("role", "Unknown")
            agent = role_info.get("agent")
            role_task = role_info.get("task", "{task}").format(**context)
            
            if agent:
                # 执行前更新Agent上下文
                result = await agent.execute(role_task)
                
                if not result.success:
                    return TaskResult(
                        success=False,
                        error=f"{role_name} 失败: {result.error}",
                        agent_name=self.name,
                    )
                
                # 将结果加入共享知识
                context["shared_knowledge"][role_name] = result.output
        
        # 汇总所有角色的输出
        summary_parts = []
        for role_name, output in context["shared_knowledge"].items():
            summary_parts.append(f"**{role_name}**:\n{output}")
        
        return TaskResult(
            success=True,
            output="\n\n".join(summary_parts),
            agent_name=self.name,
        )


class ConditionalWorkflow(BaseWorkflow):
    """
    条件工作流
    根据条件选择不同的执行路径
    """
    
    def __init__(self, branches: List[Dict], default_workflow: Optional[BaseWorkflow] = None):
        # branches: [{"condition": lambda x: x > 5, "workflow": workflow}]
        super().__init__("conditional", "条件路由工作流")
        self.branches = branches
        self.default_workflow = default_workflow
    
    async def execute(self, agents: List, task: str) -> TaskResult:
        """根据条件执行"""
        # 简单实现：检查任务关键词
        task_lower = task.lower()
        
        for branch in self.branches:
            condition = branch.get("condition")
            workflow = branch.get("workflow")
            
            if condition and workflow:
                if condition(task_lower):
                    return await workflow.execute(agents, task)
        
        # 默认执行
        if self.default_workflow:
            return await self.default_workflow.execute(agents, task)
        
        return TaskResult(
            success=False,
            error="没有匹配的工作流",
            agent_name=self.name,
        )


class WorkflowOrchestrator:
    """
    工作流编排器
    根据任务意图选择最合适的工作流
    """
    
    # 预定义工作流模板
    WORKFLOW_TEMPLATES = {
        "market_research": {
            "class": SequentialWorkflow,
            "steps": [
                {"name": "调研", "task": "进行市场调研"},
                {"name": "分析", "task": "分析数据并产出报告"},
                {"name": "策略", "task": "制定营销策略"},
            ],
        },
        "product_development": {
            "class": GroupCollaborationWorkflow,
            "roles": [
                {"role": "产品经理", "task": "分析需求，产出PRD"},
                {"role": "架构师", "task": "设计技术方案"},
                {"role": "工程师", "task": "开发实现"},
            ],
        },
        "content_creation": {
            "class": SequentialWorkflow,
            "steps": [
                {"name": "策划", "task": "制定内容策划方案"},
                {"name": "创作", "task": "创作内容"},
                {"name": "审核", "task": "审核优化内容"},
            ],
        },
        "data_analysis": {
            "class": ParallelWorkflow,
            "task_key": "数据分析任务",
        },
    }
    
    def __init__(self, config: CompanyConfig):
        self.config = config
        self.workflows: Dict[str, BaseWorkflow] = {}
        self._register_default_workflows()
    
    def _register_default_workflows(self):
        """注册默认工作流"""
        for name, template in self.WORKFLOW_TEMPLATES.items():
            if template["class"] == SequentialWorkflow:
                self.workflows[name] = template["class"](template.get("steps", []))
            elif template["class"] == GroupCollaborationWorkflow:
                self.workflows[name] = template["class"](template.get("roles", []))
            elif template["class"] == ParallelWorkflow:
                self.workflows[name] = template["class"](
                    agents=[],  # 动态传入
                    task_key=template.get("task_key", "task"),
                )
    
    def select_workflow(self, intent: Dict) -> BaseWorkflow:
        """根据意图选择工作流"""
        keywords = intent.get("task_keywords", [])
        departments = intent.get("departments", [])
        intent_type = intent.get("intent_type", "general")
        
        # 基于关键词选择
        if any(k in keywords for k in ["市场", "调研", "分析", "research"]):
            return self.workflows.get("market_research", SequentialWorkflow([]))
        
        if any(k in keywords for k in ["开发", "产品", "开发", "develop"]):
            return self.workflows.get("product_development", GroupCollaborationWorkflow([]))
        
        if any(k in keywords for k in ["内容", "文案", "content", "write"]):
            return self.workflows.get("content_creation", SequentialWorkflow([]))
        
        if any(k in keywords for k in ["数据", "分析", "data", "analytics"]):
            return self.workflows.get("data_analysis", ParallelWorkflow([]))
        
        # 基于部门选择
        if "Engineering" in departments and "Marketing" in departments:
            return self.workflows.get("product_development", GroupCollaborationWorkflow([]))
        
        if len(departments) > 1:
            # 多部门协作使用群体协作模式
            return GroupCollaborationWorkflow([
                {"role": dept, "task": f"执行{dept}相关任务"}
                for dept in departments
            ])
        
        # 默认顺序执行
        return SequentialWorkflow([])
    
    def register_workflow(self, name: str, workflow: BaseWorkflow):
        """注册自定义工作流"""
        self.workflows[name] = workflow
    
    def get_available_workflows(self) -> List[str]:
        """获取所有可用工作流"""
        return list(self.workflows.keys())
