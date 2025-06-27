"""
AISP- State和Payload（分开文件放吧）


核心特性：
- State: 思想气泡，信息流的基本单位
- Payload: 信息载体，使用Pydantic严格类型检查
"""

import time
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .op import Op

# ==================== State ====================

class State:
    """
    思想气泡 - AISP信息流的基本单位（类比torch.tensor）
    
    每个State包含：
    - payload: 具体信息内容（采用Pydantic模型保证类型安全）
    - creator_op: 创建此状态的操作（用于追溯）
    - inputs: 输入状态列表（构建计算图）
    - can_trace: 是否可追溯（类比requires_grad）
    - note: 简洁注释

    """
    
    def __init__(
        self, 
        payload: BaseModel,
        creator_op: Optional['Op'] = None,
        inputs: Optional[List['State']] = None,
        can_trace: bool = True,
        note: str = ""
    ):
        # 核心数据
        self.payload = payload
        self.creator_op = creator_op
        self.inputs = inputs or []
        self.can_trace = can_trace
        self.note = note
        
        # 基础属性
        self.bubble_id = f"bubble_{id(self)}"
        self.timestamp = time.time()
        
    def detach(self) -> 'State':
        """分离计算图（类比tensor.detach）"""
        return State(
            payload=self.payload,
            creator_op=None,
            inputs=[],
            can_trace=False,
            note=f"Detached from {self.note}"
        )
    
    def clone(self) -> 'State':
        """克隆状态（类比tensor.clone）"""
        return State(
            payload=self.payload.copy(),
            creator_op=self.creator_op,
            inputs=self.inputs.copy(),
            can_trace=self.can_trace,
            note=f"Cloned from {self.note}"
        )
    
    def backward(self, max_depth: Optional[int] = None) -> str:
        """回溯计算图路径（类比tensor.backward）（但是总感觉可视化出来都不太清晰）"""
        def build_tree(state: 'State', depth: int = 0, visited: set = None) -> str:
            if visited is None:
                visited = set()
                
            if id(state) in visited or (max_depth is not None and depth > max_depth):
                return f"{'  ' * depth}🔄 {state.bubble_id} (循环引用或深度限制)"
            
            visited.add(id(state))
            
            # 当前节点信息
            payload_type = type(state.payload).__name__
            creator_info = f" ←{state.creator_op.__class__.__name__}" if state.creator_op else " (原始)"
            current = f"{'  ' * depth}🎈 {state.bubble_id}: {payload_type}{creator_info}"
            if state.note:
                current += f" | {state.note}"
            
            # 递归处理输入
            if state.inputs:
                result = [current]
                for inp in state.inputs:
                    result.append(build_tree(inp, depth + 1, visited))
                return "\n".join(result)
            else:
                return current
        
        return build_tree(self)
    
    def is_origin(self) -> bool:
        """判断是否为原始气泡（无创建者）"""
        return self.creator_op is None
    
    def get_source(self) -> str:
        """获取来源描述"""
        if self.is_origin():
            return "原始输入"
        elif self.creator_op:
            return f"{self.creator_op.__class__.__name__}操作"
        else:
            return "未知来源"
    
    def __repr__(self) -> str:
        payload_type = type(self.payload).__name__
        source = self.get_source()
        return f"State({payload_type}, {source})"

# ==================== Payload ====================

from typing import Literal

class BasePayload(BaseModel):
    """
    所有Payload的基类
    
    统一属性：
    - stage: 科研阶段标识
    - quality: 信息质量 [0-1]
    - timestamp: 时间戳
    - notes: 研究者备注
    """
    stage: Optional[str] = Field(None, description="科研阶段标识")
    quality: Optional[float] = Field(None, ge=0.0, le=1.0, description="信息质量")
    timestamp: float = Field(default_factory=time.time, description="创建时间戳")
    notes: Optional[str] = Field(None, description="研究者备注")


