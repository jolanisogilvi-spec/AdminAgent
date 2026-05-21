from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


OPENAPI_TAGS = [
    {"name": "认证登录", "description": "登录、注册、当前登录用户和退出登录。"},
    {"name": "用户管理", "description": "维护系统用户、角色、部门、联系方式和账号启停状态。"},
    {"name": "工单管理", "description": "创建、查询、更新和删除行政工单。"},
    {"name": "资产管理", "description": "维护办公资产、库存、分类、状态和资产明细。"},
    {"name": "任务管理", "description": "维护工单拆解后的处理任务和任务状态。"},
    {"name": "审批管理", "description": "查询待审批工单，并执行通过或驳回。"},
    {"name": "知识库", "description": "维护知识条目，支持分类查询和语义检索。"},
    {"name": "系统设置", "description": "维护系统参数、AI 模型、审批规则和知识库向量配置。"},
    {"name": "智能助手", "description": "行政智能助手对话、知识库同步和知识检索。"},
    {"name": "系统监控", "description": "服务健康检查、就绪检查、存活检查和基础指标。"},
]


PATH_DOCS: dict[tuple[str, str], dict[str, Any]] = {
    ("post", "/api/v1/auth/login"): {
        "tag": "认证登录",
        "summary": "用户登录",
        "description": "使用用户名和密码登录系统，成功后返回访问令牌和当前用户信息。",
    },
    ("post", "/api/v1/auth/register"): {
        "tag": "认证登录",
        "summary": "注册用户",
        "description": "注册一个新用户，并返回登录令牌。通常由管理端或初始化流程使用。",
    },
    ("get", "/api/v1/auth/me"): {
        "tag": "认证登录",
        "summary": "获取当前用户",
        "description": "根据当前访问令牌返回登录用户的基础信息。",
    },
    ("post", "/api/v1/auth/logout"): {
        "tag": "认证登录",
        "summary": "退出登录",
        "description": "客户端退出登录时调用。当前实现返回确认结果。",
    },
    ("get", "/api/v1/users/"): {
        "tag": "用户管理",
        "summary": "用户列表",
        "description": "分页查询用户，可按角色和关键字筛选。",
        "parameters": {
            "role": "用户角色过滤，例如 employee、admin_staff、manager、sys_admin。",
            "keyword": "搜索用户名、姓名或部门。",
            "skip": "跳过的数据条数。",
            "limit": "返回的数据条数上限。",
        },
    },
    ("post", "/api/v1/users/"): {
        "tag": "用户管理",
        "summary": "新增用户",
        "description": "创建系统用户，并设置登录密码、角色、部门和账号状态。",
    },
    ("get", "/api/v1/users/{user_id}"): {
        "tag": "用户管理",
        "summary": "用户详情",
        "description": "根据用户 ID 获取单个用户的完整信息。",
        "parameters": {"user_id": "用户 ID。"},
    },
    ("patch", "/api/v1/users/{user_id}"): {
        "tag": "用户管理",
        "summary": "更新用户",
        "description": "更新用户姓名、角色、部门、联系方式、账号状态；传入密码时会重置密码。",
        "parameters": {"user_id": "用户 ID。"},
    },
    ("delete", "/api/v1/users/{user_id}"): {
        "tag": "用户管理",
        "summary": "删除用户",
        "description": "根据用户 ID 删除用户。",
        "parameters": {"user_id": "用户 ID。"},
    },
    ("post", "/api/v1/tickets/"): {
        "tag": "工单管理",
        "summary": "创建工单",
        "description": "创建采购、报修、领用或咨询类行政工单。",
    },
    ("get", "/api/v1/tickets/"): {
        "tag": "工单管理",
        "summary": "工单列表",
        "description": "分页查询工单，可按处理状态筛选。",
        "parameters": {
            "skip": "跳过的数据条数。",
            "limit": "返回的数据条数上限。",
            "processing_status": "处理状态过滤，例如 pending、in_progress、completed、closed。",
        },
    },
    ("get", "/api/v1/tickets/{ticket_id}"): {
        "tag": "工单管理",
        "summary": "工单详情",
        "description": "根据工单 ID 获取单个工单详情。",
        "parameters": {"ticket_id": "工单 ID。"},
    },
    ("patch", "/api/v1/tickets/{ticket_id}"): {
        "tag": "工单管理",
        "summary": "更新工单",
        "description": "更新工单内容、类型、费用、审批状态、处理状态、负责人和紧急程度。",
        "parameters": {"ticket_id": "工单 ID。"},
    },
    ("delete", "/api/v1/tickets/{ticket_id}"): {
        "tag": "工单管理",
        "summary": "删除工单",
        "description": "根据工单 ID 删除工单。",
        "parameters": {"ticket_id": "工单 ID。"},
    },
    ("post", "/api/v1/assets/"): {
        "tag": "资产管理",
        "summary": "新增资产",
        "description": "新增办公资产或耗材，并校验资产编号是否重复。",
    },
    ("get", "/api/v1/assets/"): {
        "tag": "资产管理",
        "summary": "资产列表",
        "description": "分页查询资产，可按资产分类和资产状态筛选。",
        "parameters": {
            "skip": "跳过的数据条数。",
            "limit": "返回的数据条数上限。",
            "category": "资产分类过滤。",
            "status": "资产状态过滤。",
        },
    },
    ("get", "/api/v1/assets/{asset_id}"): {
        "tag": "资产管理",
        "summary": "资产详情",
        "description": "根据资产 ID 获取单个资产详情。",
        "parameters": {"asset_id": "资产 ID。"},
    },
    ("patch", "/api/v1/assets/{asset_id}"): {
        "tag": "资产管理",
        "summary": "更新资产",
        "description": "更新资产编号、名称、分类、状态、负责人、库存、单价、位置和描述。",
        "parameters": {"asset_id": "资产 ID。"},
    },
    ("delete", "/api/v1/assets/{asset_id}"): {
        "tag": "资产管理",
        "summary": "删除资产",
        "description": "根据资产 ID 删除资产。",
        "parameters": {"asset_id": "资产 ID。"},
    },
    ("post", "/api/v1/assets/{asset_id}/stock"): {
        "tag": "资产管理",
        "summary": "调整库存",
        "description": "按数量调整资产库存。正数增加库存，负数减少库存。",
        "parameters": {"asset_id": "资产 ID。", "quantity": "库存调整数量。"},
    },
    ("post", "/api/v1/tasks/"): {
        "tag": "任务管理",
        "summary": "新增任务",
        "description": "创建工单处理任务，可关联工单、指定负责人、优先级和截止时间。",
    },
    ("get", "/api/v1/tasks/"): {
        "tag": "任务管理",
        "summary": "任务列表",
        "description": "分页查询任务，可按关联工单、负责人和任务状态筛选。",
        "parameters": {
            "skip": "跳过的数据条数。",
            "limit": "返回的数据条数上限。",
            "related_ticket_id": "关联工单 ID。",
            "assigned_to": "负责人用户 ID。",
            "status": "任务状态过滤。",
        },
    },
    ("get", "/api/v1/tasks/{task_id}"): {
        "tag": "任务管理",
        "summary": "任务详情",
        "description": "根据任务 ID 获取单个任务详情。",
        "parameters": {"task_id": "任务 ID。"},
    },
    ("patch", "/api/v1/tasks/{task_id}"): {
        "tag": "任务管理",
        "summary": "更新任务",
        "description": "更新任务标题、描述、关联工单、负责人、状态、优先级和截止时间。",
        "parameters": {"task_id": "任务 ID。"},
    },
    ("delete", "/api/v1/tasks/{task_id}"): {
        "tag": "任务管理",
        "summary": "删除任务",
        "description": "根据任务 ID 删除任务。",
        "parameters": {"task_id": "任务 ID。"},
    },
    ("get", "/api/v1/approvals/pending"): {
        "tag": "审批管理",
        "summary": "待审批工单",
        "description": "查询主管审批或财务审批待处理的工单列表。",
        "parameters": {
            "approval_type": "审批类型：manager 表示主管审批，finance 表示财务审批。",
            "skip": "跳过的数据条数。",
            "limit": "返回的数据条数上限。",
        },
    },
    ("post", "/api/v1/approvals/tickets/{ticket_id}/approve"): {
        "tag": "审批管理",
        "summary": "审批通过",
        "description": "对指定工单执行审批通过，可填写审批意见。",
        "parameters": {"ticket_id": "工单 ID。", "approval_type": "审批类型：manager 或 finance。"},
    },
    ("post", "/api/v1/approvals/tickets/{ticket_id}/reject"): {
        "tag": "审批管理",
        "summary": "驳回工单",
        "description": "驳回指定工单，必须填写驳回理由。",
        "parameters": {"ticket_id": "工单 ID。"},
    },
    ("post", "/api/v1/knowledge/"): {
        "tag": "知识库",
        "summary": "新增知识",
        "description": "新增知识库条目，并触发知识内容向量化。",
    },
    ("get", "/api/v1/knowledge/"): {
        "tag": "知识库",
        "summary": "知识列表",
        "description": "分页查询知识库条目，可按分类筛选。",
        "parameters": {
            "category": "知识分类。",
            "skip": "跳过的数据条数。",
            "limit": "返回的数据条数上限。",
        },
    },
    ("get", "/api/v1/knowledge/{knowledge_id}"): {
        "tag": "知识库",
        "summary": "知识详情",
        "description": "根据知识 ID 获取单条知识详情。",
        "parameters": {"knowledge_id": "知识 ID。"},
    },
    ("put", "/api/v1/knowledge/{knowledge_id}"): {
        "tag": "知识库",
        "summary": "更新知识",
        "description": "更新知识标题、内容和分类，并重新同步向量索引。",
        "parameters": {"knowledge_id": "知识 ID。"},
    },
    ("delete", "/api/v1/knowledge/{knowledge_id}"): {
        "tag": "知识库",
        "summary": "删除知识",
        "description": "删除知识库条目及其向量索引。",
        "parameters": {"knowledge_id": "知识 ID。"},
    },
    ("post", "/api/v1/knowledge/search"): {
        "tag": "知识库",
        "summary": "语义检索",
        "description": "基于查询文本在知识库中执行语义检索。",
    },
    ("post", "/api/v1/configs/"): {
        "tag": "系统设置",
        "summary": "新增配置",
        "description": "新增或保存系统配置项。",
    },
    ("get", "/api/v1/configs/"): {
        "tag": "系统设置",
        "summary": "配置列表",
        "description": "查询系统配置列表，可选择是否返回敏感配置值。",
        "parameters": {"include_sensitive": "是否包含敏感配置值。"},
    },
    ("get", "/api/v1/configs/{config_key}"): {
        "tag": "系统设置",
        "summary": "配置详情",
        "description": "根据配置键读取单个配置值。",
        "parameters": {"config_key": "配置键。"},
    },
    ("put", "/api/v1/configs/{config_key}"): {
        "tag": "系统设置",
        "summary": "更新配置",
        "description": "根据配置键更新配置值、说明和敏感标记。",
        "parameters": {"config_key": "配置键。"},
    },
    ("delete", "/api/v1/configs/{config_key}"): {
        "tag": "系统设置",
        "summary": "删除配置",
        "description": "根据配置键删除配置项。",
        "parameters": {"config_key": "配置键。"},
    },
    ("post", "/api/v1/configs/init"): {
        "tag": "系统设置",
        "summary": "补齐默认配置",
        "description": "初始化或补齐系统默认配置项。",
    },
    ("post", "/api/v1/ai/chat"): {
        "tag": "智能助手",
        "summary": "智能助手对话",
        "description": "发送用户消息，系统会判断是知识问答还是工单生成，并返回处理结果。",
    },
    ("post", "/api/v1/ai/knowledge/sync"): {
        "tag": "智能助手",
        "summary": "同步知识向量",
        "description": "将知识库条目同步到向量库，用于智能问答和语义检索。",
    },
    ("get", "/api/v1/ai/knowledge/search"): {
        "tag": "智能助手",
        "summary": "检索知识向量",
        "description": "直接调用向量检索能力，返回与查询文本相关的知识条目。",
        "parameters": {"query": "检索关键词或问题。", "top_k": "返回结果数量。"},
    },
    ("get", "/"): {
        "tag": "系统监控",
        "summary": "服务根路径",
        "description": "返回前端首页或 API 基础运行信息。",
    },
    ("get", "/health"): {
        "tag": "系统监控",
        "summary": "健康检查",
        "description": "检查 API 服务是否正常运行。",
    },
    ("get", "/health/ready"): {
        "tag": "系统监控",
        "summary": "就绪检查",
        "description": "用于部署平台判断服务是否已准备好接收请求。",
    },
    ("get", "/health/live"): {
        "tag": "系统监控",
        "summary": "存活检查",
        "description": "用于部署平台判断服务进程是否存活。",
    },
    ("get", "/metrics"): {
        "tag": "系统监控",
        "summary": "基础指标",
        "description": "返回 Prometheus 文本格式的基础服务指标。",
    },
}


