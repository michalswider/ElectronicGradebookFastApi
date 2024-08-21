from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=True)
    role = Column(String)

    klasa = relationship("Class", back_populates="students")
    subject = relationship("Subject", back_populates="teachers")
    grades = relationship("Grade", foreign_keys="[Grade.student_id]", back_populates="student")
    grades_user = relationship("Grade",foreign_keys="[Grade.added_by_id]", back_populates="teacher")
    attendance_user = relationship("Attendance", foreign_keys="[Attendance.added_by_id]", back_populates="teacher")
    attendances = relationship("Attendance", foreign_keys="[Attendance.student_id]" ,back_populates="student")


class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    teachers = relationship("User", back_populates="subject")
    grades = relationship("Grade", back_populates="subject")
    attendances = relationship("Attendance", back_populates="subject")


class Class(Base):
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    students = relationship('User', back_populates='klasa')


class Grade(Base):
    __tablename__ = 'grades'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    grade = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    added_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    student = relationship("User", foreign_keys=[student_id], back_populates="grades")
    teacher = relationship("User", foreign_keys=[added_by_id],back_populates="grades_user")
    subject = relationship("Subject", back_populates="grades")


class Attendance(Base):
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    class_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    added_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    student = relationship("User", foreign_keys=[student_id], back_populates="attendances")
    teacher = relationship("User", foreign_keys=[added_by_id],back_populates="attendance_user")
    subject = relationship("Subject", back_populates="attendances")
