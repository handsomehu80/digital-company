"""
Task Router - 任务路由器
分析CEO指令，将任务路由到合适的Agent或部门
"""

from typing import Dict, List, Optional
import asyncio


class Router:
    """
    任务路由器
    理解用户意图，决定如何执行任务
    """
    
    # 部门关键词映射
    DEPARTMENT_KEYWORDS = {
        "Marketing": [
            "市场", "营销", "品牌", "内容", "推广", "广告",
            "调研", "竞品", "用户画像", "增长", "获客",
            "market", "brand", "content", "marketing", "research",
        ],
        "Engineering": [
            "开发", "代码", "前端", "后端", "API", "数据库",
            "DevOps", "测试", "部署", "架构", "性能",
            "开发", "编程", "bug", "feature",
            "develop", "code", "frontend", "backend", "devops", "test",
        ],
        "Operations": [
            "运营", "项目", "管理", "进度", "数据", "分析",
            "客服", "支持", "维护", "监控",
            "operation", "project", "management", "data", "support",
        ],
        "Finance": [
            "财务", "预算", "成本", "收益", "投资", "报表",
            "finance", "budget", "cost", "revenue", "investment",
        ],
    }
    
    # Agent类型关键词映射
    AGENT_KEYWORDS = {
        "FrontendEngineer": [
            "前端", "React", "Vue", "UI", "界面", "样式",
            "frontend", "react", "vue", "css", "interface",
        ],
        "BackendEngineer": [
            "后端", "API", "服务器", "数据库", "SQL",
            "backend", "api", "server", "database",
        ],
        "MarketResearcher": [
            "调研", "市场分析", "竞品分析", "行业研究",
            "research", "analysis", "competitor",
        ],
        "BrandStrategist": [
            "品牌", "策略", "定位", "营销方案",
            "brand", "strategy", "positioning",
        ],
        "ContentWriter": [
            "文案", "内容", "文章", "写作",
            "content", "copy", "writing", "article",
        ],
        "ProjectManager": [
            "项目", "计划", "排期", "任务分解",
            "project", "plan", "schedule",
        ],
        "DataAnalyst": [
            "数据", "分析", "报表", "图表", "统计",
            "data", "analytics", "report", "chart",
        ],
        "QAEngineer": [
            "测试", "bug", "质量", "review",
            "test", "quality", "review",
        ],
        "DevOpsEngineer": [
            "部署", "CI/CD", "Docker", "K8s", "运维",
            "deploy", "docker", "kubernetes", "devops",
        ],
        "CustomerSupport": [
            "客服", "用户问题", "支持", "反馈",
            "support", "customer", "feedback",
        ],
    }
    
    def __init__(self, config):
        self.config = config
    
    async def understand_intent(self, command: str) -> Dict:
        """
        分析用户指令，理解意图
        返回：
        - intent_type: simple | multi_agent | workflow
        - agent_type: 具体的Agent类型
        - departments: 需要涉及的部门列表
        - requires_multiple_agents: 是否需要多Agent协作
        - task_keywords: 任务关键词
        """
        command_lower = command.lower()
        
        # 1. 分析需要的部门
        departments = self._detect_departments(command_lower)
        
        # 2. 分析具体的Agent类型
        agent_type = self._detect_agent_type(command_lower)
        
        # 3. 判断是否需要多Agent协作
        requires_multiple = self._needs_multi_agent(command_lower, departments)
        
        # 4. 提取任务关键词
        keywords = self._extract_keywords(command_lower)
        
        # 5. 判断任务类型
        intent_type = self._classify_intent(command_lower, requires_multiple, departments)
        
        return {
            "intent_type": intent_type,
            "agent_type": agent_type,
            "departments": departments,
            "requires_multiple_agents": requires_multiple,
            "task_keywords": keywords,
            "original_command": command,
        }
    
    def _detect_departments(self, command: str) -> List[str]:
        """检测涉及的部门"""
        departments = []
        
        for dept, keywords in self.DEPARTMENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in command:
                    if dept not in departments:
                        departments.append(dept)
                    break
        
        # 默认返回运营部（如果没检测到）
        if not departments:
            departments = ["Operations"]
        
        return departments
    
    def _detect_agent_type(self, command: str) -> Optional[str]:
        """检测具体的Agent类型"""
        for agent_type, keywords in self.AGENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in command:
                    return agent_type
        return None
    
    def _needs_multi_agent(self, command: str, departments: List[str]) -> bool:
        """判断是否需要多Agent协作"""
        # 多部门协作标志
        multi_indicators = [
            "和", "以及", "还有", "同时", "一起",
            "and", "also", "together", "both",
            "协作", "合作", "配合",
        ]
        
        for indicator in multi_indicators:
            if indicator in command:
                return True
        
        # 多个部门
        if len(departments) > 1:
            return True
        
        # 复杂任务标志
        complex_indicators = [
            "完整的", "整个", "全面", "系统",
            "调研", "分析", "规划", "设计",
            "develop", "analyze", "plan", "design",
        ]
        
        for indicator in complex_indicators:
            if indicator in command:
                return True
        
        return False
    
    def _extract_keywords(self, command: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取
        stop_words = {"的", "了", "是", "在", "和", "有", "我", "你", "他", "她", "它"}
        words = command.replace(",", " ").replace(".", " ").split()
        return [w for w in words if w not in stop_words and len(w) > 1]
    
    def _classify_intent(
        self, 
        command: str, 
        requires_multiple: bool, 
        departments: List[str]
    ) -> str:
        """分类任务类型"""
        if requires_multiple or len(departments) > 1:
            return "workflow"
        elif any(k in command for k in ["开发", "代码", "写", "实现", "develop", "code"]):
            return "engineering"
        elif any(k in command for k in ["调研", "分析", "研究", "research", "analyze"]):
            return "research"
        elif any(k in command for k in ["内容", "文案", "写作", "content", "write"]):
            return "content"
        elif any(k in command for k in ["项目", "计划", "排期", "project", "plan"]):
            return "project"
        else:
            return "general"
