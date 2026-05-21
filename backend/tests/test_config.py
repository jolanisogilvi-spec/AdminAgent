"""测试配置模块"""

import pytest
from app.core.config import get_settings


def test_settings_loaded():
    """测试配置是否正确加载"""
    settings = get_settings()
    assert settings.APP_NAME == "Admin Agent API"
    assert settings.APP_VERSION == "1.0.0"
    assert settings.DATABASE_URL is not None
    assert settings.REDIS_HOST is not None


def test_settings_singleton():
    """测试配置是否为单例"""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
