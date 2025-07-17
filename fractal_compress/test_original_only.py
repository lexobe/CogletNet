#!/usr/bin/env python3
"""
只测试原始HybridCompressor在43个样本上的性能
然后与已有的增强版本结果进行对比分析
"""

import sys
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# 加载.env文件
load_dotenv('/Users/liuyu/Code/CogletNet/.env')

# 添加包路径
sys.path.insert(0, 'src')

# 导入原始混合压缩器
from fractal_compress.utils.hybrid_compressor import (
    HybridCompressor, 
    validate_compression
)

def load_test_corpus():
    """加载测试语料"""
    try:
        with open('corpus_50_samples_20_300.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['corpus']
    except FileNotFoundError:
        print("❌ 未找到测试语料文件 corpus_50_samples_20_300.json")
        return []

def test_original_hybrid_optimized(corpus_list):
    """优化版本测试原始HybridCompressor"""
    print("🔧 测试原始混合压缩器 (HybridCompressor) - 优化版本")
    print("==" * 40)
    
    compressor = HybridCompressor(default_model="gpt-4o-mini")
    results = []
    
    for i, corpus in enumerate(corpus_list, 1):
        print(f"📝 [{i:2d}/43] ID{corpus['id']} ({corpus['language']}, {corpus['length']}字符)", end=" ")
        
        try:
            start_time = time.time()
            
            # 映射语言代码
            language_map = {"zh": "chinese", "en": "english", "mixed": "mixed"}
            language = language_map.get(corpus['language'], "mixed")
            
            # 执行原始混合压缩 - 减少尝试次数
            result = compressor.compress(
                text=corpus['text'],
                language=language,
                compression_strategy="precise",
                max_compression_attempts=2  # 减少为2次尝试
            )
            
            processing_time = time.time() - start_time
            validation = validate_compression(result)
            
            # 简化输出
            status = "✅" if result.success else "❌"
            print(f"{status} {result.actual_a_length}→{result.actual_compressed_length} ({processing_time:.1f}s)")
            
            # 记录详细结果
            record = {
                "id": corpus['id'],
                "title": corpus['title'],
                "category": corpus['category'],
                "language": corpus['language'],
                "original_text": corpus['text'],
                "original_length": corpus['length'],
                "part_a": result.original_part_a,
                "part_a_length": result.actual_a_length,
                "compressed_text": result.compressed_text,
                "compressed_length": result.actual_compressed_length,
                "split_ratio": result.split_ratio,
                "compression_ratio": result.compression_ratio,
                "overall_ratio": result.overall_ratio,
                "processing_time": processing_time,
                "success": result.success,
                "target_a_length": result.target_a_length,
                "target_compressed_length": result.target_compressed_length,
                "split_accurate": validation['split_accuracy'],
                "compression_accurate": validation['compression_accuracy'],
                "split_error": validation['split_error'],
                "compression_error": validation['compression_error'],
                "model": result.model_used,
                "method": "OriginalHybridCompressor",
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(record)
            
        except Exception as e:
            print(f"❌ 错误: {str(e)[:30]}...")
            record = {
                "id": corpus['id'],
                "title": corpus['title'],
                "success": False,
                "error": str(e),
                "method": "OriginalHybridCompressor"
            }
            results.append(record)
        
        # 减少延迟时间
        if i < len(corpus_list):
            time.sleep(0.3)  # 从1秒减少到0.3秒
    
    return results

def load_enhanced_results():
    """加载已有的增强版本测试结果"""
    try:
        with open('enhanced_hybrid_compressor_test_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['detailed_results']
    except FileNotFoundError:
        print("❌ 未找到增强版本测试结果文件")
        return []

def quick_comparison_analysis(original_results, enhanced_results):
    """快速对比分析"""
    print(f"\n" + "==" * 50)
    print("📊 原始版本 vs 增强版本 快速对比分析")
    print("==" * 50)
    
    # 基础统计
    original_successful = [r for r in original_results if r.get('success', False)]
    enhanced_successful = [r for r in enhanced_results if r.get('success', False)]
    
    total_count = len(original_results)
    original_success_count = len(original_successful)
    enhanced_success_count = len(enhanced_successful)
    
    print(f"🎯 基础对比:")
    print(f"  测试样本总数: {total_count}")
    print(f"  原始版本成功: {original_success_count}/{total_count} ({original_success_count/total_count*100:.1f}%)")
    print(f"  增强版本成功: {enhanced_success_count}/{total_count} ({enhanced_success_count/total_count*100:.1f}%)")
    print(f"  成功率差异: {(enhanced_success_count - original_success_count)/total_count*100:+.1f}个百分点")
    
    # 成功样本的性能对比
    if original_successful and enhanced_successful:
        orig_avg_time = sum(r['processing_time'] for r in original_successful) / len(original_successful)
        enh_avg_time = sum(r.get('processing_time', 0) for r in enhanced_successful) / len(enhanced_successful)
        
        print(f"\n⏱️ 处理时间对比:")
        print(f"  原始版本平均: {orig_avg_time:.2f}秒")
        print(f"  增强版本平均: {enh_avg_time:.2f}秒")
        
        if orig_avg_time > 0:
            time_improvement = (orig_avg_time - enh_avg_time) / orig_avg_time * 100
            print(f"  速度改进: {time_improvement:+.1f}%")
    
    # 语言类型表现
    print(f"\n🌐 语言类型表现:")
    languages = ['zh', 'en', 'mixed']
    for lang in languages:
        orig_lang_total = len([r for r in original_results if r.get('language') == lang])
        orig_lang_success = len([r for r in original_successful if r.get('language') == lang])
        enh_lang_success = len([r for r in enhanced_successful if r.get('language') == lang])
        
        if orig_lang_total > 0:
            orig_rate = orig_lang_success / orig_lang_total * 100
            enh_rate = enh_lang_success / orig_lang_total * 100
            lang_name = {'zh': '中文', 'en': '英文', 'mixed': '混合'}[lang]
            print(f"  {lang_name}: 原始{orig_rate:.1f}% vs 增强{enh_rate:.1f}%")
    
    # 结论
    print(f"\n🏆 结论:")
    if enhanced_success_count > original_success_count:
        print(f"  ✅ 增强版本成功率更高")
    elif enhanced_success_count == original_success_count:
        print(f"  ⚖️ 两版本成功率相当")
    else:
        print(f"  ⚠️ 原始版本成功率更高")
    
    print(f"  🚀 增强版本优势: 严格长度控制、置信度评估、质量分级")
    
    return {
        "original_success_rate": original_success_count / total_count,
        "enhanced_success_rate": enhanced_success_count / total_count,
        "success_rate_difference": (enhanced_success_count - original_success_count) / total_count
    }

def main():
    """主函数"""
    print("🔬 原始HybridCompressor测试 - 快速版本")
    print("然后与增强版本进行对比分析")
    print("=" * 60)
    
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ 未找到 OPENAI_API_KEY")
        return
    
    print("✅ 检测到 OPENAI_API_KEY")
    
    # 加载语料
    print("📚 加载测试语料...")
    corpus_list = load_test_corpus()
    
    if not corpus_list:
        print("❌ 无法加载测试语料")
        return
    
    print(f"✅ 已加载 {len(corpus_list)} 个测试语料")
    
    # 测试原始版本
    print(f"\n🔧 开始测试原始混合压缩器...")
    start_total = time.time()
    original_results = test_original_hybrid_optimized(corpus_list)
    end_total = time.time()
    
    print(f"\n⏱️ 原始版本测试完成，总耗时: {end_total - start_total:.1f}秒")
    
    # 加载增强版本结果
    print(f"\n📖 加载增强版本测试结果...")
    enhanced_results = load_enhanced_results()
    
    if not enhanced_results:
        print("❌ 无法加载增强版本结果，仅显示原始版本结果")
        # 显示原始版本基础统计
        successful = len([r for r in original_results if r.get('success', False)])
        print(f"原始版本成功率: {successful}/{len(original_results)} ({successful/len(original_results)*100:.1f}%)")
        return
    
    print(f"✅ 已加载增强版本结果，共 {len(enhanced_results)} 个")
    
    # 快速对比分析
    analysis = quick_comparison_analysis(original_results, enhanced_results)
    
    # 导出结果
    export_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "test_type": "Original HybridCompressor Only - Optimized",
            "total_samples": len(corpus_list),
            "purpose": "测试原始版本并与已有增强版本结果对比"
        },
        "original_results": original_results,
        "comparison_summary": analysis
    }
    
    filename = "original_hybrid_test_results.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 测试结果已导出到: {filename}")
    print(f"\n🏁 测试完成")

if __name__ == "__main__":
    main()