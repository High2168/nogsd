"""
推荐算法包

包含:
    - UserBasedCF: 基于用户的协同过滤
    - ItemBasedCF: 基于物品的协同过滤
    - ColdStartHandler: 冷启动处理
    - HybridRecommender: 混合推荐器

作者: 刘怀仁
"""

from .user_based_cf import UserBasedCF
from .item_based_cf import ItemBasedCF
from .cold_start import ColdStartHandler
from .hybrid import HybridRecommender

__all__ = [
    'UserBasedCF',
    'ItemBasedCF',
    'ColdStartHandler',
    'HybridRecommender'
]
