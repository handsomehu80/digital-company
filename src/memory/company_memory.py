"""
Company Memory System - 公司记忆系统
负责存储和检索数字公司的集体记忆
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class CompanyMemory:
    """
    公司级记忆系统
    - 存储任务执行历史
    - 存储跨Agent的知识共享
    - 支持向量检索（未来扩展）
    """
    
    def __init__(self, config):
        self.config = config
        self.db_path = Path("~/.digital-company/memory.db").expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 任务历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent_name TEXT,
                command TEXT,
                result TEXT,
                success INTEGER,
                duration REAL
            )
        """)
        
        # 知识库表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                category TEXT,
                created_at TEXT NOT NULL,
                accessed_at TEXT NOT NULL,
                access_count INTEGER DEFAULT 0
            )
        """)
        
        # Agent记忆表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def store(
        self, 
        key: str, 
        value: Any, 
        category: Optional[str] = None
    ):
        """存储记忆"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO knowledge_base 
            (key, value, category, created_at, accessed_at, access_count)
            VALUES (?, ?, ?, 
                COALESCE((SELECT created_at FROM knowledge_base WHERE key = ?), ?),
                ?, 
                COALESCE((SELECT access_count FROM knowledge_base WHERE key = ?), 0) + 1
            )
        """, (key, str(value), category, key, now, now, key))
        
        conn.commit()
        conn.close()
    
    async def recall(self, key: str) -> Optional[Any]:
        """检索记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE knowledge_base 
            SET accessed_at = ?, access_count = access_count + 1
            WHERE key = ?
        """, (datetime.now().isoformat(), key))
        
        cursor.execute(
            "SELECT value FROM knowledge_base WHERE key = ?",
            (key,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            try:
                return json.loads(row[0])
            except json.JSONDecodeError:
                return row[0]
        return None
    
    async def search(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """搜索记忆（简单文本匹配）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT key, value, category, access_count
                FROM knowledge_base
                WHERE (key LIKE ? OR value LIKE ?) AND category = ?
                ORDER BY access_count DESC
                LIMIT 10
            """, (f"%{query}%", f"%{query}%", category))
        else:
            cursor.execute("""
                SELECT key, value, category, access_count
                FROM knowledge_base
                WHERE key LIKE ? OR value LIKE ?
                ORDER BY access_count DESC
                LIMIT 10
            """, (f"%{query}%", f"%{query}%"))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "key": row[0],
                "value": row[1],
                "category": row[2],
                "access_count": row[3],
            }
            for row in rows
        ]
    
    async def store_task(
        self,
        agent_name: str,
        command: str,
        result: str,
        success: bool,
        duration: float,
    ):
        """存储任务执行记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO task_history 
            (timestamp, agent_name, command, result, success, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            agent_name,
            command,
            result[:5000],  # 限制长度
            1 if success else 0,
            duration,
        ))
        
        conn.commit()
        conn.close()
    
    async def get_task_history(
        self, 
        agent_name: Optional[str] = None, 
        limit: int = 20
    ) -> List[Dict]:
        """获取任务历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if agent_name:
            cursor.execute("""
                SELECT timestamp, agent_name, command, result, success, duration
                FROM task_history
                WHERE agent_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent_name, limit))
        else:
            cursor.execute("""
                SELECT timestamp, agent_name, command, result, success, duration
                FROM task_history
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "timestamp": row[0],
                "agent_name": row[1],
                "command": row[2],
                "result": row[3],
                "success": bool(row[4]),
                "duration": row[5],
            }
            for row in rows
        ]
    
    async def store_agent_memory(
        self,
        agent_name: str,
        key: str,
        value: Any,
    ):
        """存储单个Agent的个人记忆"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO agent_memory
            (agent_name, key, value, created_at)
            VALUES (?, ?, ?, ?)
        """, (agent_name, key, str(value), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    async def get_agent_memory(self, agent_name: str) -> List[Dict]:
        """获取Agent的个人记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT key, value, created_at
            FROM agent_memory
            WHERE agent_name = ?
            ORDER BY created_at DESC
        """, (agent_name,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {"key": row[0], "value": row[1], "created_at": row[2]}
            for row in rows
        ]
    
    def size(self) -> int:
        """获取记忆库大小"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        kb_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM task_history")
        task_count = cursor.fetchone()[0]
        
        conn.close()
        
        return kb_count + task_count
    
    async def save_all(self):
        """保存所有记忆（关闭前调用）"""
        # SQLite自动持久化，这里可以做额外的备份操作
        pass
