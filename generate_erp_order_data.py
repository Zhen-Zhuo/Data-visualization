"""
ERP订单数据生成器
使用Faker库生成1000条模拟的服装电商订单数据
"""

from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta

# 初始化Faker，使用中文
fake = Faker('zh_CN')
Faker.seed(42)
random.seed(42)

# 定义服装相关的商品数据（使用服装类目）
CLOTHING_PRODUCTS = [
    {'name': '纯棉圆领T恤', 'spu_prefix': 'TS', 'price_range': (89, 299)},
    {'name': '修身牛仔裤', 'spu_prefix': 'JP', 'price_range': (199, 599)},
    {'name': '连帽卫衣', 'spu_prefix': 'HD', 'price_range': (159, 459)},
    {'name': '休闲衬衫', 'spu_prefix': 'SH', 'price_range': (129, 399)},
    {'name': '运动裤', 'spu_prefix': 'SP', 'price_range': (99, 359)},
    {'name': '羽绒服', 'spu_prefix': 'DJ', 'price_range': (399, 1299)},
    {'name': '针织衫', 'spu_prefix': 'KN', 'price_range': (149, 499)},
    {'name': '西装外套', 'spu_prefix': 'BZ', 'price_range': (399, 999)},
    {'name': '休闲裤', 'spu_prefix': 'CP', 'price_range': (139, 449)},
    {'name': '连衣裙', 'spu_prefix': 'DR', 'price_range': (179, 699)},
]

COLORS = ['黑色', '白色', '蓝色', '灰色', '红色', '绿色', '黄色', '紫色', '粉色', '米色']
SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
STORE_NAMES = ['时尚潮流旗舰店', '优品服饰专营店', '都市风尚官方店', '经典服装品牌店', '时代服饰旗舰店']
PLATFORMS = ['淘宝', '天猫', '京东', '拼多多', '抖音']
STATUSES = ['已完成', '已完成', '已完成', '已完成', '已完成', '已完成', '待发货', '已发货', '已取消']
SUB_ORDER_STATUSES = ['已完成', '已完成', '已完成', '已完成', '已发货', '待发货']
REFUND_STATUSES = ['无退款', '无退款', '无退款', '无退款', '无退款', '无退款', '无退款', '无退款', '部分退款', '全额退款']
IS_GIFT = ['否', '否', '否', '否', '否', '否', '否', '否', '否', '是']

# 生成固定的用户ID池（200个用户，可以重复购买）
USER_IDS = [f'U{str(i).zfill(8)}' for i in range(1, 201)]

def generate_order_data(num_records=1000):
    """生成订单数据"""
    data = []
    
    for i in range(1, num_records + 1):
        # 选择商品
        product = random.choice(CLOTHING_PRODUCTS)
        color = random.choice(COLORS)
        size = random.choice(SIZES)
        
        # 生成订单号
        internal_order_number = f'IO{datetime.now().strftime("%Y%m%d")}{str(i).zfill(6)}'
        online_order_number = f'ON{fake.random_number(digits=15)}'
        sub_order_number = f'SO{fake.random_number(digits=15)}'
        online_sub_order_number = f'OSO{fake.random_number(digits=15)}'
        original_online_order_number = online_order_number
        
        # 生成SPU和SKU
        spu = f'{product["spu_prefix"]}{fake.random_number(digits=6)}'
        sku = f'{spu}-{color[:1]}-{size}'
        
        # 生成时间（最近一年内）
        order_time = fake.date_time_between(start_date='-1y', end_date='now')
        payment_date = order_time + timedelta(minutes=random.randint(1, 120))
        
        # 发货日期：付款后1-3天内发货
        shipping_date = payment_date + timedelta(days=random.randint(1, 3))
        
        # 价格相关
        original_price = round(random.uniform(product['price_range'][0], product['price_range'][1]), 2)
        unit_price = round(original_price * random.uniform(0.6, 1.0), 2)  # 可能有折扣
        quantity = random.choices([1, 2, 3, 4, 5], weights=[60, 20, 10, 7, 3])[0]
        product_amount = round(unit_price * quantity, 2)
        
        # 应付金额和已付金额（考虑运费等）
        shipping_fee = random.choice([0, 0, 0, 5, 10, 15])
        payable_amount = round(product_amount + shipping_fee, 2)
        paid_amount = payable_amount
        
        # 地址信息
        province = fake.province()
        city = fake.city()
        
        # 退款相关
        refund_status = random.choice(REFUND_STATUSES)
        if refund_status == '无退款':
            registered_quantity = 0
            actual_refund_quantity = 0
        elif refund_status == '部分退款':
            registered_quantity = random.randint(1, quantity)
            actual_refund_quantity = registered_quantity
        else:  # 全额退款
            registered_quantity = quantity
            actual_refund_quantity = quantity
        
        # 构建数据行
        record = {
            'id': i,
            'internal_order_number': internal_order_number,
            'online_order_number': online_order_number,
            'store_name': random.choice(STORE_NAMES),
            'full_channel_user_id': random.choice(USER_IDS),  # 从用户池中随机选择
            'shipping_date': shipping_date,
            'payment_date': payment_date,
            'payable_amount': payable_amount,
            'paid_amount': paid_amount,
            'status': random.choice(STATUSES),
            'consignee': fake.name(),
            'spu': spu,
            'order_time': order_time,
            'province': province,
            'city': city,
            'platform': random.choice(PLATFORMS),
            'sub_order_number': sub_order_number,
            'online_sub_order_number': online_sub_order_number,
            'original_online_order_number': original_online_order_number,
            'sku': sku,
            'quantity': quantity,
            'unit_price': unit_price,
            'product_name': product['name'],
            'color_and_spec': f'{color}/{size}',
            'product_amount': product_amount,
            'original_price': original_price,
            'is_gift': random.choice(IS_GIFT),
            'sub_order_status': random.choice(SUB_ORDER_STATUSES),
            'refund_status': refund_status,
            'registered_quantity': registered_quantity,
            'actual_refund_quantity': actual_refund_quantity,
        }
        
        data.append(record)
    
    return data

def main():
    """主函数"""
    print("开始生成ERP订单数据...")
    
    # 生成数据
    orders = generate_order_data(1000)
    
    # 转换为DataFrame
    df = pd.DataFrame(orders)
    
    # 确保所有字段都没有空值
    print(f"\n数据生成完成，共 {len(df)} 条记录")
    print(f"\n空值检查：")
    null_counts = df.isnull().sum()
    if null_counts.sum() == 0:
        print("✓ 所有字段均无空值")
    else:
        print(null_counts[null_counts > 0])
    
    # 显示用户ID重复情况
    user_counts = df['full_channel_user_id'].value_counts()
    print(f"\n用户购买统计：")
    print(f"  - 唯一用户数: {df['full_channel_user_id'].nunique()}")
    print(f"  - 平均每用户订单数: {len(df) / df['full_channel_user_id'].nunique():.2f}")
    print(f"  - 最多购买用户订单数: {user_counts.max()}")
    
    # 保存到Excel
    output_file = 'erp_order_data.xlsx'
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"\n数据已保存到: {output_file}")
    
    # 显示数据预览
    print(f"\n数据预览（前5行）：")
    print(df.head())
    
    print(f"\n商品分布：")
    print(df['product_name'].value_counts())

if __name__ == '__main__':
    main()
