from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from models.base import Model, CreatedBaseModel


class Category(Model):
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    adverts: Mapped[list['Advert']] = relationship('Advert', back_populates='category')

    def __str__(self):
        return f"{self.id} - {self.name}"


class Advert(CreatedBaseModel):
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    price: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String(15))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    category: Mapped['Category'] = relationship('Category', back_populates='adverts')

    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    owner: Mapped['User'] = relationship('User', back_populates='adverts')

    view_count: Mapped[int] = mapped_column(Integer, server_default='0')
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    images: Mapped[list['AdvertImage']] = relationship('AdvertImage', back_populates='advert')


class AdvertImage(Model):
    image: Mapped[str] = mapped_column(String(255))
    advert_id: Mapped[int] = mapped_column(ForeignKey('adverts.id'))
    advert: Mapped['Advert'] = relationship('Advert', back_populates='images')

class Region(Model):
    name: Mapped[str] = mapped_column(String(255))
    districts: Mapped[list['District']] = relationship('District', back_populates='region')


class District(Model):
    name: Mapped[str] = mapped_column(String(255))
    region_id: Mapped[int] = mapped_column(ForeignKey('regions.id'))
    region: Mapped['Region'] = relationship('Region', back_populates='districts')

    def __str__(self):
        return f"{self.id} - {self.name}"

    def __repr__(self):
        return self.name 