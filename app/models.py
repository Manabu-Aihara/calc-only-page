from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Float,
    DateTime,
    Date,
)
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash

from .database_base import Base


class User(Base):
    __tablename__ = "M_STAFFINFO"
    STAFFID = Column(Integer, primary_key=True, index=True, nullable=False)
    DEPARTMENT_CODE = Column(Integer, index=True, nullable=True)
    TEAM_CODE = Column(Integer, index=True, nullable=True)
    CONTRACT_CODE = Column(Integer, index=True, nullable=True)
    JOBTYPE_CODE = Column(Integer, index=True, nullable=True)
    POST_CODE = Column(Integer, index=True, nullable=True)
    LNAME = Column(String(50), index=True, nullable=True)
    FNAME = Column(String(50), index=True, nullable=True)
    LKANA = Column(String(50), index=True, nullable=True)
    FKANA = Column(String(50), index=True, nullable=True)
    POST = Column(String(10), index=True, nullable=True)
    ADRESS1 = Column(String(50), index=True, nullable=True)
    ADRESS2 = Column(String(50), index=True, nullable=True)
    TEL1 = Column(String(50), index=True, nullable=True)
    TEL2 = Column(String(50), index=True, nullable=True)
    BIRTHDAY = Column(DateTime, index=True, nullable=True)
    INDAY = Column(DateTime, index=True, nullable=True)
    OUTDAY = Column(DateTime, index=True, nullable=True)
    STANDDAY = Column(DateTime, index=True, nullable=True)
    SOCIAL_INSURANCE = Column(Integer, index=True, nullable=True)
    EMPLOYMENT_INSURANCE = Column(Integer, index=True, nullable=True)
    EXPERIENCE = Column(Integer, index=True, nullable=True)
    TABLET = Column(Integer, index=True, nullable=True)
    SINGLE = Column(Integer, index=True, nullable=True)
    SUPPORT = Column(Integer, index=True, nullable=True)
    HOUSE = Column(Integer, index=True, nullable=True)
    DISTANCE = Column(Float, index=True, nullable=True)
    REMARK = Column(String(100), index=True, nullable=True)
    DISPLAY = Column(Boolean, index=True, nullable=False)
    login = relationship("StaffLogin", backref="user")
    job_contract = relationship("StaffJobContract", backref="user")
    holiday_contract = relationship("StaffHolidayContract", backref="user")
    paid_holiday = relationship("RecordPaidHoliday", backref="user")
    # count_totalling = relationship("TableOfCount", backref="user")

    def __init__(self, STAFFID):
        self.STAFFID = STAFFID


class CollateralTemplate(Base):
    __tablename__ = "M_TIMECARD_TEMPLATE"
    JOBTYPE_CODE = Column(Integer, primary_key=True, index=True, nullable=False)
    CONTRACT_CODE = Column(Integer, primary_key=True, index=True, nullable=False)
    TEMPLATE_NO = Column(Integer, index=True, nullable=False)

    """
    sqlalchemy.exc.AmbiguousForeignKeysError:
    Could not determine join condition between parent/child tables on relationship ...
    - there are multiple foreign key paths linking the tables.
    Specify the 'foreign_keys' argument, providing a list of those columns 
    which should be counted as containing a foreign key reference to the parent table.
    """
    # job_history = relationship("D_JOB_HISTORY")
    # https://stackoverflow.com/questions/75756897/reference-a-relationship-with-multiple-foreign-keys-in-sqlalchemy
    # job_history = relationship(
    #     "D_JOB_HISTORY",
    #     # foreign_keys="[D_JOB_HISTORY.JOBTYPE_CODE, D_JOB_HISTORY.CONTRACT_CODE]",
    #     back_populates="timecard_template",
    # )

    def __init__(self, JOBTYPE_CODE, CONTRACT_CODE, TEMPLATE_NO):
        self.JOBTYPE_CODE = JOBTYPE_CODE
        self.CONTRACT_CODE = CONTRACT_CODE
        self.TEMPLATE_NO = TEMPLATE_NO


