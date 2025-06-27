"""
AISP Core Module

核心模块包含AISP框架的基础概念：
- State: 认知状态，信息流的基本单位（类比torch.tensor）
- Op: 认知操作，标准化的思考动作（类比nn.functional）
- Agent: 智能体，思考者的大脑（类比nn.Module）
"""

from .state import State
from .op import Op, OpRecord  
from .agent import AispAgent, Logbook

__all__ = [
    "State",
    "Op",
    "OpRecord", 
    "AispAgent",
    "Logbook",
] 


 