"""
ID生成器模块的测试
"""
import pytest
from cogletnet.utils.id_generator import generate_id

def test_generate_id_without_prefix():
    """测试无前缀的ID生成"""
    id1 = generate_id()
    id2 = generate_id()
    
    assert isinstance(id1, str)
    assert isinstance(id2, str)
    assert id1 != id2  # 确保生成的ID是唯一的

def test_generate_id_with_prefix():
    """测试带前缀的ID生成"""
    prefix = "test"
    id1 = generate_id(prefix=prefix)
    
    assert isinstance(id1, str)
    assert id1.startswith(f"{prefix}-")
    
    # 测试不同前缀
    other_prefix = "other"
    id2 = generate_id(prefix=other_prefix)
    assert id2.startswith(f"{other_prefix}-")
    assert id1 != id2 