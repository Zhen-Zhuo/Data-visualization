import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, Patch, Circle, Wedge
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import make_interp_spline
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
st.set_page_config(
    page_title="ERP订单数据可视化面板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

@st.cache_data
def load_data(file_path='erp_order_data.xlsx'):
    try:
        df = pd.read_excel(file_path)
        
        REGION_MAPPING = {
            '北京': '华北', '天津': '华北', '河北省': '华北', '山西省': '华北', '内蒙古自治区': '华北',
            '辽宁省': '东北', '吉林省': '东北', '黑龙江省': '东北',
            '上海': '华东', '江苏省': '华东', '浙江省': '华东', '安徽省': '华东', '福建省': '华东',
            '江西省': '华东', '山东省': '华东',
            '河南省': '华中', '湖北省': '华中', '湖南省': '华中',
            '广东省': '华南', '广西壮族自治区': '华南', '海南省': '华南',
            '重庆': '西南', '四川省': '西南', '贵州省': '西南', '云南省': '西南', '西藏自治区': '西南',
            '陕西省': '西北', '甘肃省': '西北', '青海省': '西北', '宁夏回族自治区': '西北', '新疆维吾尔自治区': '西北'
        }
        
        # 处理区域
        if 'province' in df.columns:
            if 'region' in df.columns:
                df['region'] = df['region'].fillna(df['province'].map(REGION_MAPPING))
            else:
                df['region'] = df['province'].map(REGION_MAPPING)
        df['region'] = df['region'].fillna('其他')
        
        # 处理日期
        date_candidates = ['payment_date', 'order_date', 'create_time', 'created_at', 'date']
        for col in date_candidates:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 识别主日期列
        primary_date = next((c for c in date_candidates if c in df.columns), None)
        if primary_date:
            df['_primary_date'] = df[primary_date]
            df['year'] = df['_primary_date'].dt.year
            df['month'] = df['_primary_date'].dt.month
            df['quarter'] = df['_primary_date'].dt.quarter
        
        # 处理金额
        amount_candidates = ['paid_amount', 'product_amount', 'amount', 'total_amount']
        amount_col = next((c for c in amount_candidates if c in df.columns), None)
        if amount_col is None and {'quantity', 'unit_price'}.issubset(df.columns):
            df['_amount'] = df['quantity'] * df['unit_price']
        elif amount_col:
            df['_amount'] = df[amount_col]
        
        # 处理数量
        if 'quantity' in df.columns:
            df['_quantity'] = df['quantity']
        
        return df
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return None

def sidebar_filters(df):
    """侧边栏筛选器"""
    st.sidebar.header("📌 数据筛选")
    
    # 年份筛选
    if 'year' in df.columns:
        years = sorted(df['year'].dropna().unique())
        selected_years = st.sidebar.multiselect(
            "选择年份",
            options=years,
            default=years
        )
    else:
        selected_years = None
    
    # 区域筛选
    regions = sorted(df['region'].unique())
    selected_regions = st.sidebar.multiselect(
        "选择区域",
        options=regions,
        default=regions
    )
    
    # 产品筛选
    if 'product_name' in df.columns:
        products = sorted(df['product_name'].dropna().unique())
        if len(products) <= 50:
            selected_products = st.sidebar.multiselect(
                "选择产品",
                options=products,
                default=products[:10] if len(products) > 10 else products
            )
        else:
            selected_products = None
    else:
        selected_products = None
    
    filtered_df = df.copy()
    if selected_years:
        filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
    if selected_regions:
        filtered_df = filtered_df[filtered_df['region'].isin(selected_regions)]
    if selected_products:
        filtered_df = filtered_df[filtered_df['product_name'].isin(selected_products)]
    
    return filtered_df

def plot_regional_gradient_bars(df):
    """区域销量渐变柱状图"""
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#1e1e2e')
    ax.set_facecolor('#1e1e2e')
    
    qty_col = '_quantity' if '_quantity' in df.columns else '_amount'
    region_stats = df.groupby('region', as_index=False).agg(
        total_quantity=(qty_col, 'sum'),
        order_count=('region', 'count')
    ).sort_values('total_quantity', ascending=False)
    
    regions = region_stats['region'].tolist()
    quantities = region_stats['total_quantity'].tolist()
    
    bar_width = 0.45
    gradient_steps = 100
    cmap = plt.cm.Blues
    layer_ratios = np.linspace(0, 1, gradient_steps, endpoint=False)
    
    for i, qty in enumerate(quantities):
        layer_height = qty / gradient_steps
        for ratio in layer_ratios:
            y_position = ratio * qty
            color = cmap(0.4 + ratio * 0.55)
            rect = Rectangle((i - bar_width/2, y_position), bar_width, layer_height,
                           facecolor=color, edgecolor='none')
            ax.add_patch(rect)
        ax.text(i, qty + max(quantities)*0.02, f'{int(qty):,}',
               ha='center', va='bottom', fontsize=16, fontweight='bold', color='white')
    
    ax.set_xticks(range(len(regions)))
    ax.set_xticklabels(regions, fontsize=15, color='white')
    ax.set_xlim(-0.5, len(regions) - 0.5)
    ax.set_ylim(0, max(quantities) * 1.15)
    ax.set_ylabel('销售数量', fontsize=16, fontweight='bold', color='white')
    ax.tick_params(axis='y', colors='white', labelsize=13)
    ax.grid(axis='y', linestyle='--', alpha=0.3, color='gray', zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    total_qty = region_stats['total_quantity'].sum()
    top_region = region_stats.iloc[0]
    percentage = top_region['total_quantity'] / total_qty * 100
    ax.text(0.5, 1.05, '各区域销量分布（渐变柱状图）',
           transform=ax.transAxes, fontsize=24, fontweight='bold', ha='center', color='white')
    ax.text(0.5, 1.00, f"{top_region['region']}销量最多占比{percentage:.0f}%",
           transform=ax.transAxes, fontsize=16, ha='center', color='#89b4fa')
    
    plt.tight_layout()
    return fig

def plot_top_products(df, n=10):
    """Top N 产品销量"""
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('#0b1430')
    ax.set_facecolor('#0b1430')
    
    value_col = '_quantity' if '_quantity' in df.columns else '_amount'
    product_col = 'product_name' if 'product_name' in df.columns else 'category'
    
    if product_col not in df.columns:
        st.warning("数据中没有产品或类别列")
        return None
    
    top_products = df.groupby(product_col, as_index=False)[value_col].sum().sort_values(
        value_col, ascending=False
    ).head(n)
    
    products = top_products[product_col].tolist()
    values = top_products[value_col].tolist()
    
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(products)))
    bars = ax.barh(products, values, color=colors, edgecolor='white', linewidth=1.2)
    
    for bar, val in zip(bars, values):
        ax.text(val + max(values)*0.01, bar.get_y() + bar.get_height()/2,
               f'{val:,.0f}', va='center', ha='left', color='white', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('销量', fontsize=14, color='white', fontweight='bold')
    ax.set_title(f'Top {n} 产品销量排行', fontsize=18, color='white', fontweight='bold', pad=20)
    ax.tick_params(colors='white', labelsize=11)
    ax.grid(axis='x', linestyle='--', alpha=0.3, color='gray')
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    return fig

def plot_monthly_trend(df):
    """月度销售趋势"""
    if '_primary_date' not in df.columns:
        st.warning("数据中没有有效的日期列")
        return None
    
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor('#0a0e1a')
    ax.set_facecolor('#0a0e1a')
    
    value_col = '_amount' if '_amount' in df.columns else '_quantity'
    
    # 按月汇总
    df_month = df.dropna(subset=['_primary_date']).copy()
    df_month['year_month'] = df_month['_primary_date'].dt.to_period('M')
    monthly = df_month.groupby('year_month')[value_col].sum().reset_index()
    monthly['year_month'] = monthly['year_month'].dt.to_timestamp()
    
    if len(monthly) < 2:
        st.warning("数据点不足,无法绘制趋势图")
        return None
    
    x = np.arange(len(monthly))
    y = monthly[value_col].values
    
    # 使用样条插值平滑曲线
    if len(monthly) > 3:
        x_smooth = np.linspace(x.min(), x.max(), 300)
        spl = make_interp_spline(x, y, k=min(3, len(monthly)-1))
        y_smooth = spl(x_smooth)
        ax.plot(x_smooth, y_smooth, color='#4edbbf', linewidth=3, zorder=3)
    else:
        ax.plot(x, y, color='#4edbbf', linewidth=3, marker='o', markersize=8, zorder=3)
    
    ax.scatter(x, y, color='#ff6b6b', s=100, zorder=4, edgecolors='white', linewidth=2)
    
    for xi, yi in zip(x, y):
        ax.text(xi, yi + max(y)*0.03, f'{yi:,.0f}',
               ha='center', va='bottom', color='white', fontsize=10, fontweight='bold')
    
    ax.set_xticks(x[::max(1, len(x)//12)])
    ax.set_xticklabels([d.strftime('%Y-%m') for d in monthly['year_month'].iloc[::max(1, len(x)//12)]],
                       rotation=45, ha='right', color='white', fontsize=10)
    ax.set_ylabel('销售额' if value_col == '_amount' else '销量',
                 fontsize=14, color='white', fontweight='bold')
    ax.set_title('月度销售趋势', fontsize=18, color='white', fontweight='bold', pad=20)
    ax.tick_params(colors='white', labelsize=11)
    ax.grid(axis='y', linestyle='--', alpha=0.3, color='#2b3f63')
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    return fig

def plot_quarterly_comparison(df):
    """季度对比柱状图"""
    if 'quarter' not in df.columns or 'year' not in df.columns:
        st.warning("数据中没有季度信息")
        return None
    
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#0b1430')
    ax.set_facecolor('#0b1430')
    
    value_col = '_amount' if '_amount' in df.columns else '_quantity'
    
    # 按年和季度汇总
    quarterly = df.groupby(['year', 'quarter'], as_index=False)[value_col].sum()
    years = sorted(quarterly['year'].unique())
    
    if len(years) == 0:
        st.warning("没有可用的年度数据")
        return None
    
    x = np.arange(4)  # Q1, Q2, Q3, Q4
    width = 0.8 / len(years) if len(years) > 1 else 0.4
    
    colors = ['#4a90e2', '#4edbbf', '#ff6b6b', '#ffd166']
    for i, year in enumerate(years):
        year_data = quarterly[quarterly['year'] == year]
        values = [year_data[year_data['quarter'] == q][value_col].values[0]
                 if len(year_data[year_data['quarter'] == q]) > 0 else 0
                 for q in range(1, 5)]
        
        offset = (i - len(years)/2 + 0.5) * width if len(years) > 1 else 0
        bars = ax.bar(x + offset, values, width, label=str(year),
                     color=colors[i % len(colors)], alpha=0.85,
                     edgecolor='white', linewidth=1)
        
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, val,
                       f'{val:,.0f}', ha='center', va='bottom',
                       color='white', fontsize=9, fontweight='bold')
    
    ax.set_xticks(x)
    ax.set_xticklabels([f'Q{i}' for i in range(1, 5)], color='white', fontsize=12)
    ax.set_ylabel('销售额' if value_col == '_amount' else '销量',
                 fontsize=14, color='white', fontweight='bold')
    ax.set_title('季度销售对比', fontsize=18, color='white', fontweight='bold', pad=20)
    ax.legend(frameon=False, fontsize=11, labelcolor='white')
    ax.tick_params(colors='white', labelsize=11)
    ax.grid(axis='y', linestyle='--', alpha=0.3, color='#2b3f63')
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    return fig

def plot_rose_chart(df):
    """南丁格尔玫瑰图"""
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    fig.patch.set_facecolor('#0b1430')
    ax.set_facecolor('#0b1430')
    
    value_col = '_quantity' if '_quantity' in df.columns else '_amount'
    category_col = 'category' if 'category' in df.columns else 'region'
    
    agg = df.groupby(category_col, as_index=False)[value_col].sum().sort_values(
        value_col, ascending=False
    ).head(12)
    
    labels = agg[category_col].astype(str).tolist()
    values = agg[value_col].astype(float).tolist()
    
    if not values:
        st.warning("没有足够的数据绘制玫瑰图")
        return None
    
    theta = np.linspace(0, 2*np.pi, len(values), endpoint=False)
    width = 2*np.pi / len(values)
    
    colors = plt.cm.Spectral(np.linspace(0.1, 0.9, len(values)))
    bars = ax.bar(theta, values, width=width, color=colors, alpha=0.85,
                  edgecolor='white', linewidth=2)
    
    ax.set_xticks(theta)
    ax.set_xticklabels(labels, color='white', fontsize=10)
    ax.set_ylim(0, max(values) * 1.1)
    ax.set_title('分类销量南丁格尔玫瑰图', fontsize=18, color='white',
                fontweight='bold', pad=30, y=1.08)
    ax.tick_params(colors='white')
    ax.grid(color='#2b3f63', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    return fig

def main():
    """主函数"""
    st.title("📊 ERP订单数据交互式可视化面板")
    
    # 加载数据
    df = load_data()
    
    if df is None:
        st.error("❌ 数据加载失败,请检查数据文件是否存在")
        st.stop()
    
    # 应用筛选
    filtered_df = sidebar_filters(df)
    
    # 显示数据概览
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 数据概览")
    st.sidebar.metric("总记录数", f"{len(filtered_df):,}")
    if '_amount' in filtered_df.columns:
        st.sidebar.metric("总销售额", f"¥{filtered_df['_amount'].sum():,.2f}")
    if '_quantity' in filtered_df.columns:
        st.sidebar.metric("总销量", f"{filtered_df['_quantity'].sum():,.0f}")
    
    # 导航标签
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🌏 区域分析", "📦 产品分析", "📅 时间趋势",
        "📊 季度对比", "🌸 玫瑰图", "📋 原始数据"
    ])
    
    with tab1:
        st.subheader("区域销售分析")
        with st.spinner("正在生成图表..."):
            fig = plot_regional_gradient_bars(filtered_df)
            if fig:
                st.pyplot(fig)
                plt.close()
        
        # 显示区域统计表
        st.markdown("#### 区域详细统计")
        qty_col = '_quantity' if '_quantity' in filtered_df.columns else '_amount'
        region_stats = filtered_df.groupby('region').agg({
            qty_col: 'sum',
            'region': 'count'
        }).rename(columns={qty_col: '销量', 'region': '订单数'}).sort_values('销量', ascending=False)
        st.dataframe(region_stats.style.format({'销量': '{:,.0f}', '订单数': '{:,.0f}'}))
    
    with tab2:
        st.subheader("产品销售分析")
        n = st.slider("选择显示Top N产品", 5, 50, 10, 5)
        with st.spinner("正在生成图表..."):
            fig = plot_top_products(filtered_df, n)
            if fig:
                st.pyplot(fig)
                plt.close()
    
    with tab3:
        st.subheader("月度销售趋势")
        with st.spinner("正在生成图表..."):
            fig = plot_monthly_trend(filtered_df)
            if fig:
                st.pyplot(fig)
                plt.close()
    
    with tab4:
        st.subheader("季度销售对比")
        with st.spinner("正在生成图表..."):
            fig = plot_quarterly_comparison(filtered_df)
            if fig:
                st.pyplot(fig)
                plt.close()
    
    with tab5:
        st.subheader("南丁格尔玫瑰图")
        with st.spinner("正在生成图表..."):
            fig = plot_rose_chart(filtered_df)
            if fig:
                st.pyplot(fig)
                plt.close()
    
    with tab6:
        st.subheader("原始数据浏览")
        st.dataframe(filtered_df.head(1000), use_container_width=True)
        
        # 导出功能
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下载筛选后的数据 (CSV)",
            data=csv,
            file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
