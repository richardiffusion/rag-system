import re
from typing import List
import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def clean_text(self, text: str) -> str:
        """
        清理文本：移除多余空格、换行等
        """
        if not text:
            return ""
        
        # 移除多余的空格和换行
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符但保留基本标点
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        
        return text.strip()
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        将长文本分割成块
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        # 首先尝试按句子分割
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # 如果当前块加上新句子不会超过大小
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + ". "
            else:
                # 如果当前块不为空，保存它
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # 如果单个句子就超过块大小，需要硬分割
                if len(sentence) > self.chunk_size:
                    # 按单词分割长句子
                    words = sentence.split()
                    current_chunk = ""
                    for word in words:
                        if len(current_chunk) + len(word) + 1 <= self.chunk_size:
                            current_chunk += word + " "
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = word + " "
                else:
                    current_chunk = sentence + ". "
        
        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # 应用重叠（如果需要）
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks_with_overlap = []
            for i in range(len(chunks)):
                if i > 0:
                    # 从前一个块取一部分作为重叠
                    previous_chunk = chunks[i-1]
                    overlap_start = max(0, len(previous_chunk) - self.chunk_overlap)
                    overlap_text = previous_chunk[overlap_start:]
                    current_with_overlap = overlap_text + " " + chunks[i]
                    chunks_with_overlap.append(current_with_overlap[:self.chunk_size])
                else:
                    chunks_with_overlap.append(chunks[i])
            return chunks_with_overlap
        
        return chunks
    
    def process_document(self, text: str) -> List[str]:
        """
        完整文档处理流程：清理 + 分块
        """
        cleaned_text = self.clean_text(text)
        chunks = self.split_into_chunks(cleaned_text)
        
        logger.info(f"文档处理完成: 原始长度 {len(text)}, 清理后 {len(cleaned_text)}, 分成 {len(chunks)} 个块")
        
        return chunks

# 全局文本处理器实例
text_processor = TextProcessor()