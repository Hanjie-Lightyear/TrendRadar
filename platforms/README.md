# 平台模块架构

## 目录结构

```
platforms/
├── __init__.py              # 模块导出
├── base.py                   # 平台抽象基类（通用代码）
├── factory.py                # 平台工厂（通用代码）
├── data_fetcher.py          # 数据获取器（通用代码）
├── sources/                  # 数据源实现（具体平台实现）
│   ├── __init__.py          # 数据源导出
│   ├── newsnow.py           # NewsNow 平台实现
│   └── blockbeats_news.py  # BlockBeats 平台实现
├── config_example.yaml       # 配置示例
└── example_usage.py          # 使用示例
```

## 架构说明

### 通用代码层（platforms/）

**职责**：提供平台抽象框架，不包含具体数据源实现

- `base.py` - 定义 `BasePlatform` 抽象基类
- `factory.py` - 平台工厂，负责创建平台实例
- `data_fetcher.py` - 统一数据获取器，调用平台接口

### 数据源实现层（platforms/sources/）

**职责**：各种平台的具体实现

- `newsnow.py` - NewsNow API 平台实现（11个平台类）
- `blockbeats_news.py` - BlockBeats API 平台实现

## 设计优势

1. **职责分离**
   - 通用代码：框架和接口定义
   - 数据源实现：具体平台的采集逻辑

2. **易于扩展**
   - 添加新数据源只需在 `sources/` 目录添加文件
   - 无需修改通用代码

3. **结构清晰**
   - 通用代码和数据源实现分离
   - 目录结构一目了然

4. **维护方便**
   - 数据源实现独立，互不影响
   - 通用代码稳定，修改频率低

## 添加新数据源

### 步骤 1：创建数据源文件

```python
# platforms/sources/my_platform.py
from ..base import BasePlatform
from typing import Dict, Optional, Tuple

class MyPlatform(BasePlatform):
    """我的平台"""
    
    def fetch_data(self, **kwargs) -> Tuple[Optional[Dict], str, str]:
        # 实现数据获取逻辑
        pass
```

### 步骤 2：在 sources/__init__.py 中导出

```python
from .my_platform import MyPlatform

__all__ = [
    # ... 现有平台
    "MyPlatform",
]
```

### 步骤 3：在 factory.py 中注册

```python
from .sources import MyPlatform

PLATFORM_REGISTRY = {
    # ... 现有注册
    "my_platform": MyPlatform,
}
```

## 导入路径

### 从外部导入（推荐）

```python
from platforms import DataFetcherV2, create_platform
```

### 从内部导入（数据源实现中）

```python
# 在 platforms/sources/xxx.py 中
from ..base import BasePlatform
from ..factory import PLATFORM_REGISTRY
```

## 文件说明

| 文件 | 类型 | 说明 |
|------|------|------|
| `base.py` | 通用 | 平台抽象基类 |
| `factory.py` | 通用 | 平台工厂和注册表 |
| `data_fetcher.py` | 通用 | 统一数据获取器 |
| `sources/newsnow.py` | 实现 | NewsNow 平台实现 |
| `sources/blockbeats_news.py` | 实现 | BlockBeats 平台实现 |

## 总结

新的目录结构实现了：
- ✅ 通用代码与数据源实现解耦
- ✅ 清晰的职责划分
- ✅ 易于扩展和维护
- ✅ 符合单一职责原则

