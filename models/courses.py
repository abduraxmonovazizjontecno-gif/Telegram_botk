from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from models.base import CreatedBaseModel


class Course(CreatedBaseModel):
    name: Mapped[str] = mapped_column(String(255))
    students: Mapped[list['User']] = relationship('User', secondary='user_courses', back_populates='courses')

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.name}"


class UserCourse(CreatedBaseModel):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))

    __table_args__ = (
        UniqueConstraint("user_id", "course_id"),
    )