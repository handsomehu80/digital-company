"""
Digital Company Configuration
数字公司配置文件
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import yaml


class ProviderConfig(BaseModel):
    """模型提供商配置"""
    provider_type: str = "ollama"  # ollama, openai, azure_openai, anthropic
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    default_model: str = "llama3.2"
    max_tokens: int = 4096
    temperature: float = 0.7


class AgentConfig(BaseModel):
    """数字员工配置"""
    name: str
    chinese_name: str
    role: str
    department: str
    instructions: str
    goal: str
    tools: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    model: Optional[str] = None
    memory_enabled: bool = True
    provider: str = "ollama"
    max_tool_iterations: int = 10


class CompanyConfig(BaseModel):
    """数字公司整体配置"""
    company_name: str = "我的数字公司"
    ceo_name: str = "CEO"
    default_provider: str = "ollama"
    providers: Dict[str, ProviderConfig] = Field(default_factory=dict)
    agents: List[AgentConfig] = Field(default_factory=list)
    mcp_servers: List[str] = Field(default_factory=list)
    memory_backend: str = "sqlite"  # sqlite, redis, milvus
    observability_enabled: bool = True
    
    @classmethod
    def from_file(cls, path: str = "~/.digital-company/config.yaml") -> "CompanyConfig":
        """从文件加载配置"""
        path = Path(path).expanduser()
        if path.exists():
            with open(path) as f:
                data = yaml.safe_load(f)
                return cls(**data)
        else:
            # 返回默认配置
            return cls()
    
    def get_provider(self, name: str) -> Optional[ProviderConfig]:
        return self.providers.get(name)
    
    def get_agent(self, name: str) -> Optional[AgentConfig]:
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None
    
    def get_agents_by_department(self, department: str) -> List[AgentConfig]:
        return [a for a in self.agents if a.department == department]


# 默认配置
DEFAULT_CONFIG = CompanyConfig(
    company_name="我的数字公司",
    ceo_name="CEO",
    default_provider="ollama",
    providers={
        "ollama": ProviderConfig(
            provider_type="ollama",
            endpoint="http://localhost:11434",
            default_model="llama3.2",
        ),
        "openai": ProviderConfig(
            provider_type="openai",
            default_model="gpt-4o-mini",
        ),
        "anthropic": ProviderConfig(
            provider_type="anthropic",
            default_model="claude-sonnet-4",
        ),
    },
    agents=[
        # 市场部
        AgentConfig(
            name="MarketResearcher",
            chinese_name="市场调研员",
            role="市场调研员",
            department="Marketing",
            instructions="""你是一名资深市场调研专家，擅长：
- 收集和分析市场数据
- 竞品分析和行业研究
- 用户画像构建
- 市场趋势预测

你使用数据驱动的方法，为决策提供可靠依据。""",
            goal="深入洞察市场，为公司提供有价值的洞察",
            tools=["web_search", "file_write", "data_analysis"],
            skills=["market_research", "competitive_analysis"],
        ),
        AgentConfig(
            name="BrandStrategist",
            chinese_name="品牌策略师",
            role="品牌策略师",
            department="Marketing",
            instructions="""你是一名品牌策略专家，擅长：
- 品牌定位和差异化策略
- 营销策划和执行方案
- 内容营销策略
- 媒体投放规划

你善于洞察用户心理，制定有效的品牌传播策略。""",
            goal="建立强大的品牌形象，推动业务增长",
            tools=["doc_writer", "ppt_generator"],
            skills=["branding", "marketing_strategy"],
        ),
        AgentConfig(
            name="ContentWriter",
            chinese_name="内容创作者",
            role="内容创作者",
            department="Marketing",
            instructions="""你是一名资深内容创作者，擅长：
- 高质量文案撰写
- 社交媒体内容策划
- SEO优化内容创作
- 故事叙述和品牌叙事

