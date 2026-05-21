"""Ticket Schemas - 工单相关的请求/响应模型

用于API的数据验证和序列化
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.models import TicketType, ApprovalStatus, ProcessingStatus


# 基础Schema
class TicketBase(BaseModel):
    """工单基础Schema"""
    title: str = Field(..., min_length=1, max_length=200, description="工单标题")
    description: Optional[str] = Field(None, description="详细描述")
    ticket_type: TicketType = Field(..., description="工单类型")
    urgency_level: int = Field(1, ge=1, le=5, description="紧急程度(1-5)")
    related_asset_id: Optional[int] = Field(None, description="关联资产ID")
    estimated_cost: Optional[float] = Field(None, ge=0, description="预估费用")


# 创建工单请求
class TicketCreate(TicketBase):
    """创建工单请求Schema"""
    original_text: str = Field(..., min_length=1, description="原始文本内容")
    attachments: Optional[List[str]] = Field(None, description="附件URL列表")

    @validator('attachments')
    def validate_attachments(cls, v):
        if v and len(v) > 10:
            raise ValueError('最多上传10个附件')
        return v


# AI解析工单请求
class TicketAIParse(BaseModel):
    """AI解析工单请求Schema"""
    original_text: str = Field(..., min_length=1, description="原始文本内容")
    attachments: Optional[List[str]] = Field(None, description="附件URL列表")


# AI解析结果
class TicketAIParseResult(BaseModel):
    """AI解析结果Schema"""
    ticket_type: TicketType = Field(..., description="工单类型")
    title: str = Field(..., description="工单标题")
    description: str = Field(..., description="详细描述")
    urgency_level: int = Field(..., ge=1, le=5, description="紧急程度")
    estimated_cost: Optional[float] = Field(None, description="预估费用")
    related_asset_name: Optional[str] = Field(None, description="关联资产名称")
    confidence_score: float = Field(..., ge=0, le=1, description="置信度")


# 更新工单请求
class TicketUpdate(BaseModel):
    """更新工单请求Schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    urgency_level: Optional[int] = Field(None, ge=1, le=5)
    related_asset_id: Optional[int] = None
    estimated_cost: Optional[float] = Field(None, ge=0)
    actual_cost: Optional[float] = Field(None, ge=0)


# 审批工单请求
class TicketApproval(BaseModel):
    """审批工单请求Schema"""
    approval_status: ApprovalStatus = Field(..., description="审批状态")
    notes: Optional[str] = Field(None, max_length=500, description="审批备注")


# 分配工单请求
class TicketAssign(BaseModel):
    """分配工单请求Schema"""
    admin_id: int = Field(..., description="行政人员ID")


# 关闭工单请求
class TicketClose(BaseModel):
    """关闭工单请求Schema"""
    actual_cost: Optional[float] = Field(None, ge=0, description="实际费用")


# 工单响应
class TicketResponse(TicketBase):
    """工单响应Schema"""
    id: int
    creator_id: int
    original_text: str
    attachments: Optional[str] = None
    approval_status: ApprovalStatus
    approved_by_manager_id: Optional[int] = None
    approved_by_finance_id: Optional[int] = None
    approval_notes: Optional[str] = None
    processing_status: ProcessingStatus
    assigned_admin_id: Optional[int] = None
    actual_cost: Optional[float] = None
    ai_confidence_score: Optional[float] = None
    ai_parsed_json: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 工单列表响应
class TicketListResponse(BaseModel):
    """工单列表响应Schema"""
    total: int = Field(..., description="总数")
    items: List[TicketResponse] = Field(..., description="工单列表")
    skip: int = Field(..., description="跳过的记录数")
    limit: int = Field(..., description="返回的最大记录数")


# 工单统计响应
class TicketStatistics(BaseModel):
    """工单统计响应Schema"""
    total_count: int
    type_counts: dict
    status_counts: dict
    avg_processing_time_hours: Optional[float] = None
    total_estimated_cost: float
    total_actual_cost: float
