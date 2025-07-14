"""
pytest配置文件
"""
import pytest
from cogletnet.core.vector_store import VectorStore
from cogletnet.core.mam import MAM
from cogletnet.core.coglets import Coglets
from cogletnet import CogletNet

@pytest.fixture
def vector_store():
    """创建向量存储实例"""
    return VectorStore(
        url="https://test-url",
        token="test-token"
    )

@pytest.fixture
def mam():
    """创建MAM实例"""
    return MAM()

@pytest.fixture
def coglets(vector_store):
    """创建Coglets实例"""
    return Coglets(vector_store=vector_store)

@pytest.fixture
def storage_config():
    """存储配置"""
    return {
        "upstash_url": "https://test.upstash.com",
        "upstash_token": "test_token",
        "set_id": "test_set"
    }

@pytest.fixture
def llm_config():
    """LLM配置"""
    return {
        "model": "4o-mini",
        "max_retries": 3,
        "temperature": 0.7
    }

@pytest.fixture
def memory_config():
    """记忆机制配置"""
    return {
        "beta": 0.85,
        "gamma": 0.3,
        "b": 0.05,
        "initial_weight": 0.5,
        "golden_ratio": 0.618,
        "top_k": 10
    }

@pytest.fixture
def thinking_config():
    """思考过程配置"""
    return {
        "max_cycles": 5
    }

@pytest.fixture
def prompts_config():
    """提示词配置"""
    return {
        "role": None,
        "format": None,
        "thinking": None,
        "example": None
    }

@pytest.fixture
def cogletnet(storage_config, llm_config, memory_config, thinking_config, prompts_config):
    """创建CogletNet实例"""
    return CogletNet(
        storage_config=storage_config,
        llm_config=llm_config,
        memory_config=memory_config,
        thinking_config=thinking_config,
        prompts_config=prompts_config
    ) 