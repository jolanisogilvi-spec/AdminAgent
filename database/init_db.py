"""数据库初始化脚本

功能：
1. 创建所有数据库表
2. 插入初始系统配置
3. 创建默认管理员账号
4. 插入示例知识库数据
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, select
from app.core.database import engine, init_db
from app.models import (
    User, SysConfig, KnowledgeBase, Asset,
    ConfigKeys, UserRole, AssetCategory, AssetStatus
)
from app.core.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_default_configs(session: Session):
    """创建默认系统配置"""
    logger.info("Creating default system configurations...")

    default_configs = [
        # LLM配置
        SysConfig(
            config_key=ConfigKeys.LLM_BASE_URL,
            config_value="https://api.openai.com/v1",
            description="大模型API基础URL（支持OpenAI协议）",
            category="llm",
            is_required=True,
            is_editable=True,
            display_order=1
        ),
        SysConfig(
            config_key=ConfigKeys.LLM_API_KEY,
            config_value="",
            description="大模型API密钥",
            category="llm",
            is_sensitive=True,
            is_required=True,
            is_editable=True,
            display_order=2
        ),
        SysConfig(
            config_key=ConfigKeys.LLM_MODEL_NAME,
            config_value="gpt-4",
            description="模型名称（如gpt-4, deepseek-chat, qwen-plus等）",
            category="llm",
            is_required=True,
            is_editable=True,
            display_order=3
        ),
        SysConfig(
            config_key=ConfigKeys.LLM_TEMPERATURE,
            config_value="0.7",
            description="温度参数（0-2，越高越随机）",
            category="llm",
            value_type="float",
            default_value="0.7",
            is_editable=True,
            display_order=4
        ),
        SysConfig(
            config_key=ConfigKeys.LLM_MAX_TOKENS,
            config_value="2000",
            description="最大token数",
            category="llm",
            value_type="int",
            default_value="2000",
            is_editable=True,
            display_order=5
        ),
        SysConfig(
            config_key=ConfigKeys.LLM_TIMEOUT,
            config_value="30",
            description="请求超时时间（秒）",
            category="llm",
            value_type="int",
            default_value="30",
            is_editable=True,
            display_order=6
        ),
        # 审批规则配置
        SysConfig(
            config_key=ConfigKeys.APPROVAL_THRESHOLD_AMOUNT,
            config_value="1000",
            description="需要审批的金额阈值（元）",
            category="approval",
            value_type="float",
            default_value="1000",
            is_editable=True,
            display_order=10
        ),
        SysConfig(
            config_key=ConfigKeys.AUTO_ASSIGN_ADMIN,
            config_value="true",
            description="是否自动分配行政人员",
            category="system",
            value_type="bool",
            default_value="true",
            is_editable=True,
            display_order=20
        ),
        # 系统配置
        SysConfig(
            config_key=ConfigKeys.SYSTEM_NAME,
            config_value="行政智能体系统",
            description="系统名称",
            category="system",
            default_value="行政智能体系统",
            is_editable=True,
            display_order=30
        ),
        SysConfig(
            config_key=ConfigKeys.SESSION_TIMEOUT,
            config_value="480",
            description="会话超时时间（分钟）",
            category="system",
            value_type="int",
            default_value="480",
            is_editable=True,
            display_order=31
        ),
        SysConfig(
            config_key=ConfigKeys.MAX_UPLOAD_SIZE,
            config_value="10",
            description="最大上传文件大小（MB）",
            category="system",
            value_type="int",
            default_value="10",
            is_editable=True,
            display_order=32
        ),
    ]

    for config in default_configs:
        session.add(config)

    logger.info(f"Created {len(default_configs)} system configurations")


def create_default_users(session: Session):
    """创建默认用户"""
    logger.info("Creating default users...")

    users = [
        User(
            username="admin",
            full_name="系统管理员",
            password_hash=get_password_hash("admin123"),
            role=UserRole.SYSTEM_ADMIN,
            department="系统部",
            email="admin@company.com",
            phone="13800138000",
            is_active=True
        ),
        User(
            username="admin_staff",
            full_name="行政专员",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            department="行政部",
            email="admin_staff@company.com",
            phone="13800138001",
            is_active=True
        ),
        User(
            username="manager",
            full_name="部门主管",
            password_hash=get_password_hash("admin123"),
            role=UserRole.MANAGER,
            department="技术部",
            email="manager@company.com",
            phone="13800138002",
            is_active=True
        ),
        User(
            username="employee",
            full_name="普通员工",
            password_hash=get_password_hash("admin123"),
            role=UserRole.EMPLOYEE,
            department="技术部",
            email="employee@company.com",
            phone="13800138003",
            is_active=True
        ),
    ]

    for user in users:
        session.add(user)

    logger.info(f"Created {len(users)} default users")
    logger.info("Default credentials: username / admin123")
    logger.info("⚠️  Please change default passwords after first login!")


def create_sample_knowledge_base(session: Session):
    """创建示例知识库数据"""
    logger.info("Creating sample knowledge base...")

    knowledge_items = [
        KnowledgeBase(
            title="公司WiFi密码获取方式",
            content="""访客WiFi:
- SSID: Guest-WiFi
- 密码: Guest2024

员工WiFi:
- SSID: Staff-WiFi
- 登录方式: 使用工号 + 身份证后6位
- 如有问题请联系IT部门: ext 8888""",
            category="网络",
            tags='["WiFi", "网络", "密码", "IT"]',
            applicable_scenarios='["新员工入职", "访客来访", "网络问题"]',
            is_active=True
        ),
        KnowledgeBase(
            title="报销流程说明",
            content="""报销流程:
