from datetime import datetime
from typing import Optional

from sqlmodel import Session, select, func

from .models import User, UserPointLog, DownloadRecord


class UserDataService:
    def __init__(self, session: Session):
        self.session = session

    def get_user(self, open_id: str) -> Optional[User]:
        statement = select(User).where(User.open_id == open_id)
        return self.session.exec(statement).first()

    def create_or_update_user(
        self,
        open_id: str,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None,
        gender: str = "unknown",
        country: Optional[str] = None,
        province: Optional[str] = None,
        city: Optional[str] = None,
        wechat_id: Optional[str] = None,
        status: str = "active",
    ) -> User:
        user = self.get_user(open_id)
        if user is None:
            user = User(
                open_id=open_id,
                nickname=nickname,
                avatar_url=avatar_url,
                gender=gender,
                country=country,
                province=province,
                city=city,
                wechat_id=wechat_id,
                status=status,
            )
            self.session.add(user)
        else:
            if nickname is not None:
                user.nickname = nickname
            if avatar_url is not None:
                user.avatar_url = avatar_url
            if gender is not None:
                user.gender = gender
            if country is not None:
                user.country = country
            if province is not None:
                user.province = province
            if city is not None:
                user.city = city
            if wechat_id is not None:
                user.wechat_id = wechat_id
            if status is not None:
                user.status = status
            user.updated_at = datetime.utcnow()

        self.session.commit()
        self.session.refresh(user)
        return user

    def increase_parse_count(self, open_id: str) -> User:
        user = self.get_user(open_id)
        if user is None:
            user = User(open_id=open_id, total_parse_count=1)
            self.session.add(user)
        else:
            user.total_parse_count += 1
            user.updated_at = datetime.utcnow()
        self.session.commit()
        self.session.refresh(user)
        return user

    def adjust_points(self, open_id: str, delta: int, reason: str) -> User:
        user = self.get_user(open_id)
        if user is None:
            raise ValueError("用户不存在")

        new_points = user.points + delta
        if new_points < 0:
            raise ValueError("积分不足")

        user.points = new_points
        user.updated_at = datetime.utcnow()
        self.session.add(UserPointLog(open_id=open_id, delta=delta, reason=reason))
        self.session.commit()
        self.session.refresh(user)
        return user

    def create_download_record(
        self,
        open_id: str,
        video_id: str,
        platform: Optional[str],
        title: Optional[str],
        source_url: Optional[str],
        download_url: Optional[str],
        points_cost: int = 0,
    ) -> DownloadRecord:
        user = self.get_user(open_id)
        if user is None:
            raise ValueError("用户不存在")

        if points_cost > 0:
            self.adjust_points(open_id=open_id, delta=-points_cost, reason=f"下载视频:{video_id}")
            user = self.get_user(open_id)

        record = DownloadRecord(
            open_id=open_id,
            video_id=video_id,
            platform=platform,
            title=title,
            source_url=source_url,
            download_url=download_url,
            points_cost=points_cost,
        )
        self.session.add(record)
        user.total_download_count += 1
        user.updated_at = datetime.utcnow()
        self.session.commit()
        self.session.refresh(record)
        return record

    def list_download_records(self, open_id: str, limit: int = 20, offset: int = 0) -> list[DownloadRecord]:
        statement = (
            select(DownloadRecord)
            .where(DownloadRecord.open_id == open_id)
            .order_by(DownloadRecord.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.exec(statement).all())

    def get_total_download_count(self, open_id: str) -> int:
        statement = select(func.count()).select_from(DownloadRecord).where(DownloadRecord.open_id == open_id)
        value = self.session.exec(statement).one()
        return int(value or 0)