# class StaffJobContract(Base):
#     __tablename__ = "D_JOB_HISTORY"
#     STAFFID = Column(
#         Integer,
#         ForeignKey("M_STAFFINFO.STAFFID"),
#         primary_key=True,
#         index=True,
#         nullable=False,
#     )
#     JOBTYPE_CODE = Column(Integer, index=True, nullable=False)
#     CONTRACT_CODE = Column(Integer, index=True, nullable=False)
#     PART_WORKTIME = Column(Integer, index=True, nullable=False)
#     START_DAY = Column(Date, primary_key=True, index=True, nullable=True)
#     END_DAY = Column(Date, index=True, nullable=True)

#     def __init__(
#         self, STAFFID, JOBTYPE_CODE, CONTRACT_CODE, PART_WORKTIME, START_DAY, END_DAY
#     ):
#         self.STAFFID = STAFFID
#         self.JOBTYPE_CODE = JOBTYPE_CODE
#         self.CONTRACT_CODE = CONTRACT_CODE
#         self.PART_WORKTIME = PART_WORKTIME
#         self.START_DAY = START_DAY
#         self.END_DAY = END_DAY
# print("")


class StaffJobContract(Base):
    __tablename__ = "D_JOB_HISTORY"
    # __table_args__ = (
    #     ForeignKeyConstraint(
    #         ["JOBTYPE_CODE", "CONTRACT_CODE"],
    #         ["M_TIMECARD_TEMPLATE.JOBTYPE_CODE", "M_TIMECARD_TEMPLATE.CONTRACT_CODE"],
    #     ),
    # )
    STAFFID = Column(
        Integer,
        ForeignKey("M_STAFFINFO.STAFFID"),
        primary_key=True,
        index=True,
        nullable=False,
    )
    JOBTYPE_CODE = Column(
        Integer,
        ForeignKey("M_TIMECARD_TEMPLATE.JOBTYPE_CODE"),
        index=True,
        nullable=False,
    )
    CONTRACT_CODE = Column(
        Integer,
        ForeignKey("M_TIMECARD_TEMPLATE.CONTRACT_CODE"),
        index=True,
        nullable=False,
    )
    # JOBTYPE_CODE = Column(Integer, index=True, nullable=False)
    # CONTRACT_CODE = Column(Integer, index=True, nullable=False)
    """
    2024/8/15 リレーション機能追加
    SQLAlchemy multiple foreign keys in one mapped class to the same primary key
    https://stackoverflow.com/questions/22355890/sqlalchemy-multiple-foreign-keys-in-one-mapped-class-to-the-same-primary-key
    """
    jobtype = relationship(
        "CollateralTemplate", foreign_keys=[JOBTYPE_CODE], uselist=True
    )
    constract = relationship(
        "CollateralTemplate", foreign_keys=[CONTRACT_CODE], uselist=True
    )

    PART_WORKTIME = Column(Float, index=True, nullable=False)
    START_DAY = Column(Date, primary_key=True, index=True, nullable=True)
    END_DAY = Column(Date, index=True, nullable=True)

    # timecard_template = relationship(
    #     "M_TIMECARD_TEMPLATE",
    #     # foreign_keys="[M_TIMECARD_TEMPLATE.JOBTYPE_CODE, M_TIMECARD_TEMPLATE.CONTRACT_CODE]",
    #     back_populates="job_history",
    #     uselist=True,
    # )

    def __init__(
        self, STAFFID, JOBTYPE_CODE, CONTRACT_CODE, PART_WORKTIME, START_DAY, END_DAY
    ):
        self.STAFFID = STAFFID
        self.JOBTYPE_CODE = JOBTYPE_CODE
        self.CONTRACT_CODE = CONTRACT_CODE
        self.PART_WORKTIME = PART_WORKTIME
        self.START_DAY = START_DAY
        self.END_DAY = END_DAY


class StaffHolidayContract(Base):
    __tablename__ = "D_HOLIDAY_HISTORY"
    STAFFID = Column(
        Integer,
        ForeignKey("M_STAFFINFO.STAFFID"),
        primary_key=True,
        index=True,
        nullable=False,
    )
    HOLIDAY_TIME = Column(Integer, primary_key=True, index=True, nullable=False)
    START_DAY = Column(Date, index=True, nullable=True)
    END_DAY = Column(Date, index=True, nullable=True)

    def __init__(self, HOLIDAY_TIME, START_DAY, END_DAY):
        self.HOLIDAY_TIME = HOLIDAY_TIME
        self.START_DAY = START_DAY
        self.END_DAY = END_DAY


