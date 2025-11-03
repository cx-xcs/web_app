"""
Windows启动脚本：在启动uvicorn前设置正确的事件循环策略
"""
import asyncio
import sys

if sys.platform == 'win32':
    # 必须在导入任何异步库之前设置
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print("✅ Windows事件循环策略已设置为 SelectorEventLoop")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False  # reload模式下策略会被重置
    )
