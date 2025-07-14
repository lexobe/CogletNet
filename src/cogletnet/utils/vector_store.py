"""向量存储实现，使用 Upstash 作为后端存储"""

from typing import Dict, List, Any, Optional, Union
from upstash_vector import Index, Vector
from upstash_vector.types import QueryResult
from datetime import datetime
import json
import time

from ..utils.id_generator import generate_id
from ..utils.log_config import setup_logger

# 常量定义
DEFAULT_BATCH_SIZE = 1000
MAX_ATTEMPTS = 3
RETRY_DELAY = 5  # 秒

logger = setup_logger("VectorStore")

class VectorStore:
    """向量存储实现，使用 Upstash 作为后端存储"""
    
    def __init__(self, url: str, token: str):
        """
        初始化向量存储
        
        Args:
            url: Upstash 服务地址
            token: Upstash 访问令牌
            
        Raises:
            ValueError: 当url或token为空时
        """
        if not url or not token:
            raise ValueError("URL和token不能为空")
            
        self.index = Index(
            url=url,
            token=token
        )
        
    def clean_coglet_set(self, set_id: str) -> bool:
        """
        清理指定认元集合中的所有认元
        
        Args:
            set_id: 认元集合ID
            
        Returns:
            bool: 操作是否成功
            
        Raises:
            ValueError: 当set_id为空时
        """
        if not set_id:
            raise ValueError("set_id不能为空")
            
        logger.info(f"Clean set: {set_id}")
        
        for attempt in range(MAX_ATTEMPTS):
            # 查找集合中的认元
            try:
            results = self.index.query(
                data="",
                    top_k=DEFAULT_BATCH_SIZE,
                filter=f"set_id = '{str(set_id)}'",
                include_metadata=False,
                include_data=False
            )
            except Exception as e:
                logger.error(f"查询失败: {str(e)}")
                continue
            
            logger.debug(f"Query {attempt+1}, found: {len(results) if results else 0}")
            
            if not results:
                logger.info(f"Set {set_id} cleaned")
                return True
                
            try:
            # 批量删除找到的认元
            coglet_ids = [str(result.id) for result in results]
            success = self.index.delete(ids=coglet_ids)
            
            logger.debug(f"Batch delete: {coglet_ids}")
            
                # 验证删除结果
                if not success:
                    logger.warning(f"删除操作未返回成功状态")
                    continue
            
            # 再次查询以确认删除成功
            check_results = self.index.query(
                data="",
                    top_k=DEFAULT_BATCH_SIZE,
                filter=f"set_id = '{str(set_id)}'",
                include_metadata=False,
                include_data=False
            )
            
            logger.debug(f"After delete, left: {len(check_results) if check_results else 0}")
            
            if not check_results or len(check_results) < len(results) / 2:
                    continue
                    
                time.sleep(RETRY_DELAY)
                
            except Exception as e:
                logger.error(f"删除操作失败: {str(e)}")
                continue
            
        # 最终确认
        try:
        final_check = self.index.query(
            data="",
            top_k=10,
            filter=f"set_id = '{str(set_id)}'",
            include_metadata=False,
            include_data=False
        )
        
        logger.info(f"Final check {set_id}, left: {len(final_check) if final_check else 0}")
            return not final_check
        
        except Exception as e:
            logger.error(f"最终确认查询失败: {str(e)}")
            return False
        
    def add_coglet(self, set_id: str, content: str, metadata: Dict[str, Any]) -> str:
        """
        添加新的认元
        
        Args:
            set_id: 认元集合ID
            content: 认元内容
            metadata: 认元元数据
            
        Returns:
            str: 新认元的ID
            
        Raises:
            ValueError: 当必要参数为空时
        """
        if not set_id or not content:
            raise ValueError("set_id和content不能为空")
            
        if metadata is None:
            metadata = {}
            
        # 生成基于内容的 ID
        coglet_id = generate_id(prefix=set_id)
        
        logger.info(f"Add coglet: {coglet_id} to set: {set_id}")
        
        try:
            # 准备元数据
            full_metadata = self._prepare_metadata(set_id, metadata)
            
            # 使用 Vector 类构建数据
            vector = Vector(
                id=coglet_id,
                data=str(content),
                metadata=full_metadata
            )
            
            # 添加认元
            success = self.index.upsert(vectors=[vector])
            if not success:
                raise RuntimeError("向量存储操作未返回成功状态")
                
            logger.debug(f"认元{coglet_id}已写入向量库")
            return coglet_id
            
        except Exception as e:
            logger.error(f"添加认元失败: {str(e)}")
            raise
            
    def _prepare_metadata(self, set_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备元数据，确保所有值都可以被序列化
        
        Args:
            set_id: 认元集合ID
            metadata: 原始元数据
            
        Returns:
            Dict[str, Any]: 处理后的元数据
        """
        full_metadata = {
            "set_id": str(set_id),
            "created_at": datetime.now().isoformat()
        }
        
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                full_metadata[str(key)] = value
            else:
                full_metadata[str(key)] = json.dumps(value)
        
        return full_metadata
        
    def add_coglets(self, set_id: str, items: List[Dict[str, Any]]) -> List[str]:
        """
        批量添加认元
        
        Args:
            set_id: 认元集合ID
            items: 认元列表，每个项目包含 content 和 metadata
            
        Returns:
            List[str]: 新认元的ID列表
            
        Raises:
            ValueError: 当必要参数为空或无效时
        """
        if not set_id or not items:
            raise ValueError("set_id和items不能为空")
            
        logger.info(f"批量添加认元到集合: {set_id}，数量: {len(items)}")
        vectors = []
        coglet_ids = []
        
        try:
        for item in items:
                if not isinstance(item, dict) or "content" not in item:
                    raise ValueError("每个item必须是包含content的字典")
                    
                # 生成ID
                coglet_id = generate_id(prefix=set_id)
            coglet_ids.append(coglet_id)
            
            # 准备元数据
                metadata = item.get("metadata", {})
                full_metadata = self._prepare_metadata(set_id, metadata)
            
            vectors.append(Vector(
                id=coglet_id,
                data=str(item["content"]),
                metadata=full_metadata
            ))
            
            # 批量添加
            success = self.index.upsert(vectors=vectors)
            if not success:
                raise RuntimeError("向量存储操作未返回成功状态")
                
        logger.debug(f"批量认元已写入向量库: {coglet_ids}")
        return coglet_ids
        
        except Exception as e:
            logger.error(f"批量添加认元失败: {str(e)}")
            raise
            
    def get_coglet(self, coglet_id: str) -> Dict[str, Any]:
        """
        获取指定认元的信息
        
        Args:
            coglet_id: 认元ID
            
        Returns:
            Dict[str, Any]: 认元信息，包含内容和元数据
            
        Raises:
            ValueError: 当coglet_id为空时
            KeyError: 当认元不存在时
        """
        if not coglet_id:
            raise ValueError("coglet_id不能为空")
            
        logger.info(f"Get coglet: {coglet_id}")
        
        try:
        result = self.index.fetch(
            ids=[str(coglet_id)],
            include_metadata=True,
            include_data=True
        )
        
            if not result or not result[0]:
            logger.warning(f"Coglet not found: {coglet_id}")
            raise KeyError(f"Coglet {coglet_id} not found")
        
        vector_result = result[0]
        content = str(vector_result.data or "")
        metadata = vector_result.metadata or {}
        
        return {
            "content": content,
                "metadata": self._process_metadata(metadata)
        }
            
        except Exception as e:
            if isinstance(e, KeyError):
                raise
            logger.error(f"获取认元失败: {str(e)}")
            raise
        
    def update_coglet(self, coglet_id: str, metadata: Dict[str, Any]) -> bool:
        """
        更新认元的元数据
        
        Args:
            coglet_id: 认元ID
            metadata: 新的元数据
        
        Returns:
            bool: 操作是否成功
            
        Raises:
            ValueError: 当必要参数为空时
            KeyError: 当认元不存在时
        """
        if not coglet_id:
            raise ValueError("coglet_id不能为空")
            
        if metadata is None:
            metadata = {}
            
        logger.info(f"Update coglet: {coglet_id}")
        
        try:
            # 检查认元是否存在
        result = self.index.fetch(
            ids=[str(coglet_id)],
            include_metadata=True,
                include_data=False
        )
            
            if not result or not result[0]:
            logger.error(f"Coglet not found: {coglet_id}")
            raise KeyError(f"Coglet {coglet_id} not found")
                
            # 更新元数据
        metadata = dict(metadata)
        metadata["updated_at"] = datetime.now().isoformat()
            
            success = self.index.update(id=coglet_id, metadata=metadata)
            return bool(success)
            
        except Exception as e:
            if isinstance(e, KeyError):
                raise
            logger.error(f"更新认元失败: {str(e)}")
            return False
        
    def delete_coglet(self, coglet_id: str) -> bool:
        """
        删除指定的认元
        
        Args:
            coglet_id: 认元ID
        
        Returns:
            bool: 操作是否成功
            
        Raises:
            ValueError: 当coglet_id为空时
        """
        if not coglet_id:
            raise ValueError("coglet_id不能为空")
            
        logger.info(f"Delete coglet: {coglet_id}")
        
        try:
            result = self.index.delete(ids=[coglet_id])
            return getattr(result, "deleted", 0) >= 0
            
        except Exception as e:
            logger.error(f"删除认元失败: {str(e)}")
            return False
        
    def delete_coglets(self, coglet_ids: List[str]) -> bool:
        """
        批量删除认元
        
        Args:
            coglet_ids: 认元ID列表
        
        Returns:
            bool: 操作是否成功
            
        Raises:
            ValueError: 当coglet_ids为空时
        """
        if not coglet_ids:
            raise ValueError("coglet_ids不能为空")
            
        logger.info(f"Batch delete: {coglet_ids}")
        
        try:
            result = self.index.delete(ids=coglet_ids)
            return getattr(result, "deleted", 0) >= 0
            
        except Exception as e:
            logger.error(f"批量删除失败: {str(e)}")
            return False
        
    def search_similar(
        self,
        set_id: str,
        query: str,
        top_k: int = 10,
        similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        在指定认元集合中搜索相似认元
        
        Args:
            set_id: 认元集合ID
            query: 查询文本
            top_k: 返回结果数量
            similarity_threshold: 相似度阈值，0-1之间
        
        Returns:
            List[Dict[str, Any]]: 相似认元列表
            
        Raises:
            ValueError: 当必要参数为空或无效时
        """
        if not set_id or not query:
            raise ValueError("set_id和query不能为空")
            
        if top_k < 1:
            raise ValueError("top_k必须大于0")
            
        if not 0 <= similarity_threshold <= 1:
            raise ValueError("similarity_threshold必须在0-1之间")
            
        logger.info(f"Search: set={set_id}, query={query}, top_k={top_k}")
        
        try:
            # 添加小延迟，确保索引已更新
            time.sleep(0.5)
            
            # 尝试多次查询以提高成功率
            results = None
            for attempt in range(2):
                results = self.index.query(
                    data=query,
                    top_k=top_k,
                    filter=f"set_id = '{str(set_id)}'",
                    include_metadata=True,
                    include_data=True
                )
                if results:
                    break
                time.sleep(1)
                
            logger.debug(f"Search result: {len(results) if results else 0}")
            
            if not results:
                return []
                
            output = []
            for r in results:
                score = getattr(r, "score", 0.0)
                if score >= similarity_threshold:
                output.append({
                    "coglet_id": r.id,
                    "id": r.id,
                    "content": r.data,
                    "metadata": self._process_metadata(r.metadata),
                        "score": score
                })
            return output
            
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []
    
    def _process_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理元数据，尝试将 JSON 字符串转换回原始类型
        
        Args:
            metadata: 原始元数据
            
        Returns:
            Dict[str, Any]: 处理后的元数据
        """
        if not metadata:
            return {}
            
        processed = {}
        for key, value in metadata.items():
            if key in ["set_id", "created_at", "updated_at"]:
                processed[key] = value
                continue
                
            if isinstance(value, str):
                try:
                    processed[key] = json.loads(value)
                except json.JSONDecodeError:
                    processed[key] = value
            else:
                processed[key] = value
        return processed 