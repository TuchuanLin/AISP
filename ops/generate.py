"""
Generate Operation

AISP协议标准：统一的生成操作接口定义
注意：此为接口协议，不包含具体实现逻辑
开发者需要基于此接口标准实现具体的生成功能
"""

from typing import Dict, Any, Optional
from ..core.op import Op
from ..core.state import State

class Generate(Op):
    """
    统一生成操作 - 创造性思考动作接口标准
    
    AISP协议定义：生成操作的标准化接口
    - 定义输入输出规范
    - 指定参数格式要求  
    - 提供类型注解标准
    
    注意：开发者需要继承此类并实现具体的生成逻辑
    """
    
    def forward(self, input_state: State, type_: str = 'auto', **kwargs) -> State:
        """
        统一生成接口协议标准
        
        AISP协议规范：
        - 输入：单个思想气泡(State)
        - 输出：包含生成内容的新思想气泡(State)
        - 参数：type_指定生成类型，**kwargs扩展参数
        
        Args:
            input_state: 输入思想气泡 
            type_: 生成类型 {'idea', 'hypothesis', 'plan', 'code', 'auto', ...}
            **kwargs: 扩展参数，如creativity, domain, methodology等
            
        Returns:
            State: 包含生成内容的新思想气泡
            
        Raises:
            NotImplementedError: 开发者必须实现此方法
        """
        raise NotImplementedError(
            "Generate.forward() must be implemented by developers. "
            "AISP provides interface standard only, not implementation."
        )
    
    def _infer_generation_type(self, input_state: State) -> str:
        """
        生成类型推断接口（可选实现）
        
        开发者可以重写此方法实现智能类型推断逻辑
        
        Args:
            input_state: 输入思想气泡
            
        Returns:
            str: 推断的生成类型
        """
        return 'auto'  # 默认返回auto，由开发者决定具体推断逻辑
    
 