class Department(Base):
    __tablename__ = "M_DEPARTMENT"
    CODE = Column(Integer, primary_key=True, index=True, nullable=False)
    NAME = Column(String(50), index=True, nullable=True)

    def __init__(self, CODE):
        self.CODE = CODE


class Team(Base):
    __tablename__ = "M_TEAM"
    CODE = Column(Integer, primary_key=True, index=True, nullable=False)
    NAME = Column(String(50), index=True, nullable=False)
    SHORTNAME = Column(String(50), index=True, nullable=False)

    def __init__(self, CODE):
        self.CODE = CODE


class JobType(Base):
    __tablename__ = "M_JOBTYPE"
    JOBTYPE_CODE = Column(Integer, primary_key=True, index=True, nullable=False)
    NAME = Column(String(50), index=True, nullable=False)
    SHORTNAME = Column(String(50), index=True, nullable=False)

    def __init__(self, JOBTYPE_CODE, NAME, SHORTNAME):
        self.JOBTYPE_CODE = JOBTYPE_CODE
        self.NAME = NAME
        self.SHORTNAME = SHORTNAME


class Contract(Base):
    __tablename__ = "M_CONTRACT"
    CONTRACT_CODE = Column(Integer, primary_key=True, index=True, nullable=False)
    NAME = Column(String(50), index=True, nullable=True)
    SHORTNAME = Column(String(50), index=True, nullable=False)
    WORKTIME = Column(Float, nullable=True)

    def __init__(self, CONTRACT_CODE):
        self.CODE = CONTRACT_CODE


class Post(Base):
    __tablename__ = "M_POST"
    CODE = Column(Integer, primary_key=True, index=True, nullable=False)
    NAME = Column(String(50), index=True, nullable=True)

    def __init__(self, CODE):
        self.CODE = CODE


class StaffLogin(Base):
    __tablename__ = "M_LOGGININFO"
    id = Column(Integer, primary_key=True)
    # login = relationship("User", backref="user")
    STAFFID = Column(
        Integer,
        ForeignKey("M_STAFFINFO.STAFFID"),
        unique=True,
        index=True,
        nullable=False,
    )
    PASSWORD_HASH = Column(String(128), index=True, nullable=True)
    ADMIN = Column(Boolean, index=True, nullable=True)
    attendance = relationship("Attendance", backref="login_user")

    def __init__(self, STAFFID, PASSWORD, ADMIN):
        self.STAFFID = STAFFID
        self.PASSWORD_HASH = generate_password_hash(PASSWORD)
        self.ADMIN = ADMIN


class Attendance(Base):
    __tablename__ = "M_ATTENDANCE"
    id = Column(Integer, primary_key=True)
    STAFFID = Column(Integer, ForeignKey("M_LOGGININFO.STAFFID"), index=True)
    WORKDAY = Column(Date, index=True, nullable=True)
    HOLIDAY = Column(String(32), index=True, nullable=True)
    STARTTIME = Column(String(32), index=True, nullable=True)  # 出勤時間
    ENDTIME = Column(String(32), index=True, nullable=True)  # 退勤時間
    MILEAGE = Column(String(32), index=True, nullable=True)  # 走行距離
    ONCALL = Column(String(32), index=True, nullable=True)  # オンコール当番
    ONCALL_COUNT = Column(String(32), index=True, nullable=True)  # オンコール回数
    ENGEL_COUNT = Column(String(32), index=True, nullable=True)  # エンゼルケア
    NOTIFICATION = Column(String(32), index=True, nullable=True)  # 届出（午前）
    NOTIFICATION2 = Column(String(32), index=True, nullable=True)  # 届出（午後）
    OVERTIME = Column(String(32), index=True, nullable=True)  # 残業時間申請
    ALCOHOL = Column(Integer, index=True, nullable=True)
    REMARK = Column(String(100), index=True, nullable=True)  # 備考

    def __init__(
        self,
        STAFFID,
        WORKDAY,
        HOLIDAY,
        STARTTIME,
        ENDTIME,
        MILEAGE,
        ONCALL,
        ONCALL_COUNT,
        ENGEL_COUNT,
        NOTIFICATION,
        NOTIFICATION2,
        OVERTIME,
        ALCOHOL,
        REMARK,
    ):
        self.STAFFID = STAFFID
        self.WORKDAY = WORKDAY
        self.HOLIDAY = HOLIDAY
        self.STARTTIME = STARTTIME
        self.ENDTIME = ENDTIME
        self.MILEAGE = MILEAGE
        self.ONCALL = ONCALL
        self.ONCALL_COUNT = ONCALL_COUNT
        self.ENGEL_COUNT = ENGEL_COUNT
        self.NOTIFICATION = NOTIFICATION
        self.NOTIFICATION2 = NOTIFICATION2
        self.OVERTIME = OVERTIME
        self.ALCOHOL = ALCOHOL
        self.REMARK = REMARK


