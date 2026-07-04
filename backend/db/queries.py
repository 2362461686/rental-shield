"""数据库查询函数（接收 Session 参数，由路由层注入）"""
from sqlalchemy.orm import Session
from backend.db.models import House, Review, PriceHistory, Landlord, ListingImage


def query_houses(db: Session, districts=None, layout=None, min_price=0, max_price=99999):
    """房源列表查询，支持筛选"""
    q = db.query(House)
    if districts:
        q = q.filter(House.district.in_(districts))
    if layout:
        q = q.filter(House.layout == layout)
    q = q.filter(House.price >= min_price, House.price <= max_price)
    return q.all()


def get_house(db: Session, house_id: int):
    return db.query(House).filter(House.id == house_id).first()


def get_reviews(db: Session, house_id: int):
    return db.query(Review).filter(Review.house_id == house_id).all()


def get_price_history(db: Session, house_id: int):
    return db.query(PriceHistory).filter(PriceHistory.house_id == house_id).order_by(PriceHistory.record_date).all()


def get_landlord(db: Session, phone_hash: str):
    return db.query(Landlord).filter(Landlord.phone_hash == phone_hash).first()


def get_landlord_houses(db: Session, phone_hash: str):
    return db.query(House).filter(House.landlord_phone_hash == phone_hash).all()


def get_images(db: Session, house_id: int):
    return db.query(ListingImage).filter(ListingImage.house_id == house_id).order_by(ListingImage.sort_order).all()
