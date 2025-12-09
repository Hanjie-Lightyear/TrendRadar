# 测试说明

本目录包含 TrendRadar 项目的单元测试。

## 测试内容

### test_deduplication.py

测试跨平台去重功能，包括：

1. **标题相似度计算** (`_calculate_title_similarity`)
   - 完全相同标题
   - 大小写不敏感
   - 相似标题识别
   - 词序不敏感（RapidFuzz token_sort_ratio）
   - 不同标题区分

2. **URL标准化** (`_normalize_url`)
   - HTTP/HTTPS协议处理
   - www前缀处理
   - 末尾斜杠处理
   - 大小写不敏感

3. **跨平台去重** (`_deduplicate_cross_platform`)
   - 完全相同标题去重
   - 相同URL去重
   - 相似标题去重
   - ranks合并
   - URL保留
   - 移动端URL处理
   - 相似度阈值测试

## 运行测试

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行所有测试

```bash
# 使用 pytest
pytest tests/

# 或使用 unittest
python -m pytest tests/
```

### 运行特定测试文件

```bash
pytest tests/test_deduplication.py
```

### 运行特定测试类

```bash
pytest tests/test_deduplication.py::TestTitleSimilarity
```

### 运行特定测试方法

```bash
pytest tests/test_deduplication.py::TestTitleSimilarity::test_identical_titles
```

### 查看详细输出

```bash
pytest tests/ -v
```

### 查看覆盖率

```bash
# 需要先安装 pytest-cov
pip install pytest-cov
pytest tests/ --cov=main --cov-report=html
```

## 测试示例

```python
# 测试标题相似度
from main import _calculate_title_similarity

# 完全相同
similarity = _calculate_title_similarity("苹果发布新iPhone", "苹果发布新iPhone")
assert similarity == 1.0

# 词序不同但内容相同
similarity = _calculate_title_similarity("苹果发布新手机", "新手机苹果发布")
assert similarity > 0.85  # RapidFuzz token_sort_ratio 的优势
```

## 注意事项

1. 测试需要安装 `rapidfuzz` 库
2. 测试会导入 `main.py` 中的函数，确保项目根目录在 Python 路径中
3. 某些测试可能需要根据实际数据调整相似度阈值