class RecordPaidHoliday(Base):  # 年休関連
    __tablename__ = "M_RECORD_PAIDHOLIDAY"
    STAFFID = Column(
        Integer,
        ForeignKey("M_STAFFINFO.STAFFID"),
        primary_key=True,
        index=True,
        nullable=False,
    )
    LAST_DATEGRANT = Column(DateTime, index=True, nullable=True)  # 今回付与年月日
    NEXT_DATEGRANT = Column(DateTime, index=True, nullable=True)  # 次回付与年月日
    USED_PAIDHOLIDAY = Column(Float, index=True, nullable=True)  # 使用日数
    REMAIN_PAIDHOLIDAY = Column(Float, index=True, nullable=True)  # 残日数
    TEAM_CODE = Column(Integer, index=True, nullable=True)
    CONTRACT_CODE = Column(Integer, index=True, nullable=True)
    LAST_CARRIEDOVER = Column(Float, index=True, nullable=True)  # 前回繰越日数
    ATENDANCE_YEAR = Column(
        Integer, index=True, nullable=True
    )  # 年間出勤日数（年休べース）
    WORK_TIME = Column(Float, index=True, nullable=True)  # 職員勤務時間
    BASETIMES_PAIDHOLIDAY = Column(Float, index=True, nullable=True)  # 規定の年休時間
    ACQUISITION_TYPE = Column(String(1))  # 年休付与タイプ

    def __init__(self, STAFFID):
        self.STAFFID = STAFFID


class TableOfCount(Base):
    __tablename__ = "M_TABLE_OF_COUNTER"
    id = Column(String(15), primary_key=True)
    # count_totalling = relationship("User", backref="user")
    STAFFID = Column(
        Integer,
        # ForeignKey("M_STAFFINFO.STAFFID"),
        index=True,
        nullable=False,
    )
    YEAR_MONTH = Column(String(10), index=True, nullable=False)
    ONCALL = Column(Integer, index=True, nullable=True)
    ONCALL_HOLIDAY = Column(Integer, index=True, nullable=True)
    ONCALL_COUNT = Column(Integer, index=True, nullable=True)
    ENGEL_COUNT = Column(Integer, index=True, nullable=True)
    NENKYU = Column(Integer, index=True, nullable=True)
    NENKYU_HALF = Column(Integer, index=True, nullable=True)
    TIKOKU = Column(Integer, index=True, nullable=True)
    SOUTAI = Column(Integer, index=True, nullable=True)
    KEKKIN = Column(Integer, index=True, nullable=True)
    SYUTTYOU = Column(Integer, index=True, nullable=True)
    SYUTTYOU_HALF = Column(Integer, index=True, nullable=True)
    REFLESH = Column(Integer, index=True, nullable=True)
    MILEAGE = Column(Float, index=True, nullable=True)
    SUM_WORKTIME = Column(Float, index=True, nullable=True)
    SUM_REAL_WORKTIME = Column(Float, index=True, nullable=True)
    OVERTIME = Column(Float, index=True, nullable=True)
    HOLIDAY_WORK = Column(Float, index=True, nullable=True)
    WORKDAY_COUNT = Column(Integer, index=True, nullable=True)
    SUM_WORKTIME_10 = Column(Float, index=True, nullable=True)
    OVERTIME_10 = Column(Float, index=True, nullable=True)
    HOLIDAY_WORK_10 = Column(Float, index=True, nullable=True)
    TIMEOFF = Column(Integer, index=True, nullable=True)
    HALFWAY_THROUGH = Column(Integer, index=True, nullable=True)

    def __init__(self, staff_id: int):
        super().__init__()
        self.STAFFID = staff_id
