from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True, nullable=False)
    discord_id = Column(Integer)
    name = Column(String)
    avatar = Column(String)
    attendances = relationship("Attendance", back_populates="members")
    unattendances = relationship("Unattendance", back_populates="members")
    outs = relationship("Out", back_populates="members")

class Workday(Base):
    __tablename__ = 'workdays'
    __table_args__ = {'sqlite_autoincrement':True}
    id = Column(Integer, primary_key=True, nullable=False)
    date = Column(Date, nullable=False)
    detail = Column(Text)
    attendances = relationship("Attendance", back_populates="workdays")
    unattendances = relationship("Unattendance", back_populates="workdays")
    outs = relationship("Out", back_populates="workdays")

class Attendance(Base):
    __tablename__ = 'attendances'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True, nullable=False)
    workday_id = Column(Integer, ForeignKey('workdays.id'), nullable=False)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    masuk = Column(Integer) # 1 or 0
    waktu_masuk = Column(Time)
    waktu_pulang = Column(Time)
    detail = Column(String)
    workdays = relationship("Workday", back_populates="attendances")
    members = relationship("Member", back_populates="attendances")


class Unattendance(Base):
    __tablename__ = 'unattendances'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True, nullable=False)
    workday_id = Column(Integer, ForeignKey('workdays.id'), nullable=False)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    detail = Column(Text)
    workdays = relationship("Workday", back_populates="unattendances")
    members = relationship("Member", back_populates="unattendances")

# Izin keluar selama jam kerja
class Out(Base):
    __tablename__ = 'outs'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True, nullable=False)
    workday_id = Column(Integer, ForeignKey('workdays.id'), nullable=False)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    detail = Column(Text)
    waktu_keluar = Column(Time)
    waktu_kembali = Column(Time)
    workdays = relationship("Workday", back_populates="outs")
    members = relationship("Member", back_populates="outs")