1. 在系统中提交报销申请，上传发票照片
2. 直属主管审批（1000元以下自动通过）
3. 财务部审核发票真伪
4. 审批通过后5个工作日内到账

注意事项:
- 发票必须是公司抬头
- 超过3个月的发票不予报销
- 差旅费需附行程单""",
            category="财务",
            tags='["报销", "财务", "发票"]',
            applicable_scenarios='["费用报销", "差旅报销"]',
            is_active=True
        ),
        KnowledgeBase(
            title="会议室预定规则",
            content="""会议室预定:
1. 通过系统提前预定，最多提前7天
2. 会议开始前30分钟可取消
3. 会议结束后请清理会议室

会议室列表:
- A101: 10人，配投影仪
- A102: 20人，配视频会议设备
- B201: 50人，多功能会议厅

紧急会议请联系行政部: ext 6666""",
            category="办公",
            tags='["会议室", "预定", "办公"]',
            applicable_scenarios='["会议预定", "场地申请"]',
            is_active=True
        ),
        KnowledgeBase(
            title="办公用品申领流程",
            content="""申领流程:
1. 在系统中提交申领申请
2. 行政部审核库存
3. 到行政部领取（工作日9:00-17:00）

常备物品:
- 文具类: 笔、本子、订书机等
- 耗材类: 打印纸、墨盒等
- 其他: 口罩、消毒液等

特殊物品需提前3天申请""",
            category="办公",
            tags='["办公用品", "申领", "行政"]',
            applicable_scenarios='["物品申领", "办公需求"]',
            is_active=True
        ),
        KnowledgeBase(
            title="IT设备报修流程",
            content="""报修流程:
1. 在系统中提交报修工单，描述故障现象
2. 上传故障照片（如有）
3. IT部门评估后上门或远程处理
4. 紧急故障（影响工作）请电话联系: ext 8888

常见问题自助:
- 电脑卡顿: 重启电脑
- 网络断开: 检查网线连接
- 打印机故障: 检查纸张和墨盒""",
            category="IT",
            tags='["报修", "IT", "设备", "故障"]',
            applicable_scenarios='["设备故障", "IT支持"]',
            is_active=True
        ),
    ]

    for item in knowledge_items:
        session.add(item)

    logger.info(f"Created {len(knowledge_items)} knowledge base items")


def create_sample_assets(session: Session):
    """创建示例资产数据"""
    logger.info("Creating sample assets...")

    assets = [
        Asset(
            asset_code="IT-2024-001",
            asset_name="联想ThinkPad笔记本",
            category=AssetCategory.IT_EQUIPMENT,
            status=AssetStatus.IN_USE,
            current_stock=1,
            unit_price=6500.00,
            brand="联想",
            model="ThinkPad X1 Carbon",
            location="3楼技术部",
            supplier="联想官方旗舰店"
        ),
        Asset(
            asset_code="IT-2024-002",
            asset_name="戴尔显示器",
            category=AssetCategory.IT_EQUIPMENT,
            status=AssetStatus.IDLE,
            current_stock=5,
            unit_price=1200.00,
            brand="戴尔",
            model="U2720Q 27英寸4K",
            location="仓库",
            supplier="京东自营"
        ),
        Asset(
            asset_code="OF-2024-001",
            asset_name="办公桌椅套装",
            category=AssetCategory.OFFICE_FURNITURE,
            status=AssetStatus.IN_USE,
            current_stock=50,
            unit_price=800.00,
            brand="震旦",
            location="各楼层办公区",
            supplier="震旦办公家具"
        ),
        Asset(
            asset_code="CS-2024-001",
            asset_name="A4打印纸",
            category=AssetCategory.CONSUMABLES,
            status=AssetStatus.IDLE,
            current_stock=100,
            unit_price=25.00,
            brand="得力",
            specifications="500张/包，5包/箱",
            location="行政部仓库",
            supplier="得力官方旗舰店"
        ),
    ]

    for asset in assets:
        session.add(asset)

    logger.info(f"Created {len(assets)} sample assets")


def main():
    """主函数"""
    logger.info("="*50)
    logger.info("Starting database initialization...")
    logger.info("="*50)

    # 创建所有表
    logger.info("Creating database tables...")
    init_db()

    # 检查是否已初始化
    with Session(engine) as session:
        existing_config = session.exec(select(SysConfig)).first()
        if existing_config:
            logger.warning("Database already initialized. Skipping seed data.")
            logger.info("If you want to re-initialize, please drop all tables first.")
            return

        # 插入初始数据
        try:
            create_default_configs(session)
            create_default_users(session)
            create_sample_knowledge_base(session)
            create_sample_assets(session)

            session.commit()

            logger.info("="*50)
            logger.info("Database initialization completed successfully!")
            logger.info("="*50)
            logger.info("\nDefault accounts created:")
            logger.info("  - admin / admin123 (系统管理员)")
            logger.info("  - admin_staff / admin123 (行政专员)")
            logger.info("  - manager / admin123 (部门主管)")
            logger.info("  - employee / admin123 (普通员工)")
            logger.info("\n⚠️  IMPORTANT: Please change default passwords!")

        except Exception as e:
            session.rollback()
            logger.error(f"Error during initialization: {e}")
            raise


if __name__ == "__main__":
    main()
