"""
测试 VectorStore 类的功能
"""

import pytest
from datetime import datetime, timedelta
import json
import os
import time
from dotenv import load_dotenv
from cogletnet.core.vector_store import VectorStore
from cogletnet.utils.logging import setup_logger

# 加载环境变量
load_dotenv()

# 设置测试环境
os.environ["LOG_LEVEL_VECTORSTORE"] = "INFO"
logger = setup_logger("VectorStore")

# 从环境变量获取配置
TEST_URL = os.getenv("UPSTASH_URL")
TEST_TOKEN = os.getenv("UPSTASH_TOKEN")
TEST_SET_ID = "test_set_" + datetime.now().strftime("%Y%m%d%H%M%S")  # 使用时间戳确保唯一性
TEST_CONTENT = "这是一个测试内容"
TEST_METADATA = {"tag": "test", "priority": 1}

@pytest.fixture
def vector_store():
    """创建测试用的 VectorStore 实例"""
    if not TEST_URL or not TEST_TOKEN:
        pytest.skip("缺少 Upstash Vector 配置")
    store = VectorStore(TEST_URL, TEST_TOKEN)
    # 确保测试集合是空的
    store.clean_coglet_set(TEST_SET_ID)
    time.sleep(1)  # 等待清理完成
    return store

def test_init():
    """测试初始化"""
    # 测试正常初始化
    store = VectorStore(TEST_URL, TEST_TOKEN)
    assert store.index is not None

    # 测试参数验证
    with pytest.raises(ValueError):
        VectorStore("", TEST_TOKEN)
    with pytest.raises(ValueError):
        VectorStore(TEST_URL, "")

def test_clean_coglet_set(vector_store):
    """测试清理认元集合"""
    # 先添加一些测试数据
    vector_store.add_coglet(TEST_SET_ID, "测试内容1", {"tag": "A"})
    time.sleep(1)
    vector_store.add_coglet(TEST_SET_ID, "测试内容2", {"tag": "B"})
    time.sleep(1)

    # 测试清理
    assert vector_store.clean_coglet_set(TEST_SET_ID)
    time.sleep(1)  # 等待清理完成

    # 验证清理结果
    results = vector_store.search_similar(TEST_SET_ID, "测试内容", top_k=10)
    assert len(results) == 0

    # 测试参数验证
    with pytest.raises(ValueError):
        vector_store.clean_coglet_set("")

def test_add_coglet(vector_store):
    """测试添加单个认元"""
    # 测试正常添加
    vector_id = vector_store.add_coglet(TEST_SET_ID, TEST_CONTENT, TEST_METADATA)
    assert vector_id is not None
    time.sleep(1)  # 等待索引更新

    # 验证添加结果
    results = vector_store.search_similar(TEST_SET_ID, TEST_CONTENT, top_k=1)
    assert len(results) == 1
    assert results[0]["text"] == TEST_CONTENT
    assert results[0]["set_id"] == TEST_SET_ID
    assert results[0]["tag"] == TEST_METADATA["tag"]
    assert results[0]["priority"] == TEST_METADATA["priority"]

    # 测试参数验证
    with pytest.raises(ValueError):
        vector_store.add_coglet("", TEST_CONTENT, TEST_METADATA)
    with pytest.raises(ValueError):
        vector_store.add_coglet(TEST_SET_ID, "", TEST_METADATA)

def test_add_coglets(vector_store):
    """测试批量添加认元"""
    # 准备测试数据
    items = [
        {"content": "内容1", "metadata": {"tag": "A"}},
        {"content": "内容2", "metadata": {"tag": "B"}}
    ]
    
    # 测试正常添加
    vector_ids = vector_store.add_coglets(TEST_SET_ID, items)
    assert len(vector_ids) == 2
    time.sleep(1)  # 等待索引更新

    # 验证批量添加的结果
    results = vector_store.search_similar(TEST_SET_ID, "内容", top_k=10)
    assert len(results) == 2
    assert any(r["text"] == "内容1" and r["tag"] == "A" for r in results)
    assert any(r["text"] == "内容2" and r["tag"] == "B" for r in results)

    # 测试参数验证
    with pytest.raises(ValueError):
        vector_store.add_coglets("", items)
    with pytest.raises(ValueError):
        vector_store.add_coglets(TEST_SET_ID, [])

def test_get_coglet(vector_store):
    """测试获取认元"""
    # 先添加测试数据
    vector_id = vector_store.add_coglet(TEST_SET_ID, TEST_CONTENT, TEST_METADATA)
    time.sleep(1)  # 等待索引更新

    # 测试正常获取
    coglet = vector_store.get_coglet(vector_id)
    assert coglet is not None
    assert coglet["text"] == TEST_CONTENT
    assert coglet["set_id"] == TEST_SET_ID
    assert coglet["tag"] == TEST_METADATA["tag"]

    # 测试认元不存在
    assert vector_store.get_coglet("not_exist") is None

    # 测试参数验证
    with pytest.raises(ValueError):
        vector_store.get_coglet("")

