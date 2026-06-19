"""
Base Agent - 数字员工基类
所有数字员工都继承自这个基类
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

from ..config import AgentConfig, CompanyConfig


class BaseAgent:
    """
    数字员工基类
    封装了Agent的通用能力：
    - 与LLM交互
    - 工具调用
    - 记忆管理
    - 状态追踪
    """
    
    def __init__(self, config: AgentConfig, company_config: CompanyConfig):
        self.config = config
        self.company_config = company_config
        self.provider = None
        self.model_client = None
        self.memory = None
        self.tool_results: List[Dict] = []
        self.conversation_history: List[Dict] = []
        
    async def initialize(self):
        """初始化Agent，建立与LLM的连接"""
        # 根据配置选择provider
        provider_name = self.config.provider or self.company_config.default_provider
        provider_config = self.company_config.providers.get(provider_name)
        
        if not provider_config:
            provider_config = self.company_config.providers.get("ollama")
        
        # 创建模型客户端
        self.model_client = await self._create_model_client(provider_config)
        
        # 初始化工具
        self.tools = await self._init_tools()
        
    async def _create_model_client(self, provider_config):
        """创建模型客户端"""
        # 支持多种provider
        if provider_config.provider_type == "ollama":
            try:
                from agent_framework.providers.ollama import OllamaClient
                return OllamaClient(
                    endpoint=provider_config.endpoint,
                    model=provider_config.default_model,
                )
            except ImportError:
                # Fallback: 使用简单的HTTP客户端
                return await self._create_simple_ollama_client(provider_config)
        
        elif provider_config.provider_type == "openai":
            from agent_framework.providers.openai import OpenAIClient
            return OpenAIClient(
                api_key=provider_config.api_key,
                model=provider_config.default_model,
            )
        
        else:
            # 默认使用简单实现
            return await self._create_simple_ollama_client(provider_config)
    
    async def _create_simple_ollama_client(self, provider_config):
        """创建简单的Ollama客户端（不依赖agent-framework）"""
        import aiohttp
        
        class SimpleOllamaClient:
            def __init__(self, endpoint: str, model: str):
                self.endpoint = endpoint
                self.model = model
                self.session = None
            
            async def __aenter__(self):
                self.session = aiohttp.ClientSession()
                return self
            
            async def __aexit__(self, *args):
                if self.session:
                    await self.session.close()
            
            async def complete(self, prompt: str, **kwargs) -> str:
                """调用Ollama API"""
                if not self.session:
                    self.session = aiohttp.ClientSession()
                
                async with self.session.post(
                    f"{self.endpoint}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    result = await resp.json()
                    return result.get("response", "")
            
            async def close(self):
                if self.session:
                    await self.session.close()
        
        return SimpleOllamaClient(
            endpoint=provider_config.endpoint or "http://localhost:11434",
            model=self.config.model or provider_config.default_model,
        )
    
    async def _init_tools(self) -> List[Dict]:
        """初始化工具集"""
        tools = []
        for tool_name in self.config.tools:
            tool = self._get_tool_implementation(tool_name)
            if tool:
                tools.append(tool)
        return tools
    
    def _get_tool_implementation(self, tool_name: str) -> Optional[Dict]:
        """获取工具实现"""
        # 内置工具映射
        built_in_tools = {
            "web_search": {
                "name": "web_search",
                "description": "搜索互联网获取信息",
                "parameters": {
                    "query": {"type": "string", "description": "搜索关键词"}
                },
            },
            "file_write": {
                "name": "file_write",
                "description": "写入文件",
                "parameters": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
            },
            "git": {
                "name": "git",
                "description": "执行Git命令",
                "parameters": {
                    "command": {"type": "string"},
                },
            },
            "code_editor": {
                "name": "code_editor",
                "description": "编写和编辑代码",
                "parameters": {
                    "file_path": {"type": "string"},
                    "code": {"type": "string"},
                    "operation": {"type": "string", "enum": ["create", "update", "delete"]},
                },
            },
        }
        return built_in_tools.get(tool_name)
    
    async def load_memory(self, memory_system):
        """加载记忆系统"""
        self.memory = memory_system
        if self.memory:
            # 加载该Agent的历史记忆
            self.conversation_history = await self.memory.recall(
                f"agent_{self.config.name}"
            )
    
    async def execute(self, task: str) -> "TaskResult":
        """执行任务"""
        from ..company import TaskResult
        
        start_time = time.time()
        
        try:
            # 确保已初始化
            if not self.model_client:
                await self.initialize()
            
            # 构建提示词
            prompt = self._build_prompt(task)
            
            # 调用LLM
            if hasattr(self.model_client, 'complete'):
                response = await self.model_client.complete(prompt)
            else:
                # 兼容不同的client接口
                response = await self.model_client.chat([{"role": "user", "content": prompt}])
            
            duration = time.time() - start_time
            
            return TaskResult(
                success=True,
                output=response,
                agent_name=self.config.name,
                duration=duration,
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TaskResult(
                success=False,
                error=str(e),
                agent_name=self.config.name,
                duration=duration,
            )
    
    def _build_prompt(self, task: str) -> str:
        """构建完整的提示词"""
        system_prompt = f"""你是{self.config.chinese_name}（{self.config.name}）。

## 角色定义
{self.config.instructions}

## 核心目标
{self.config.goal}

## 部门
{self.config.department}

## 指示
1. 始终以{self.config.chinese_name}的身份回答
2. 运用你的专业知识提供最有价值的输出
3. 如果需要执行操作，使用JSON格式的工具调用
4. 回答要简洁、专业、有洞见
"""
        
        # 如果有记忆，附加上下文
        context = ""
        if self.conversation_history:
            context = f"\n\n## 历史上下文\n你之前已经处理过相关任务，以下是历史记录：\n"
            for h in self.conversation_history[-3:]:
                context += f"- {h}\n"
        
        return f"{system_prompt}{context}\n\n## 当前任务\n{task}"
    
    async def call_tool(self, tool_name: str, parameters: Dict) -> Any:
        """调用工具"""
        # 实现工具调用逻辑
        # 这里可以接入MCP服务器
        pass
    
    async def shutdown(self):
        """关闭Agent，释放资源"""
        if self.model_client and hasattr(self.model_client, 'close'):
            await self.model_client.close()
        self.tool_results.clear()