class ResearchBriefPayload(BasePayload):
    """研究任务 - 科研流程起点"""
    research_goal: str = Field(..., description="研究目标和问题")
    background: str = Field(..., description="研究背景和动机")
    requirements: Optional[List[str]] = Field(default_factory=list, description="具体要求和约束")
    deliverables: Optional[List[str]] = Field(default_factory=list, description="预期交付成果")
    timeline: Optional[str] = Field(None, description="时间安排")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.stage:
            self.stage = "research_brief"

class HypothesisPayload(BasePayload):
    """研究假设"""
    hypothesis_statement: str = Field(..., description="明确的假设表述")
    theoretical_basis: str = Field(..., description="理论依据和文献支持")
    variables: Optional[List[str]] = Field(default_factory=list, description="关键变量定义")
    testability: str = Field(..., description="可验证性描述")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.stage:
            self.stage = "hypothesis"

class ExperimentPlanPayload(BasePayload):
    """实验方案"""
    experiment_design: str = Field(..., description="实验设计和架构")
    methodology: str = Field(..., description="具体方法和步骤")
    data_requirements: Optional[List[str]] = Field(default_factory=list, description="数据需求和来源")
    evaluation_metrics: Optional[List[str]] = Field(default_factory=list, description="评估指标和标准")
    resource_needs: Optional[List[str]] = Field(default_factory=list, description="所需资源和工具")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.stage:
            self.stage = "experiment_plan"

class CodePayload(BasePayload):
    """实验代码（方案的具体实现）"""
    code_content: str = Field(..., description="完整代码内容")
    language: str = Field(default="python", description="编程语言")
    dependencies: Optional[List[str]] = Field(default_factory=list, description="依赖包和环境")
    documentation: Optional[str] = Field(None, description="代码文档和注释")
    test_cases: Optional[List[str]] = Field(default_factory=list, description="测试用例")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.stage:
            self.stage = "code"

class ExperimentResultPayload(BasePayload):
    """实验结果（原始数据）"""
    raw_data: Any = Field(..., description="原始实验数据")
    execution_log: str = Field(..., description="执行日志和过程")
    performance_metrics: Optional[Dict[str, float]] = Field(default_factory=dict, description="性能指标数据")
    output_files: Optional[List[str]] = Field(default_factory=list, description="输出文件路径")
    execution_status: str = Field(..., description="执行状态和耗时")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.stage:
            self.stage = "experiment_result"

class FindingPayload(BasePayload):
    """科学发现"""
    key_insights: List[str] = Field(..., description="核心洞察和发现")
    patterns_identified: Optional[List[str]] = Field(default_factory=list, description="识别的模式和规律")
    novelty_assessment: str = Field(..., description="新颖性评估")
    significance: str = Field(..., description="科学意义和影响")
    implications: Optional[List[str]] = Field(default_factory=list, description="理论和实践含义")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.stage:
            self.stage = "finding"

class ManuscriptPayload(BasePayload):
    """学术论文"""
    title: str = Field(..., description="论文标题")
    abstract: str = Field(..., description="摘要")
    sections: Dict[str, str] = Field(..., description="各章节内容字典")
    figures_tables: Optional[List[str]] = Field(default_factory=list, description="图表和可视化")
    references: Optional[List[str]] = Field(default_factory=list, description="参考文献")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.stage:
            self.stage = "manuscript"

class CritiquePayload(BasePayload):
    """批判评审"""
    review_type: Literal["peer_review", "self_review", "mentor_review"] = Field(..., description="评审类型")
    strengths: List[str] = Field(..., description="论文优势和亮点")
    weaknesses: List[str] = Field(..., description="不足和问题")
    suggestions: List[str] = Field(..., description="改进建议")
    decision: Optional[str] = Field(None, description="评审决定")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.stage:
            self.stage = "critique"

__all__ = [
    "State",
    "BasePayload",
    "ResearchBriefPayload", 
    "HypothesisPayload",
    "ExperimentPlanPayload",
    "CodePayload",
    "ExperimentResultPayload",
    "FindingPayload",
    "ManuscriptPayload",
    "CritiquePayload",
] 