"""
AISP (AI Scientist Protocol)

人工智能科学家协议 - 为自主科研AI系统提供开放、标准化的设计与协作框架

核心特性：
- 基于认知计算图的可追溯思考过程
- PyTorch风格的模块化设计（State, Op, Agent）
- 标准化的科研协作接口
"""

__version__ = "1.0.0"


from .core.state import State
from .core.op import Op, OpRecord
from .core.agent import AispAgent


from . import ops


Agent = AispAgent

__all__ = [
    "State",
    "Op", 
    "OpRecord",
    "AispAgent",
    "Agent",
    "ops",
] 