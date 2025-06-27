"""
Critique Operation

AISP协议标准：统一的批判操作接口定义
注意：此为接口协议，不包含具体实现逻辑
开发者需要基于此接口标准实现具体的批判功能
"""

from typing import List, Dict, Any, Optional
from ..core.op import Op
from ..core.state import State

class Critique(Op):
    """
    统一批判操作 - 批判性思考动作接口标准
    
    AISP协议定义：批判操作的标准化接口
    - 定义输入输出规范
    - 指定批判焦点参数格式
    - 提供类型注解标准
    
    注意：开发者需要继承此类并实现具体的批判逻辑
    """
    
    def forward(self, target_state: State, focus: str = 'comprehensive', **kwargs) -> State:
        """
        统一批判接口协议标准
        
        AISP协议规范：
        - 输入：待批判的思想气泡(State)
        - 输出：包含批判分析的新思想气泡(State)
        - 参数：focus指定批判焦点，**kwargs扩展参数
        
        Args:
            target_state: 待批判的思想气泡
            focus: 批判焦点 {'validity', 'feasibility', 'novelty', 'completeness', 'comprehensive', ...}
            **kwargs: 扩展参数，如criteria, depth, perspective等
            
        Returns:
            State: 包含批判分析的新思想气泡
            
        Raises:
            NotImplementedError: 开发者必须实现此方法
        """
        raise NotImplementedError(
            "Critique.forward() must be implemented by developers. "
            "AISP provides interface standard only, not implementation."
        ) 