SCHEMA_TITLES = {
    "LoginRequest": "登录请求",
    "RegisterRequest": "注册请求",
    "HTTPValidationError": "请求参数校验错误",
    "ValidationError": "字段校验错误",
    "ApprovalStatus": "审批状态",
    "ProcessingStatus": "处理状态",
    "TicketType": "工单类型",
    "UrgencyLevel": "紧急程度",
    "AssetCategory": "资产分类",
    "AssetStatus": "资产状态",
    "TaskStatus": "任务状态",
    "UserRole": "用户角色",
    "UserCreate": "新增用户请求",
    "UserUpdate": "更新用户请求",
    "UserResponse": "用户信息",
    "TicketCreate": "创建工单请求",
    "TicketUpdate": "更新工单请求",
    "TicketResponse": "工单信息",
    "AssetCreate": "新增资产请求",
    "AssetUpdate": "更新资产请求",
    "AssetResponse": "资产信息",
    "TaskCreate": "新增任务请求",
    "TaskUpdate": "更新任务请求",
    "TaskResponse": "任务信息",
    "ApprovalRecordUpdate": "审批意见请求",
    "KnowledgeCreate": "新增知识请求",
    "KnowledgeUpdate": "更新知识请求",
    "KnowledgeSearch": "知识检索请求",
    "KnowledgeResponse": "知识信息",
    "ConfigCreate": "新增配置请求",
    "ConfigUpdate": "更新配置请求",
    "ConfigResponse": "配置信息",
    "ChatRequest": "智能助手请求",
    "ChatResponse": "智能助手响应",
}


