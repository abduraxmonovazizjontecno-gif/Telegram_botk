from datetime import datetime

from sqlalchemy import String, DateTime, Integer, UniqueConstraint, CheckConstraint, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from models.base import CreatedBaseModel, Model


class User(CreatedBaseModel):
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(12), unique=True)
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    adverts: Mapped[list['Advert']] = relationship('Advert', back_populates='owner')
    passport: Mapped['Passport'] = relationship('Passport', back_populates='user')
    courses: Mapped[list['Course']] = relationship('Course', secondary='user_courses', back_populates='students')

    def __str__(self):
        return f"{self.id} - {self.first_name}"


class Passport(Model):
    series: Mapped[str] = mapped_column(String(2))
    number: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    user: Mapped['User'] = relationship('User', back_populates='passport')

    __table_args__ = (
        UniqueConstraint("series", "number", name="uk_series_number_passport"),
        CheckConstraint("number >= 1000000 and number <= 9999999", name="ck_number_passport")
    )
