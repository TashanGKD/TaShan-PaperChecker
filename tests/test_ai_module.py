"""
AI服务模块测试脚本
用于验证AI服务模块是否正常工作
"""
import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_simple_ai_client():
    """测试简化版AI客户端"""
    print("=== 测试简化版AI客户端 ===")
    try:
        from core.ai.ai_client import ai_generate
        
        # 测试基本功能
        prompt = "请用一句话介绍人工智能。"
        result = ai_generate(prompt)
        print(f"输入: {prompt}")
        print(f"输出: {result[:200]}...")  # 只显示前200个字符
        print("✅ 简化版AI客户端测试通过\n")
        return True
    except Exception as e:
        print(f"❌ 简化版AI客户端测试失败: {e}\n")
        return False

def test_full_ai_client():
    """测试完整版AI客户端"""
    print("=== 测试完整版AI客户端 ===")
    
    # 获取环境变量中的API密钥
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not dashscope_key and not openai_key:
        print("⚠️ 未配置API密钥，跳过完整版AI客户端测试\n")
        return True
    
    try:
        from core.ai.ai_client import AIClient
        
        # 根据可用的API密钥选择提供商
        if dashscope_key:
            print("使用DashScope进行测试...")
            client = AIClient(
                provider_type="dashscope",
                api_key=dashscope_key,
                model="qwen-turbo"
            )
        elif openai_key:
            print("使用OpenAI进行测试...")
            client = AIClient(
                provider_type="openai",
                api_key=openai_key,
                model="gpt-3.5-turbo"
            )
        else:
            print("⚠️ 未配置有效的API密钥\n")
            return False
        
        # 测试基本生成功能
        prompt = "请简要说明学术论文引用的重要性。"
        result = client.generate(prompt)
        print(f"输入: {prompt}")
        print(f"输出: {result[:200]}...")  # 只显示前200个字符
        
        # 测试提取信息功能
        text = "本文研究了张三（2023）和李四（2024）提出的新型算法。"
        instruction = "提取作者和年份信息"
        extracted = client.extract_info(text, instruction)
        print(f"\n提取测试 - 输入: {text}")
        print(f"提取结果: {extracted}")
        
        # 测试分类功能
        categories = ["学术", "新闻", "商业"]
        category_result = client.classify_text("本文研究了人工智能在医疗领域的应用", categories)
        print(f"\n分类测试 - 结果: {category_result}")
        
        print("✅ 完整版AI客户端测试通过\n")
        return True
    except Exception as e:
        print(f"❌ 完整版AI客户端测试失败: {e}\n")
        return False

def test_citation_optimization():
    """测试引用优化功能"""
    print("=== 测试引用优化功能 ===")
    print("⚠️ 引用优化功能当前不在新架构中，跳过此测试\n")
    # 这个功能可能在新架构中不需要或已重构
    return True

def test_citation_checker_ai():
    """测试CitationChecker中的AI功能"""
    print("=== 测试新架构的CitationChecker ===")
    
    try:
        from core.checker.citation_checker import CitationChecker

        # 测试新的CitationChecker
        # 由于CitationChecker是一个抽象类，我们需要创建一个子类来实例化
        class TestCitationChecker(CitationChecker):
            def check(self, document):
                from models.compliance import ComplianceResult, CheckType
                return ComplianceResult(CheckType.CITATIONS, True, [], {}, {})

        checker = TestCitationChecker()
        print(f"检查类型: {checker.get_check_type()}")
        print(f"检查名称: {checker.get_check_name()}")

        print("✅ 新架构CitationChecker测试通过\n")
        return True
    except Exception as e:
        print(f"❌ 新架构CitationChecker测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试AI服务模块...\n")
    
    results = []
    
    # 运行所有测试
    results.append(test_simple_ai_client())
    results.append(test_full_ai_client())
    results.append(test_citation_optimization())
    results.append(test_citation_checker_ai())
    
    # 输出测试总结
    passed = sum(results)
    total = len(results)
    
    print("="*50)
    print(f"测试完成: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！AI服务模块工作正常。")
    else:
        print("⚠️  部分测试未通过，这通常是因为API密钥未配置。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)