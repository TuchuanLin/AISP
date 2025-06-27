"""
AISP Operations

四大核心操作
- generate: 生成新想法、假设、代码
- critique: 批判分析现有内容  
- execute: 执行代码和实验
- synthesize: 综合多个状态

"""

from typing import Union, List, Optional, Any, Dict
from ..core.state import State
from ..core.op import Op

# ==================== 核心操作 ====================

def generate(input_state: State, 
            type_: str = 'auto', 
            **kwargs) -> State:
    """生成操作 - 创造新的思想内容
    
    Args:
        input_state: 输入思想气泡
        type_: 生成类型，可选值：
            - 'idea': 研究想法
            - 'hypothesis': 可测试假设  
            - 'plan': 实施方案
            - 'code': 代码实现
            - 'auto': 智能推断（默认）
        **kwargs: 额外的生成参数
            
    Returns:
        包含生成内容的新思想气泡
            
    Examples:
        >>> idea = generate(background, 'idea')
        >>> hypothesis = generate(data, 'hypothesis')
        >>> code = generate(plan, 'code')
        >>> auto_result = generate(input_state)  # 自动推断
    """
    from .generate import Generate
    return Generate()(input_state, type=type_, **kwargs)

def critique(target_state: State, 
            focus: str = 'comprehensive',
            **kwargs) -> State:
    """批判操作 - 批判性分析内容
    
    Args:
        target_state: 待批判的思想气泡
        focus: 批判焦点，可选值：
            - 'validity': 有效性检查
            - 'feasibility': 可行性评估
            - 'novelty': 新颖性评判
            - 'completeness': 完整性检查
            - 'comprehensive': 综合批判（默认）
        **kwargs: 额外的批判参数
            
    Returns:
        包含批判分析的新思想气泡
            
    Examples:
        >>> review = critique(hypothesis, 'validity')
        >>> feasibility = critique(plan, 'feasibility')
        >>> full_review = critique(content)  # 综合批判
    """
    from .critique import Critique
    return Critique()(target_state, focus=focus, **kwargs)

def execute(executable_state: State,
           mode: str = 'auto',
           **kwargs) -> State:
    """执行操作 - 实践验证内容
    
    Args:
        executable_state: 可执行的思想气泡
        mode: 执行模式，可选值：
            - 'code': 代码执行
            - 'experiment': 实验运行  
            - 'analysis': 数据分析
            - 'benchmark': 性能测试
            - 'auto': 智能推断（默认）
        **kwargs: 额外的执行参数
            
    Returns:
        包含执行结果的新思想气泡
            
    Examples:
        >>> result = execute(code, 'experiment')
        >>> analysis = execute(data, 'analysis')
        >>> auto_result = execute(content)  # 自动推断
    """
    from .execute import Execute
    return Execute()(executable_state, mode=mode, **kwargs)

def synthesize(*input_states: State,
              output: str = 'insights',
              **kwargs) -> State:
    """综合操作 - 整合多个思想状态
    
    Args:
        *input_states: 多个输入思想气泡
        output: 输出类型，可选值：
            - 'insights': 洞察提取（默认）
            - 'conclusion': 结论总结
            - 'report': 报告生成  
            - 'knowledge': 知识构建
            - 'recommendations': 建议提出
        **kwargs: 额外的综合参数
            
    Returns:
        包含综合结果的新思想气泡
            
    Examples:
        >>> insights = synthesize(result1, result2, 'insights')
        >>> report = synthesize(hyp, exp, critique, 'report')
        >>> auto_synthesis = synthesize(state1, state2)  # 默认洞察
    """
    from .synthesize import Synthesize
    return Synthesize()(*input_states, output=output, **kwargs)



# ==================== 导出接口 ====================

__all__ = [
    'generate', 'critique', 'execute', 'synthesize',
] 