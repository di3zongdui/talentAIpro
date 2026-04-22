#!/usr/bin/env python
"""
Phase 2 测试运行器
"""
import sys
import os

# 添加项目根目录到sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 确保TalentAI_Pro被识别为一个包
os.chdir(project_root)

# 现在可以导入TalentAI_Pro的模块了
from TalentAI_Pro.tests.test_phase2 import main

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)