FIELD_DESCRIPTIONS = {
    "username": "用户名。",
    "password": "登录密码。",
    "name": "姓名。",
    "full_name": "姓名。",
    "role": "用户角色。",
    "department": "所属部门。",
    "email": "邮箱。",
    "phone": "电话。",
    "is_active": "账号是否启用。",
    "id": "数据 ID。",
    "created_at": "创建时间。",
    "updated_at": "更新时间。",
    "original_text": "工单原始诉求内容。",
    "attachments": "附件地址，多个附件可用逗号分隔。",
    "ticket_type": "工单类型。",
    "related_asset_id": "关联资产 ID。",
    "estimated_cost": "预估费用。",
    "urgency": "紧急程度。",
    "approval_status": "审批状态。",
    "processing_status": "处理状态。",
    "assigned_to": "负责人用户 ID。",
    "requester_id": "发起人用户 ID。",
    "closed_at": "关闭时间。",
    "asset_code": "资产编号。",
    "category": "分类。",
    "status": "状态。",
    "owner_id": "负责人用户 ID。",
    "current_stock": "当前库存。",
    "unit_price": "单价。",
    "location": "存放位置。",
    "description": "描述。",
    "title": "标题。",
    "content": "内容。",
    "view_count": "查看次数。",
    "config_key": "配置键。",
    "config_value": "配置值。",
    "is_sensitive": "是否为敏感配置。",
    "message": "用户消息。",
    "image_urls": "图片地址列表。",
    "intent_type": "识别出的意图类型。",
    "response": "助手回复内容。",
    "ticket_id": "生成的工单 ID。",
    "confidence": "识别置信度。",
    "query": "检索文本。",
    "n_results": "返回结果数量。",
    "top_k": "返回结果数量。",
    "comment": "审批意见或驳回原因。",
    "priority": "优先级。",
    "due_date": "截止时间。",
    "completed_at": "完成时间。",
}


