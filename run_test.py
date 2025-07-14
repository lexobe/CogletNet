"""
运行测试
"""

import sys
import os

# 保证 src 在 PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from dotenv import load_dotenv
from cogletnet import CogletNet
import pytest

if __name__ == "__main__":
    # 调用指定测试函数，便于断点调试
    pytest.main([
        "-s",
        "-v",
        "-W", "ignore::pytest.PytestAssertRewriteWarning",
        "tests/core/test_real_think_with_20_coglets.py::test_real_think"
    ]) 