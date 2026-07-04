"""
rental-shield 数据库模型模块
使用 SQLAlchemy ORM 定义 four 张核心表：houses, reviews, price_history, landlords
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

import config

# ============================================================
# 数据库引擎 & 会话工厂
# ============================================================
engine = create_engine(config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# ============================================================
# 表1：房源信息表 houses
# ============================================================
class House(Base):
    """房源主表，存储每个出租房源的核心属性"""
    __tablename__ = "houses"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="房源唯一ID")
    title = Column(String(200), nullable=False, comment="房源标题")
    district = Column(String(20), nullable=False, comment="所属区域（天河/海珠等）")
    community = Column(String(100), comment="小区名称")
    layout = Column(String(20), comment="户型（一室/两室/三室及以上）")
    area = Column(Float, comment="建筑面积（平方米）")
    price = Column(Integer, comment="月租（元）")
    floor = Column(Integer, comment="所在楼层")
    total_floors = Column(Integer, comment="总楼层数")
    orientation = Column(String(10), comment="朝向（南/北/东南等）")
    window_type = Column(String(10), default="普通窗", comment="窗户类型（落地窗/普通窗/小窗）")
    building_type = Column(String(10), comment="建筑类型（塔楼/板楼/自建房）")
    building_year = Column(Integer, comment="建筑年代")
    distance_to_street = Column(Integer, comment="距主街道距离（米）")
    has_business_below = Column(Boolean, default=False, comment="是否有底商")
    landlord_phone_hash = Column(String(64), comment="房东手机号哈希，关联 landlords 表")
    source_url = Column(String(500), comment="房源来源链接")
    created_at = Column(DateTime, default=datetime.now, comment="入库时间")

    # 关联：一个房源有多条评论、价格记录和图片
    reviews = relationship("Review", back_populates="house", cascade="all, delete-orphan")
    price_records = relationship("PriceHistory", back_populates="house", cascade="all, delete-orphan")
    images = relationship("ListingImage", back_populates="house", cascade="all, delete-orphan")


# ============================================================
# 表2：评论信息表 reviews
# ============================================================
class Review(Base):
    """租客评论表，存储各平台抓取的评论内容"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="评论唯一ID")
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False, comment="关联房源ID")
    platform = Column(String(20), comment="评论来源平台（小红书/豆瓣/链家）")
    content = Column(Text, comment="评论原文")
    rating = Column(Integer, comment="评分（1-5）")
    created_at = Column(DateTime, default=datetime.now, comment="评论时间")

    house = relationship("House", back_populates="reviews")


# ============================================================
# 表3：价格历史表 price_history
# ============================================================
class PriceHistory(Base):
    """价格变动记录表，追踪同一房源的价格变化"""
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="记录唯一ID")
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False, comment="关联房源ID")
    price = Column(Integer, comment="历史价格（元/月）")
    record_date = Column(DateTime, default=datetime.now, comment="记录日期")

    house = relationship("House", back_populates="price_records")


# ============================================================
# 表4：房东信息表 landlords
# ============================================================
class Landlord(Base):
    """房东信息表，记录房东类型、投诉次数和风险标签"""
    __tablename__ = "landlords"

    phone_hash = Column(String(64), primary_key=True, comment="手机号哈希，唯一标识")
    name = Column(String(50), comment="房东称呼")
    type = Column(String(20), comment="房东类型（一手房东/二房东/公寓托管/中介）")
    complaint_count = Column(Integer, default=0, comment="历史投诉次数")
    risk_tags = Column(String(200), comment="风险标签，逗号分隔")


# ============================================================
# 表5：房源图片表 listing_images
# ============================================================
class ListingImage(Base):
    """房源图片表，存储从租房平台抓取的房源实拍图片路径"""
    __tablename__ = "listing_images"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="图片唯一ID")
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False, comment="关联房源ID")
    image_path = Column(String(500), comment="本地图片相对路径，如 images/1/001.jpg")
    source_url = Column(Text, comment="图片来源URL（原始链家/贝壳链接）")
    sort_order = Column(Integer, default=0, comment="排序序号（1-10）")
    is_primary = Column(Boolean, default=False, comment="是否为主图/封面")
    created_at = Column(DateTime, default=datetime.now, comment="抓取时间")

    house = relationship("House", back_populates="images")


# ============================================================
# 数据库工具函数
# ============================================================

def init_db():
    """初始化数据库，创建所有表（如果不存在则创建）"""
    Base.metadata.create_all(bind=engine)


def get_session():
    """获取一个新的数据库会话"""
    return SessionLocal()


def get_houses_by_filter(districts=None, layout=None, min_price=0, max_price=99999):
    """
    根据筛选条件查询房源列表

    参数：
        districts: 区域列表，如 ["天河", "海珠"]。None 表示不限区域
        layout: 户型筛选，如 "一室"。None 表示不限户型
        min_price: 最低月租
        max_price: 最高月租

    返回：
        房源对象列表
    """
    session = get_session()
    query = session.query(House)

    # 区域筛选：如果指定了区域列表，则条件过滤
    if districts:
        query = query.filter(House.district.in_(districts))

    # 户型筛选：如果指定了户型，精确匹配
    if layout and layout != "不限":
        query = query.filter(House.layout == layout)

    # 价格范围筛选
    query = query.filter(House.price >= min_price, House.price <= max_price)

    results = query.all()
    session.close()
    return results


def get_house_by_id(house_id):
    """
    根据ID获取单个房源详情

    参数：
        house_id: 房源ID

    返回：
        House 对象，如果不存在返回 None
    """
    session = get_session()
    house = session.query(House).filter(House.id == house_id).first()
    session.close()
    return house


def get_house_reviews(house_id):
    """
    获取指定房源的所有评论

    参数：
        house_id: 房源ID

    返回：
        Review 对象列表
    """
    session = get_session()
    reviews = session.query(Review).filter(Review.house_id == house_id).all()
    session.close()
    return reviews


def get_landlord_by_phone(phone_hash):
    """
    根据手机号哈希获取房东信息

    参数：
        phone_hash: 手机号哈希值

    返回：
        Landlord 对象，如果不存在返回 None
    """
    session = get_session()
    landlord = session.query(Landlord).filter(Landlord.phone_hash == phone_hash).first()
    session.close()
    return landlord


def get_houses_by_landlord(phone_hash):
    """
    获取某房东名下的所有房源

    参数：
        phone_hash: 手机号哈希值

    返回：
        House 对象列表
    """
    session = get_session()
    houses = session.query(House).filter(House.landlord_phone_hash == phone_hash).all()
    session.close()
    return houses


def get_house_images(house_id):
    """
    获取指定房源的所有图片，按排序序号升序排列

    参数：
        house_id: 房源ID

    返回：
        ListingImage 对象列表（按 sort_order 升序）
    """
    session = get_session()
    images = session.query(ListingImage).filter(
        ListingImage.house_id == house_id
    ).order_by(ListingImage.sort_order).all()
    session.close()
    return images