def install_chinese_openapi(app: FastAPI) -> None:
    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title="行政智能体 API 文档",
            version=app.version,
            description=(
                "行政智能体后端接口文档，覆盖认证登录、用户管理、工单、任务、审批、"
                "资产、知识库、系统设置、智能助手和系统监控接口。"
            ),
            routes=app.routes,
            tags=OPENAPI_TAGS,
        )

        for path, path_item in schema.get("paths", {}).items():
            for method, operation in list(path_item.items()):
                if method not in {"get", "post", "put", "patch", "delete"}:
                    continue
                doc = PATH_DOCS.get((method, path))
                if not doc:
                    continue
                operation["tags"] = [doc["tag"]]
                operation["summary"] = doc["summary"]
                operation["description"] = doc["description"]
                operation["operationId"] = f"{method}_{path.strip('/').replace('/', '_').replace('{', '').replace('}', '') or 'root'}"

                parameter_docs = doc.get("parameters", {})
                for parameter in operation.get("parameters", []):
                    name = parameter.get("name")
                    if name in parameter_docs:
                        parameter["description"] = parameter_docs[name]

        schemas = schema.get("components", {}).get("schemas", {})
        for name, component in schemas.items():
            if name in SCHEMA_TITLES:
                component["title"] = SCHEMA_TITLES[name]
            for field_name, prop in component.get("properties", {}).items():
                prop.setdefault("description", FIELD_DESCRIPTIONS.get(field_name, field_name))

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi
