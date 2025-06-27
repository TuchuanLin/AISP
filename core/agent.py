"""
Agent Module - 智能体

AispAgent是AISP框架中的智能体基类，类比PyTorch中的nn.Module。
Agent是"思考者"大脑，决定使用哪个Op来处理思想气泡(State)。

设计理念：
- 基类仅提供基础设施，不预设任何行为逻辑
- 开发者完全自主实现forward()方法
- 支持Agent组合和模块化设计
- 遵循PyTorch风格的API设计
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Iterator, Tuple
from collections import OrderedDict

from .state import State
from .op import Op, OpRecord


class Logbook:
    """
    实验笔记 - Agent的"思考地图"记录器
    
    Logbook记录两类信息：
    1. 思想气泡(State) - 信息载体
    2. Op执行记录(OpRecord) - 思考过程
    
    每当一个Op产生新的思想气泡时，这个执行过程都会被自动记录为OpRecord。
    所有的"思想气泡"和连接它们的"Op执行记录"，共同构成了
    一张完整的认知计算图。
    """
    
    def __init__(self, name: str = "default", verbose: bool = False):
        self.name = name
        self.op_records: List[OpRecord] = []  # Op执行记录
        self.bubbles: List['State'] = []  # 所有思想气泡
        self.start_time = time.time()
        self.verbose = verbose  # 控制是否自动打印
        
        if self.verbose:
            print(f"[{time.strftime('%H:%M:%S')}] 📚 Logbook '{name}' initialized.")
    
    def _print_event(self, event_type: str, message: str, timestamp: float = None):
        """打印事件日志（仅在需要时使用）"""
        if timestamp is None:
            timestamp = time.time()
        formatted_time = time.strftime('%H:%M:%S', time.localtime(timestamp))
        print(f"[{formatted_time}] {event_type} {message}")
    
    def record(self, bubble: Optional['State'] = None, op_name: Optional[str] = None, inputs: Optional[List['State']] = None, error: Optional[str] = None):
        """
        统一记录方法：记录所有类型的气泡和Op执行
        
        Args:
            bubble: 要记录的气泡 (原始气泡或Op产生的气泡)
            op_name: Op名称，提供时表示这是Op执行记录 (默认: None) 
            inputs: Op的输入气泡列表，op_name提供时必需 (默认: None)
            error: Op执行失败时的错误信息 (默认: None)
        """
        if op_name is not None:
            if inputs is None:
                raise ValueError("inputs is required when op_name is provided")
            record = OpRecord(op_name, inputs)
            start_time = record.timestamp
            if self.verbose:
                input_ids = [f"Bubble[{b.bubble_id}]" for b in inputs]
                self._print_event("🧠", f"{self.name} starts {op_name}({', '.join(input_ids)})", start_time)
            
            if bubble is not None:
                execution_time = time.time() - start_time
                record.complete(bubble, execution_time)
                
                self.bubbles.append(bubble)
                if self.verbose:
                    self._print_event("✨", f"-> 🎈 Bubble[{bubble.bubble_id}] {bubble.note}", bubble.timestamp)
                    
            elif error is not None:
                record.fail(error)
                
                if self.verbose:
                    self._print_event("❌", f"Op {op_name} failed: {error}")
            else:
                raise ValueError("Either bubble or error must be provided for Op execution")
        
            self.op_records.append(record)
            
        elif bubble is not None:
            self.bubbles.append(bubble)
            
            if self.verbose:
                self._print_event("🎈", f"Bubble[{bubble.bubble_id}] {bubble.note}", bubble.timestamp)
                
        else:
            raise ValueError("Either bubble or op_name must be provided")

    def display(self, from_bubble: Optional['State'] = None, count: Optional[int] = None):
        """
        显示计算图树状追溯
        
        Args:
            from_bubble: 起始气泡，None表示从最新气泡开始 (默认: None)
            count: 最大追溯深度，None表示无限制 (默认: None)
        """
        if from_bubble is None:
            if not self.bubbles:
                print(f"📝 Logbook '{self.name}': 无记录")
                return
            from_bubble = self.bubbles[-1]

        def trace_tree(bubble, depth=0, visited=None, prefix=""):
            if visited is None:
                visited = set()

            if count and depth >= count:
                return f"🔄 深度限制({count})"

            if bubble.bubble_id in visited:
                return f"🔄 {bubble.note} (循环引用)"
            
            visited.add(bubble.bubble_id)
            
            producing_record = next((r for r in self.op_records 
                                   if r.output and r.output.bubble_id == bubble.bubble_id), None)
            
            if producing_record:
                result = f"🧠 {producing_record.op_name} -> 🎈 {bubble.note}"
                if producing_record.inputs:
                    for i, input_bubble in enumerate(producing_record.inputs):
                        is_last = i == len(producing_record.inputs) - 1
                        child_prefix = prefix + ("    " if is_last else "│   ")
                        connector = "└── " if is_last else "├── "
                        child_result = trace_tree(input_bubble, depth+1, visited.copy(), child_prefix)
                        result += f"\n{prefix}{connector}{child_result}"
                return result
            else:
                return f"🎈 Origin: {bubble.note}"

        print(f"📝 Logbook '{self.name}' 计算图追溯:")
        print(trace_tree(from_bubble))


class AispAgent(ABC):
    """
    AISP智能体基类 - 类比torch.nn.Module
    
    核心设计理念：
    - Agent是"思考者"大脑，决定使用哪个Op来处理思想气泡
    - 基类仅提供基础设施，不预设任何行为逻辑  
    - 开发者完全自主实现forward()方法
    - 支持Agent组合和模块化设计
    
    基础设施：
    - name: Agent名称
    - logbook: 实验笔记，记录思考过程
    - _modules: 子Agent模块字典，支持组合模式
    """
    
    def __init__(self, name: str, logbook: Optional[Logbook] = None):
        self.name = name
        self.logbook = logbook or Logbook(name)
        self._modules: Dict[str, Any] = OrderedDict()  # 可以包含AispAgent或Op
    
    @abstractmethod
    async def forward(self, *inputs: State, **kwargs) -> Union[State, List[State]]:
        """
        Agent的核心逻辑 - 子类必须实现
        
        Args:
            *inputs: 输入的思想气泡序列
            **kwargs: Agent操作参数
            
        Returns:
            Union[State, List[State]]: 输出的思想气泡
        """
        pass
    
    async def __call__(self, *inputs: State, **kwargs) -> Union[State, List[State]]:
        """
        Agent的统一调用接口
        
        Args:
            *inputs: 输入的思想气泡序列
            **kwargs: Agent操作参数
            
        Returns:
            Union[State, List[State]]: 输出的思想气泡
        """
        return await self.forward(*inputs, **kwargs)
    
    # ==================== 模块管理（仿pytorch） ====================
    
    def add_module(self, name: str, module) -> None:
        """
        添加子模块（Agent或Op）
        
        Args:
            name: 子模块名称
            module: 子模块实例（AispAgent或Op）
        """
        from .op import Op
        
        if not isinstance(module, (AispAgent, Op)):
            raise TypeError(f"Expected AispAgent or Op, got {type(module)}")
        self._modules[name] = module
    
    def modules(self) -> Iterator[Any]:
        """返回所有子模块的迭代器"""
        for module in self._modules.values():
            yield module
    
    def named_modules(self, prefix: str = '') -> Iterator[Tuple[str, Any]]:
        """
        返回所有子模块的名称和模块的迭代器
        
        Args:
            prefix: 名称前缀
            
        Yields:
            Tuple[str, Any]: (模块名, 模块实例)
        """
        if prefix:
            prefix += '.'
        
        for name, module in self._modules.items():
            yield prefix + name, module
            # 只有AispAgent才有named_modules方法
            if isinstance(module, AispAgent):
                yield from module.named_modules(prefix + name)
    
    def get_submodule(self, target: str) -> Any:
        """
        获取指定路径的子模块
        
        Args:
            target: 子模块路径，如 'layer1.conv'
            
        Returns:
            Any: 目标子模块（AispAgent或Op）
        """
        if target == '':
            return self
        
        atoms = target.split('.')
        mod = self
        
        for item in atoms:
            if not hasattr(mod, '_modules'):
                raise AttributeError(f'{mod} has no attribute _modules')
            if item not in mod._modules:
                raise AttributeError(f'{mod} has no submodule {item}')
            mod = mod._modules[item]
        
        return mod
    
    def __getattr__(self, name: str) -> Any:
        """支持通过属性访问子模块"""
        if '_modules' in self.__dict__:
            modules = self.__dict__['_modules']
            if name in modules:
                return modules[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        """支持通过属性设置子模块"""
        from .op import Op
        
        if isinstance(value, (AispAgent, Op)):
            if hasattr(self, '_modules'):
                self._modules[name] = value
        super().__setattr__(name, value)
    
    def __repr__(self) -> str:
        """Agent的字符串表示"""
        return f"{self.__class__.__name__}(name='{self.name}')" 



 