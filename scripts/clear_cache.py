#!/usr/bin/env python3
"""
强制清除所有模型缓存
"""

import os
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_all_cache():
    """清除所有相关缓存"""
    cache_paths = [
        os.path.expanduser('~/.cache/torch/sentence_transformers'),
        os.path.expanduser('~/.cache/huggingface/hub'),
        os.path.expanduser('~/.cache/torch/transformers'),
        # Windows 特定路径
        os.path.expanduser('~/AppData/Local/torch/sentence_transformers'),
        os.path.expanduser('~/AppData/Local/huggingface/hub'),
    ]
    
    for cache_path in cache_paths:
        if os.path.exists(cache_path):
            try:
                shutil.rmtree(cache_path, ignore_errors=True)
                logger.info(f"✅ 已清除缓存: {cache_path}")
            except Exception as e:
                logger.warning(f"清除缓存 {cache_path} 失败: {e}")
        else:
            logger.info(f"ℹ️ 缓存路径不存在: {cache_path}")
    
    print("🎉 缓存清除完成！")

if __name__ == "__main__":
    clear_all_cache()
