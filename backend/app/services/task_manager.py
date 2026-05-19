"""
AI任务管理器 - 支持任务取消功能
"""
import threading
from typing import Dict, Set
from app.core.logger import get_logger

logger = get_logger(__name__)


class TaskManager:
    """管理AI任务的运行状态和取消信号"""
    
    def __init__(self):
        # 存储需要取消的任务ID集合
        self._cancel_tasks: Set[int] = set()
        # 线程锁，保证线程安全
        self._lock = threading.Lock()
    
    def request_cancel(self, task_id: int):
        """请求取消任务"""
        with self._lock:
            self._cancel_tasks.add(task_id)
        logger.info(f"任务取消请求已提交 | 任务ID: {task_id}")
    
    def is_cancelled(self, task_id: int) -> bool:
        """检查任务是否被取消"""
        with self._lock:
            return task_id in self._cancel_tasks
    
    def clear_cancel(self, task_id: int):
        """清除取消标记（任务完成或重新开始时调用）"""
        with self._lock:
            self._cancel_tasks.discard(task_id)
    
    def cleanup(self, task_id: int):
        """清理任务相关的所有状态"""
        self.clear_cancel(task_id)


# 全局任务管理器实例
task_manager = TaskManager()
