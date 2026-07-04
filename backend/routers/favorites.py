"""收藏功能 API 路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import Favorite
from backend.db.queries import get_house
from backend.services import favorite_service

router = APIRouter(prefix="/api/v1/favorites", tags=["favorites"])


@router.get("")
def list_favorites(db: Session = Depends(get_db)):
    """获取所有收藏的房源列表"""
    return favorite_service.list_favorites_with_houses(db)


@router.post("/{house_id}")
def toggle_favorite(house_id: int, db: Session = Depends(get_db)):
    """切换收藏状态（添加/取消）"""
    existing = db.query(Favorite).filter(Favorite.house_id == house_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"favorited": False, "house_id": house_id}
    else:
        house = get_house(db, house_id)
        if not house:
            raise HTTPException(status_code=404, detail="房源不存在")
        fav = Favorite(house_id=house_id)
        db.add(fav)
        db.commit()
        return {"favorited": True, "house_id": house_id}


@router.get("/check/{house_id}")
def check_favorite(house_id: int, db: Session = Depends(get_db)):
    """检查指定房源是否已收藏"""
    fav = db.query(Favorite).filter(Favorite.house_id == house_id).first()
    return {"favorited": fav is not None, "house_id": house_id}
