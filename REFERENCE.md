# 数据可视化参考文档 (Data Visualization Reference)

本文档提供了各种数据可视化类型的参考示例，包括平滑折线图、菱形走势图和月度趋势图等。所有示例均基于 Excel 数据表动态读取，避免硬编码数值。

## 目录
1. [平滑折线图 (Smooth Line Chart)](#平滑折线图-smooth-line-chart)
2. [菱形走势图 (Diamond Chart)](#菱形走势图-diamond-chart)
3. [月度走势图 (Monthly Trend Chart)](#月度走势图-monthly-trend-chart)
4. [数据读取最佳实践](#数据读取最佳实践)
5. [格式化指南](#格式化指南)

---

## 平滑折线图 (Smooth Line Chart)

平滑折线图使用插值技术使线条更加平滑，适合展示趋势变化。

### 示例代码

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# 读取 Excel 数据
df = pd.read_excel('erp_order_data.xlsx')
df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')

# 筛选 2025 年数据并按月汇总
df_2025 = df[df['payment_date'].dt.year == 2025].copy()
monthly_sales = df_2025.groupby(df_2025['payment_date'].dt.month)['paid_amount'].sum()

# 准备数据
months = np.array(monthly_sales.index)
sales = np.array(monthly_sales.values)

# 创建平滑曲线 (使用 B-spline 插值)
if len(months) > 3:
    months_smooth = np.linspace(months.min(), months.max(), 300)
    spl = make_interp_spline(months, sales, k=3)
    sales_smooth = spl(months_smooth)
else:
    months_smooth = months
    sales_smooth = sales

# 绑定图形
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('#0f1730')
ax.set_facecolor('#0f1730')

# 绘制平滑曲线
ax.plot(months_smooth, sales_smooth, color='#4fa5ff', linewidth=2.5, label='2025年销量')

# 绘制原始数据点
ax.scatter(months, sales, color='#7edbf3', s=80, zorder=5, edgecolor='white', linewidth=1.5)

# 添加数据标签
for m, s in zip(months, sales):
    ax.annotate(f'{s:,.0f}', (m, s), textcoords="offset points", 
                xytext=(0, 12), ha='center', fontsize=9, color='white')

# 样式设置
ax.set_xlabel('月份', color='white', fontsize=12)
ax.set_ylabel('销售额 (元)', color='white', fontsize=12)
ax.set_title('2025年月度销售平滑趋势图', color='white', fontsize=16, fontweight='bold', pad=15)
ax.tick_params(colors='white')
ax.grid(True, linestyle='--', alpha=0.3, color='#2b3f63')
for spine in ax.spines.values():
    spine.set_color('#2b3f63')

plt.tight_layout()
plt.show()
```

### 关键参数说明

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `k` | B-spline 阶数 | 3 (三次样条) |
| `linewidth` | 线条宽度 | 2-3 |
| `alpha` | 透明度 | 0.8-1.0 |

---

## 菱形走势图 (Diamond Chart)

菱形走势图使用菱形标记来强调数据点，适合展示关键节点数据。

### 示例代码

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection

# 读取 Excel 数据
df = pd.read_excel('erp_order_data.xlsx')
df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')

# 筛选 2025 年数据并按月汇总
df_2025 = df[df['payment_date'].dt.year == 2025].copy()
monthly_sales = df_2025.groupby(df_2025['payment_date'].dt.month)['paid_amount'].sum()

months = monthly_sales.index.tolist()
sales = monthly_sales.values.tolist()

# 创建图表
fig, ax = plt.subplots(figsize=(14, 7))
fig.patch.set_facecolor('#0f1730')
ax.set_facecolor('#0f1730')

# 绘制连接线
ax.plot(months, sales, color='#4fa5ff', linewidth=2, alpha=0.7, zorder=1)

# 绘制菱形标记
diamond_size = max(sales, default=0) * 0.03 if sales else 0
colors = ['#7edbf3', '#3cb4a1', '#f07a57', '#f4c338', '#4fa5ff', 
          '#1678d8', '#7d66ff', '#9b88ff', '#c94a64', '#5cd65c', '#ff9f40', '#ff6b9d']

patches = []
for i, (m, s) in enumerate(zip(months, sales)):
    # 创建菱形 (45度旋转的正方形)
    diamond = RegularPolygon((m, s), numVertices=4, radius=diamond_size,
                             orientation=np.pi/4, facecolor=colors[i % len(colors)],
                             edgecolor='white', linewidth=2)
    patches.append(diamond)
    ax.add_patch(diamond)
    
    # 添加数值标签
    ax.text(m, s + diamond_size * 1.5, f'{s:,.0f}', ha='center', va='bottom',
            fontsize=10, color='white', fontweight='bold')

# 样式设置
ax.set_xlabel('月份', color='white', fontsize=12)
ax.set_ylabel('销售额 (元)', color='white', fontsize=12)
ax.set_title('2025年月度销售菱形走势图', color='white', fontsize=16, fontweight='bold', pad=15)
ax.set_xticks(months)
ax.set_xticklabels([f'{m}月' for m in months], color='white')
ax.tick_params(colors='white')
ax.set_ylim(0, max(sales, default=0) * 1.2 if sales else 100)
ax.grid(True, linestyle='--', alpha=0.3, color='#2b3f63')
for spine in ax.spines.values():
    spine.set_color('#2b3f63')

plt.tight_layout()
plt.show()
```

### 菱形参数说明

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `numVertices` | 顶点数 | 4 (菱形) |
| `orientation` | 旋转角度 | π/4 (45度) |
| `radius` | 菱形大小 | 数据范围的 2-5% |

---

## 月度走势图 (Monthly Trend Chart)

专门用于展示 2025 年月度销售趋势的图表。

### 示例代码

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# 读取 Excel 数据
df = pd.read_excel('erp_order_data.xlsx')
df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')

# 筛选 2025 年数据
df_2025 = df[df['payment_date'].dt.year == 2025].copy()

# 按月汇总销量
monthly_qty = df_2025.groupby(df_2025['payment_date'].dt.month)['quantity'].sum()

# 创建完整的月份序列 (1-12月)
all_months = range(1, 13)
sales_data = [monthly_qty.get(m, 0) for m in all_months]
month_labels = [f'{m}月' for m in all_months]

# 创建图表
fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor('#0f1730')
ax.set_facecolor('#0f1730')

# 蓝色渐变色
blue_colors = ['#1a5276', '#2471a3', '#2e86c1', '#3498db', '#5dade2', 
               '#85c1e9', '#aed6f1', '#d4e6f1', '#eaf2f8', '#f8fbfd', '#3498db', '#2471a3']

x = np.arange(len(month_labels))
bars = ax.bar(x, sales_data, color=blue_colors[:len(sales_data)], width=0.6, edgecolor='none')

# 在每个柱子上方显示销量 (蓝色单元格样式)
for i, (xi, val) in enumerate(zip(x, sales_data)):
    if val > 0:
        # 蓝色背景单元格
        box_width = 0.5
        box_height = max(sales_data) * 0.08
        box = FancyBboxPatch((xi - box_width/2, val + max(sales_data)*0.02), 
                             box_width, box_height,
                             boxstyle='round,pad=0.02,rounding_size=0.1',
                             facecolor='#3498db', edgecolor='white', linewidth=1)
        ax.add_patch(box)
        ax.text(xi, val + max(sales_data)*0.02 + box_height/2, f'{int(val)}',
                ha='center', va='center', fontsize=10, color='white', fontweight='bold')

# 样式设置
ax.set_xticks(x)
ax.set_xticklabels(month_labels, color='white', fontsize=11)
ax.set_ylabel('销量', color='white', fontsize=12)
ax.set_title('2025年月度销量走势', color='white', fontsize=16, fontweight='bold', pad=15)
ax.tick_params(colors='white')
max_sales = max(sales_data) if sales_data else 0
ax.set_ylim(0, max_sales * 1.25 if max_sales > 0 else 100)
ax.grid(True, axis='y', linestyle='--', alpha=0.3, color='#2b3f63')
for spine in ax.spines.values():
    spine.set_color('#2b3f63')

# 添加注释
ax.text(0.01, -0.1, '*数据来源：ERP订单系统', transform=ax.transAxes, 
        fontsize=9, color='gray', ha='left')

plt.tight_layout()
plt.show()
```

---

## 数据读取最佳实践

### 动态读取 Excel 数据 (避免硬编码)

```python
import pandas as pd

# ✅ 推荐：从 Excel 文件动态读取数据
df = pd.read_excel('erp_order_data.xlsx')

# ✅ 动态获取日期范围
df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')
min_date = df['payment_date'].min()
max_date = df['payment_date'].max()

# ✅ 动态筛选年份
current_year = pd.Timestamp.now().year
df_current = df[df['payment_date'].dt.year == current_year]

# ✅ 动态汇总数据
monthly_sales = df_current.groupby(df_current['payment_date'].dt.month)['paid_amount'].sum()

# ❌ 避免：硬编码数值
# months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
# sales = [15000, 18500, 22000, 19800, 24500, 28000, 31200, 26800, 23500, 21000, 25600, 32000]  # 不推荐
```

### 处理缺失数据

```python
# 填充缺失月份为 0
all_months = range(1, 13)
complete_sales = pd.Series({m: monthly_sales.get(m, 0) for m in all_months})
```

### 区域映射

```python
# 省份到区域的映射
region_mapping = {
    '北京': '华北', '天津': '华北', '河北省': '华北', '山西省': '华北', '内蒙古自治区': '华北',
    '辽宁省': '东北', '吉林省': '东北', '黑龙江省': '东北',
    '上海': '华东', '江苏省': '华东', '浙江省': '华东', '安徽省': '华东', '福建省': '华东',
    '江西省': '华东', '山东省': '华东',
    '河南省': '华中', '湖北省': '华中', '湖南省': '华中',
    '广东省': '华南', '广西壮族自治区': '华南', '海南省': '华南',
    '重庆': '西南', '四川省': '西南', '贵州省': '西南', '云南省': '西南', '西藏自治区': '西南',
    '陕西省': '西北', '甘肃省': '西北', '青海省': '西北', '宁夏回族自治区': '西北', '新疆维吾尔自治区': '西北'
}

df['region'] = df['province'].map(region_mapping).fillna('其他')
```

---

## 格式化指南

### 颜色方案

#### 主色调 (深色背景主题)

| 用途 | 颜色代码 | 示例 |
|------|----------|------|
| 背景色 | `#0f1730` | 深蓝黑色 |
| 网格线 | `#2b3f63` | 深蓝灰色 |
| 主色调 | `#4fa5ff` | 亮蓝色 |
| 强调色 | `#c94a64` | 红色 (用于涨幅等) |
| 文字色 | `#ffffff` | 白色 |

#### 渐变色板

```python
palette = ['#7edbf3', '#3cb4a1', '#f07a57', '#f4c338', '#4fa5ff', 
           '#1678d8', '#7d66ff', '#9b88ff', '#c94a64', '#5cd65c']
```

### 单元格样式

#### 蓝色单元格 (显示销量)

```python
from matplotlib.patches import FancyBboxPatch

# 蓝色圆角矩形
blue_box = FancyBboxPatch(
    (x - width/2, y), width, height,
    boxstyle='round,pad=0.02,rounding_size=0.1',
    facecolor='#3498db',  # 蓝色
    edgecolor='white',
    linewidth=1
)
ax.add_patch(blue_box)
```

#### 红色单元格 (显示涨幅，加宽)

```python
# 红色圆角矩形 (加宽)
red_width = width * 1.5  # 加宽 50%
red_box = FancyBboxPatch(
    (x - red_width/2, y), red_width, height,
    boxstyle='round,pad=0.02,rounding_size=0.1',
    facecolor='#c94a64',  # 红色
    edgecolor='white',
    linewidth=1
)
ax.add_patch(red_box)

# 显示涨幅百分比
growth_text = f'+{growth:.1f}%' if growth >= 0 else f'{growth:.1f}%'
ax.text(x, y + height/2, growth_text, ha='center', va='center',
        color='white', fontsize=10, fontweight='bold')
```

### 字体设置

```python
import matplotlib.pyplot as plt

# 设置中文字体 (包含多个备选字体以确保跨平台兼容性)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
```

### 图表尺寸推荐

| 图表类型 | 推荐尺寸 (英寸) |
|----------|----------------|
| 标准图表 | (12, 6) |
| 宽屏图表 | (14, 6) |
| 详细图表 | (14, 8) |
| 仪表板组件 | (8, 5) |

---

## 常见问题解答

### Q1: 如何确保中文显示正常？

```python
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
```

### Q2: 如何计算同比增长率？

```python
# 同比增长率计算
def calculate_yoy_growth(current, previous):
    if previous == 0:
        return np.nan
    return ((current - previous) / previous) * 100

# 应用到 DataFrame
df_2025['yoy_growth'] = df_2025.apply(
    lambda row: calculate_yoy_growth(row['sales_2025'], row['sales_2024']), axis=1
)
```

### Q3: 如何处理占位符值？

```python
# 使用占位符标记缺失或待定数据
placeholder = '-'

# 在显示时检查
for value in values:
    if pd.isna(value) or value == 0:
        display_text = placeholder
    else:
        display_text = f'{value:,.0f}'
```

---

## 完整示例：综合月度走势图

以下是一个综合示例，结合了上述所有最佳实践：

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from scipy.interpolate import make_interp_spline

# 设置中文字体 (包含多个备选字体以确保跨平台兼容性)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
df = pd.read_excel('erp_order_data.xlsx')
df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')

# 2025年数据
df_2025 = df[df['payment_date'].dt.year == 2025].copy()
monthly_2025 = df_2025.groupby(df_2025['payment_date'].dt.month)['paid_amount'].sum()

# 2024年数据 (用于同比)
df_2024 = df[df['payment_date'].dt.year == 2024].copy()
monthly_2024 = df_2024.groupby(df_2024['payment_date'].dt.month)['paid_amount'].sum()

# 准备完整月份数据
all_months = range(1, 13)
sales_2025 = [monthly_2025.get(m, 0) for m in all_months]
sales_2024 = [monthly_2024.get(m, 0) for m in all_months]

# 计算同比增长率
yoy_growth = []
for s25, s24 in zip(sales_2025, sales_2024):
    if s24 > 0:
        yoy_growth.append(((s25 - s24) / s24) * 100)
    else:
        yoy_growth.append(np.nan)

# 创建图表
fig, ax = plt.subplots(figsize=(14, 7))
fig.patch.set_facecolor('#0f1730')
ax.set_facecolor('#0f1730')

x = np.arange(len(all_months))

# 绘制柱状图
bars = ax.bar(x, sales_2025, color='#4fa5ff', width=0.6, alpha=0.8, label='2025年销售额')

# 添加蓝色销量标签
for xi, val in zip(x, sales_2025):
    if val > 0:
        box_h = max(sales_2025) * 0.06
        box_w = 0.5
        box = FancyBboxPatch((xi - box_w/2, val + max(sales_2025)*0.02), 
                             box_w, box_h,
                             boxstyle='round,pad=0.01,rounding_size=0.08',
                             facecolor='#3498db', edgecolor='white', linewidth=0.5)
        ax.add_patch(box)
        ax.text(xi, val + max(sales_2025)*0.02 + box_h/2, f'{int(val):,}',
                ha='center', va='center', fontsize=9, color='white', fontweight='bold')

# 添加红色涨幅标签 (加宽)
for xi, (val, growth) in enumerate(zip(sales_2025, yoy_growth)):
    if val > 0:
        box_h = max(sales_2025) * 0.06
        box_w = 0.7  # 加宽的红色单元格
        y_pos = val + max(sales_2025)*0.12
        box = FancyBboxPatch((xi - box_w/2, y_pos), 
                             box_w, box_h,
                             boxstyle='round,pad=0.01,rounding_size=0.08',
                             facecolor='#c94a64', edgecolor='white', linewidth=0.5)
        ax.add_patch(box)
        
        if np.isfinite(growth):
            growth_text = f'{growth:+.1f}%'
        else:
            growth_text = '-'
        ax.text(xi, y_pos + box_h/2, growth_text,
                ha='center', va='center', fontsize=9, color='white', fontweight='bold')

# 样式设置
ax.set_xticks(x)
ax.set_xticklabels([f'{m}月' for m in all_months], color='white', fontsize=11)
ax.set_ylabel('销售额 (元)', color='white', fontsize=12)
ax.set_title('2025年月度销售走势及同比增长', color='white', fontsize=16, fontweight='bold', pad=20)
ax.tick_params(colors='white')
max_sales_2025 = max(sales_2025) if sales_2025 else 0
ax.set_ylim(0, max_sales_2025 * 1.35 if max_sales_2025 > 0 else 100)
ax.grid(True, axis='y', linestyle='--', alpha=0.3, color='#2b3f63')
for spine in ax.spines.values():
    spine.set_color('#2b3f63')

# 图例
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#3498db', edgecolor='white', label='销售额'),
    Patch(facecolor='#c94a64', edgecolor='white', label='同比增长率')
]
ax.legend(handles=legend_elements, loc='upper right', facecolor='#0f1730', 
          edgecolor='#2b3f63', labelcolor='white')

# 注释
total_2025 = sum(sales_2025)
total_2024 = sum(sales_2024)
ax.text(0.01, 1.02, f'2025年累计: ¥{total_2025:,.0f}  |  2024年累计: ¥{total_2024:,.0f}',
        transform=ax.transAxes, fontsize=11, color='#9cc9ff', ha='left')
ax.text(0.01, -0.08, '*数据来源：ERP订单系统，动态读取自 erp_order_data.xlsx',
        transform=ax.transAxes, fontsize=9, color='gray', ha='left')

plt.tight_layout()
plt.show()
```

---

## 附录：常用 Matplotlib 参考

### 颜色命名

```python
# 使用十六进制颜色
color = '#4fa5ff'

# 使用 RGB 元组 (0-1 范围)
color = (0.31, 0.65, 1.0)

# 使用 RGBA 元组 (带透明度)
color = (0.31, 0.65, 1.0, 0.8)
```

### FancyBboxPatch 样式

```python
boxstyle_options = [
    'round',           # 圆角矩形
    'round4',          # 四角圆角
    'roundtooth',      # 锯齿边缘
    'sawtooth',        # 锯齿
    'square',          # 正方形
]
```

---

*本文档最后更新：2025年*
