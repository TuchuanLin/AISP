"""
Execute Operation

AISP协议标准：统一的执行操作接口定义
注意：此为接口协议，不包含具体实现逻辑
开发者需要基于此接口标准实现具体的执行功能
"""

from typing import Dict, Any, Optional, List
from ..core.op import Op
from ..core.state import State

class Execute(Op):
    """
    统一执行操作 - 实践验证思考动作接口标准
    
    AISP协议定义：执行操作的标准化接口
    - 定义输入输出规范
    - 指定执行模式参数格式
    - 提供类型注解标准
    
    注意：开发者需要继承此类并实现具体的执行逻辑
    """
    
    def forward(self, executable_state: State, mode: str = 'auto', **kwargs) -> State:
        """
        统一执行接口协议标准
        
        AISP协议规范：
        - 输入：可执行的思想气泡(State)
        - 输出：包含执行结果的新思想气泡(State)
        - 参数：mode指定执行模式，**kwargs扩展参数
        
        Args:
            executable_state: 可执行的思想气泡
            mode: 执行模式 {'code', 'experiment', 'analysis', 'benchmark', 'auto', ...}
            **kwargs: 扩展参数，如timeout, environment, iterations等
            
        Returns:
            State: 包含执行结果的新思想气泡
            
        Raises:
            NotImplementedError: 开发者必须实现此方法
        """
        raise NotImplementedError(
            "Execute.forward() must be implemented by developers. "
            "AISP provides interface standard only, not implementation."
        )
    
    def _infer_execution_mode(self, executable_state: State) -> str:
        """
        执行模式推断接口（可选实现）
        
        开发者可以重写此方法实现智能模式推断逻辑
        
        Args:
            executable_state: 可执行的思想气泡
            
        Returns:
            str: 推断的执行模式
        """
        return 'auto'  # 默认返回auto，由开发者决定具体推断逻辑 