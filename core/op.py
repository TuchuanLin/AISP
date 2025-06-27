"""
Op Module

Op（Operation）是AISP框架中的标准化认知操作，类比PyTorch中的Function。
在动态计算图中，Op作为边连接State节点

每个Op都是无状态的、可组合的，专注于特定的认知任务，
自动维护计算图的结构和完整性
"""

import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .state import State

class OpRecord:
    """
    认知操作执行记录 - 用于Logbook记录
    
    记录一次完整的Op执行过程，包括：
    - 操作信息（op_name, inputs）
    - 执行结果（output, execution_time, status）
    - 错误信息（error）
    
    注意：这主要用于Logbook记录，计算图结构由State和Op直接维护。
    """
    
    def __init__(self, op_name: str, inputs: List['State']):
        self.record_id = str(uuid.uuid4())[:8]
        self.op_name = op_name
        self.inputs = inputs
        self.output = None
        self.timestamp = time.time()
        self.execution_time = None
        self.status = "started"
        self.error = None
    
    def complete(self, output: 'State', execution_time: float):
        """完成Op执行记录"""
        self.output = output
        self.execution_time = execution_time
        self.status = "completed"
    
    def fail(self, error: str):
        """标记Op执行失败"""
        self.status = "failed"
        self.error = error
    
    def __repr__(self) -> str:
        return f"OpRecord(id='{self.record_id}', op='{self.op_name}')"

class OpFunction:
    """
    Op函数上下文 - 类比PyTorch的Function
    
    提供静态方法来执行forward操作，
    并自动维护计算图结构。
    """
    
    @staticmethod
    def apply(op: 'Op', *inputs: 'State', **kwargs) -> Union['State', List['State']]:
        """
        执行Op并构建计算图连接
        
        Args:
            op: 要执行的Op实例
            *inputs: 输入State节点
            **kwargs: 操作参数
            
        Returns:
            Union[State, List[State]]: 输出State节点
        """
        from .state import State

        for input_state in inputs:
            if not isinstance(input_state, State):
                raise TypeError(f"Expected State, got {type(input_state)}")

        try:
            outputs = op.forward(*inputs, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Op {op.name} failed: {str(e)}") from e
        
        if not isinstance(outputs, list):
            outputs = [outputs]
        
        # 设置计算图连接
        result_states = []
        for output in outputs:
            if isinstance(output, State):
                if output.creator_op is None:  
                    output.creator_op = op
                    output.inputs = list(inputs)
                    output.is_origin = False
                result_states.append(output)
            else:
                # 这里需要确定payload类型，可能得根据具体Op实现
                raise TypeError(f"Op {op.name} output must be State, got {type(output)}")

        return result_states[0] if len(result_states) == 1 else result_states

class Op(ABC):
    """
    认知操作基类 - 动态计算图的边 (类比 torch.nn.functional)
    
    在动态计算图中，Op作为边连接State节点：
    - State是节点，保存数据和计算历史
    - Op是边，定义节点间的变换关系
    - 执行Op会自动构建计算图连接

    """
    
    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
    
    @abstractmethod
    def forward(self, *states: 'State', **kwargs) -> Union['State', List['State']]:
        """
        执行认知操作的核心逻辑 - 子类必须实现
        
        Args:
            *states: 输入的State节点
            **kwargs: 操作参数
            
        Returns:
            Union[State, List[State]]: 输出State节点
            
        Note:
            这个方法只负责实际的计算逻辑，计算图连接由OpFunction.apply自动处理
        """
        pass
    
    def __call__(self, *states: 'State', logbook=None, **kwargs) -> Union['State', List['State']]:
        """
        执行认知操作
        
        Args:
            *states: 输入的State节点
            logbook: 实验笔记，记录执行过程（可选）
            **kwargs: 操作参数
            
        Returns:
            Union[State, List[State]]: 输出State节点
            
        Note:
            自动构建计算图连接，并可选地记录到Logbook
        """
        start_time = time.time()
        
        try:
            # 使用OpFunction.apply执行操作并构建计算图
            result = OpFunction.apply(self, *states, **kwargs)
            
            execution_time = time.time() - start_time

            if logbook:
                outputs = result if isinstance(result, list) else [result]
                for output in outputs:
                    logbook.record(output, op_name=self.name, inputs=list(states))
            
            return result
            
        except Exception as e:
            if logbook:
                logbook.record(op_name=self.name, inputs=list(states), error=str(e))
            raise
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"

class CompositeOp(Op):
    """
    复合Op - 将多个Op组合成一个操作
    
    类比PyTorch的Sequential，支持Op的链式组合。（其实感觉有点鸡肋）
    """
    
    def __init__(self, *ops: Op, name: Optional[str] = None):
        super().__init__(name or f"Composite({len(ops)})")
        self.ops = ops
    
    def forward(self, *states: 'State', **kwargs) -> Union['State', List['State']]:
        """
        顺序执行所有子Op
        
        Args:
            *states: 输入State节点
            **kwargs: 操作参数
            
        Returns:
            Union[State, List[State]]: 最终输出State节点
        """
        current = states
        
        for op in self.ops:
            # 执行当前Op
            current = op(*current, **kwargs)
            # 确保下一次输入是tuple形式
            if not isinstance(current, (list, tuple)):
                current = (current,)
        
        return current[0] if len(current) == 1 else list(current)


# ==================== 工具函数 ====================

def create_op_record(op_name: str, inputs: List['State']) -> OpRecord:
    """
    创建操作记录的便捷函数
    
    Args:
        op_name: 操作名称
        inputs: 输入的State列表
        
    Returns:
        OpRecord: 新创建的操作记录
    """
    return OpRecord(op_name, inputs)


__all__ = [
    "Op",
    "OpRecord", 
    "OpFunction",
    "CompositeOp",
    "create_op_record",
] 