你的文字有感染力，能引发读者共鸣。""",
            goal="创作引人入胜的内容，传递品牌价值",
            tools=["writing_tool", "seo_tool"],
            skills=["copywriting", "content_strategy", "seo"],
        ),
        
        # 技术部
        AgentConfig(
            name="FrontendEngineer",
            chinese_name="前端工程师",
            role="前端工程师",
            department="Engineering",
            instructions="""你是一名资深前端工程师，擅长：
- React/Vue/Angular 等现代框架
- TypeScript 类型安全编程
- 响应式设计和CSS动画
- 性能优化和用户体验

你编写高质量、可维护的前端代码。""",
            goal="交付高质量、用户友好的前端产品",
            tools=["code_editor", "git", "testing", "browser_devtools"],
            skills=["react", "typescript", "css", "performance"],
            model="codellama",  # 编程任务用专用模型
        ),
        AgentConfig(
            name="BackendEngineer",
            chinese_name="后端工程师",
            role="后端工程师",
            department="Engineering",
            instructions="""你是一名资深后端工程师，擅长：
- Python/Go/Node.js 后端开发
- RESTful API 设计和实现
- 数据库设计和优化
- 微服务架构

你构建稳定、可扩展的后端系统。""",
            goal="构建高效、稳定、安全的后端服务",
            tools=["code_editor", "git", "docker", "database"],
            skills=["python", "golang", "api_design", "database"],
        ),
        AgentConfig(
            name="DevOpsEngineer",
            chinese_name="DevOps工程师",
            role="DevOps工程师",
            department="Engineering",
            instructions="""你是一名资深DevOps工程师，擅长：
- CI/CD 流水线设计
- Docker/Kubernetes 容器化
- 云基础设施管理(AWS/GCP/Azure)
- 监控和日志系统

你确保系统的高可用性和快速迭代能力。""",
            goal="构建可靠的自动化运维体系",
            tools=["docker", "k8s", "monitoring", "logging"],
            skills=["ci_cd", "kubernetes", "aws", "terraform"],
        ),
        AgentConfig(
            name="QAEngineer",
            chinese_name="QA工程师",
            role="QA工程师",
            department="Engineering",
            instructions="""你是一名资深QA工程师，擅长：
- 测试策略制定
- 自动化测试开发
- 性能测试和压力测试
- Bug追踪和质量评估

你坚持质量优先，不让缺陷流出。""",
            goal="确保产品质量，发现并预防潜在问题",
            tools=["testing", "bug_tracker", "performance_testing"],
            skills=["test_automation", "performance_testing", "qa_strategy"],
        ),
        
        # 运营部
        AgentConfig(
            name="ProjectManager",
            chinese_name="项目经理",
            role="项目经理",
            department="Operations",
            instructions="""你是一名经验丰富的项目经理，擅长：
- 项目规划和任务分解
- 进度管理和风险控制
- 团队协作和沟通
- 敏捷/Scrum 方法论

你确保项目按时、高质量交付。""",
            goal="高效协调资源，确保项目成功",
            tools=["task_board", "calendar", "doc_writer"],
            skills=["project_management", "agile", "risk_management"],
        ),
        AgentConfig(
            name="DataAnalyst",
            chinese_name="数据分析师",
            role="数据分析师",
            department="Operations",
            instructions="""你是一名资深数据分析师，擅长：
- 数据清洗和处理
- 统计分析和建模
- 数据可视化
- 洞察提炼和报告

你用数据讲述故事，支持决策。""",
            goal="从数据中提取有价值的洞察",
            tools=["python_code", "chart_generator", "sql"],
            skills=["data_analysis", "visualization", "statistics"],
        ),
        AgentConfig(
            name="CustomerSupport",
            chinese_name="客服专员",
            role="客服专员",
            department="Operations",
            instructions="""你是一名专业客服专员，擅长：
- 用户问题快速响应
- 复杂问题升级处理
- 用户反馈收集整理
- 客户关系维护

你始终保持耐心和专业，给用户最好的体验。""",
            goal="提供优质的客户服务，赢得用户信任",
            tools=["email", "chat", "crm"],
            skills=["customer_service", "problem_solving", "communication"],
        ),
    ],
)