def test_update_coglet(vector_store):
    """测试更新认元"""
    # 先添加测试数据
    vector_id = vector_store.add_coglet(TEST_SET_ID, TEST_CONTENT, TEST_METADATA)
    time.sleep(1)  # 等待索引更新
    
    # 测试正常更新
    new_text = "更新后的内容"
    assert vector_store.update_coglet(vector_id, new_text)
    time.sleep(1)  # 等待索引更新
    
    # 验证更新结果
    coglet = vector_store.get_coglet(vector_id)
    assert coglet is not None
    assert coglet["text"] == new_text

    # 测试认元不存在
    assert not vector_store.update_coglet("not_exist", new_text)

    # 测试参数验证
    with pytest.raises(ValueError):
        vector_store.update_coglet("", new_text)

def test_delete_coglet(vector_store):
    """测试删除单个认元"""
    # 先添加测试数据
    vector_id = vector_store.add_coglet(TEST_SET_ID, TEST_CONTENT, TEST_METADATA)
    time.sleep(1)  # 等待索引更新

    # 测试正常删除
    assert vector_store.delete_coglet(vector_id)
    time.sleep(1)  # 等待索引更新

    # 验证删除结果
    assert vector_store.get_coglet(vector_id) is None

    # 测试删除不存在的认元
    assert not vector_store.delete_coglet("not_exist")
    
    # 测试参数验证
    with pytest.raises(ValueError):
        vector_store.delete_coglet("")

def test_delete_coglets(vector_store):
    """测试批量删除认元"""
    # 先添加测试数据
    vector_ids = vector_store.add_coglets(TEST_SET_ID, [
        {"content": "内容1", "metadata": {"tag": "A"}},
        {"content": "内容2", "metadata": {"tag": "B"}}
    ])
    time.sleep(1)  # 等待索引更新

    # 测试正常删除
    assert vector_store.delete_coglets(vector_ids)
    time.sleep(1)  # 等待索引更新
    
    # 验证删除结果
    for vector_id in vector_ids:
        assert vector_store.get_coglet(vector_id) is None

    # 测试删除不存在的认元
    assert not vector_store.delete_coglets(["not_exist1", "not_exist2"])
    
    # 测试参数验证
    with pytest.raises(ValueError):
        vector_store.delete_coglets([])

def test_search_similar(vector_store):
    """测试相似性搜索"""
    # 先添加测试数据
    vector_store.add_coglets(TEST_SET_ID, [
        {"content": "Python 编程语言", "metadata": {"tag": "A"}},
        {"content": "Java 编程语言", "metadata": {"tag": "B"}},
        {"content": "数据库设计", "metadata": {"tag": "C"}}
    ])
    time.sleep(1)  # 等待索引更新

    # 测试正常搜索
    results = vector_store.search_similar(TEST_SET_ID, "编程语言", top_k=2)
    assert len(results) == 2
    assert all("编程语言" in r["text"] for r in results)

    # 测试相似度阈值
    results = vector_store.search_similar(TEST_SET_ID, "编程语言", top_k=2, similarity_threshold=0.8)
    assert len(results) <= 2
    assert all(r["score"] >= 0.8 for r in results)

    # 测试参数验证
    with pytest.raises(ValueError):
        vector_store.search_similar("", "测试查询")
    with pytest.raises(ValueError):
        vector_store.search_similar(TEST_SET_ID, "")
    with pytest.raises(ValueError):
        vector_store.search_similar(TEST_SET_ID, "测试查询", top_k=0)
    with pytest.raises(ValueError):
        vector_store.search_similar(TEST_SET_ID, "测试查询", similarity_threshold=1.5)

def test_search_order(vector_store):
    """测试搜索结果排序"""
    # 先添加测试数据
    vector_store.add_coglets(TEST_SET_ID, [
        {"content": "Python 编程语言", "metadata": {"tag": "A"}},
        {"content": "Python 基础教程", "metadata": {"tag": "B"}},
        {"content": "Python 高级特性", "metadata": {"tag": "C"}}
    ])
    time.sleep(1)  # 等待索引更新

    # 测试结果排序
    results = vector_store.search_similar(TEST_SET_ID, "Python", top_k=3)
    
    # 验证分数降序排列
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)

def test_error_handling(vector_store):
    """测试错误处理"""
    # 测试网络错误（通过使用无效的 URL）
    with pytest.raises(Exception):
        VectorStore("https://invalid.url", TEST_TOKEN).add_coglet(TEST_SET_ID, TEST_CONTENT, TEST_METADATA)

    # 测试无效的 token
    with pytest.raises(Exception):
        VectorStore(TEST_URL, "invalid_token").add_coglet(TEST_SET_ID, TEST_CONTENT, TEST_METADATA)

    # 测试认元不存在
    assert vector_store.get_coglet("not_exist") is None
