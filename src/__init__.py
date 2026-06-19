"""
Digital Company - 数字公司主入口
1人CEO + N个数字员工的多Agent协作系统
"""

import asyncio
from typing import Optional, Dict, Any
from .company import DigitalCompany
from .config import CompanyConfig

__version__ = "0.1.0"
__all__ = ["DigitalCompany", "CompanyConfig"]


async def main():
    """启动数字公司"""
    config = CompanyConfig.from_file("~/.digital-company/config.yaml")
    company = DigitalCompany(config)
    
    print("🏢 数字公司启动中...")
    print(f"   CEO: {config.ceo_name}")
    print(f"   数字员工: {len(config.agents)} 人")
    print()
    
    await company.start()
    
    # 启动交互式CEO界面
    print("\n" + "="*50)
    print("🎙️  CEO指令界面 (输入 'exit' 退出)")
    print("="*50 + "\n")
    
    while True:
        try:
            command = input("CEO> ")
            if command.lower() in ["exit", "quit", "退出"]:
                break
            
            if command.strip():
                result = await company.execute(command)
                print(f"\n📋 执行结果:\n{result}\n")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    await company.shutdown()
    print("\n👋 数字公司已关闭")


if __name__ == "__main__":
    asyncio.run(main())
