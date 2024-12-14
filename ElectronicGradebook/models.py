from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    date_of_birth: Mapped[Date | None] = mapped_column(Date, nullable=True)
    class_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('classes.id'), nullable=True)
    subject_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('subjects.id'), nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=False)

    klasa: Mapped["Class"] = relationship("Class", back_populates="students")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="teachers")
    grades: Mapped[list["Grade"]] = relationship("Grade", foreign_keys="Grade.student_id", back_populates="student")
    grades_user: Mapped[list["Grade"]] = relationship("Grade", foreign_keys="Grade.added_by_id",
                                                      back_populates="teacher")
    attendance_user: Mapped[list["Attendance"]] = relationship("Attendance", foreign_keys="Attendance.added_by_id",
                                                               back_populates="teacher")
    attendances: Mapped[list["Attendance"]] = relationship("Attendance", foreign_keys="Attendance.student_id",
                                                           back_populates="student")


class Subject(Base):
    __tablename__ = 'subjects'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    teachers: Mapped[list["User"]] = relationship("User", back_populates="subject")
    grades: Mapped[list["Grade"]] = relationship("Grade", back_populates="subject")
    attendances: Mapped[list["Attendance"]] = relationship("Attendance", back_populates="subject")


class Class(Base):
    __tablename__ = 'classes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    students: Mapped[list["User"]] = relationship('User', back_populates='klasa')


class Grade(Base):
    __tablename__ = 'grades'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey('subjects.id'), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    added_by_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)

    student: Mapped["User"] = relationship("User", foreign_keys=[student_id], back_populates="grades")
    teacher: Mapped["User"] = relationship("User", foreign_keys=[added_by_id], back_populates="grades_user")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="grades")


class Attendance(Base):
    __tablename__ = 'attendance'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey('subjects.id'), nullable=False)
    class_date: Mapped[Date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    added_by_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)

    student: Mapped["User"] = relationship("User", foreign_keys=[student_id], back_populates="attendances")
    teacher: Mapped["User"] = relationship("User", foreign_keys=[added_by_id], back_populates="attendance_user")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="attendances")
