from dataclasses import dataclass, field, InitVar
from typing import Dict, Optional
from datetime import date

from .database_base import session
from .models import (
    User,
    StaffJobContract,
    Attendance,
)


@dataclass
class AttendanceQuery:
    # staff_id: int
    # filter_from_day: date
    # filter_to_day: date
    # part_time_flag: bool
    staff_id: InitVar[int]

    # `__post_init__`は、通常`__init__`の後に追加の初期化処理が必要な場合にのみ使用します
    # このため、__post_init__で同じ値を再代入する処理は不要 by cursor
    def __post_init__(self, staff_id):
        self.staff_id = staff_id

    def set_data(
        self, filter_from_day: date, filter_to_day: date, part_time_flag: bool
    ):
        self.filter_from_day = filter_from_day
        self.filter_to_day = filter_to_day
        self.part_time_flag = part_time_flag

    def _get_filter(self) -> list:
        attendance_filters = []
        attendance_filters.append(Attendance.STAFFID == self.staff_id)
        # pymysql.err.OperationalError: (1241, 'Operand should contain 1 column(s)')対策も、
        # 🙅ファクトリーにしているため、単体のインスタンスで値が合算される
        # attendance_filters.append(Attendance.STAFFID.in_(self.staff_id))
        attendance_filters.append(
            Attendance.WORKDAY.between(self.filter_from_day, self.filter_to_day)
        )
        attendance_filters.append(Attendance.STAFFID == User.STAFFID)
        return attendance_filters

    def _get_job_filter(self):
        attendance_filters = []
        attendance_filters.append(Attendance.STAFFID == StaffJobContract.STAFFID)
        attendance_filters.append(StaffJobContract.START_DAY <= Attendance.WORKDAY)
        attendance_filters.append(StaffJobContract.END_DAY >= Attendance.WORKDAY)
        (
            attendance_filters.append(StaffJobContract.CONTRACT_CODE != 2)
            if self.part_time_flag is False
            else attendance_filters.append(StaffJobContract.CONTRACT_CODE == 2)
        )
        return attendance_filters

        # Max attendance_filters[0:8] index7まで取り出す
        # return (
        #     attendance_filters[array_number[0] : array_number[1]]
        #     if array_number != ()
        #     else attendance_filters
        # )

    def db_error_handler(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                return e

        return wrapper

    @db_error_handler
    def get_clerical_attendance(self):
        clerk_filters = self._get_filter() + self._get_job_filter()

        # sub_clerk_query = self._get_sub_clerk_query()
        return (
            # session.query(
            #     Attendance,
            #     User.FNAME,
            #     User.LNAME,
            #     StaffJobContract.JOBTYPE_CODE,
            #     StaffJobContract.CONTRACT_CODE,
            #     StaffJobContract.PART_WORKTIME,
            #     sub_clerk_query.c.HOLIDAY_TIME,
            # ).filter(and_(*clerk_filters))
            # .outerjoin(sub_clerk_query, sub_clerk_query.c.STAFFID == User.STAFFID)
            session.query(Attendance, StaffJobContract.CONTRACT_CODE)
            .filter(*clerk_filters)
            .join(StaffJobContract, StaffJobContract.STAFFID == Attendance.STAFFID)
            .order_by(Attendance.STAFFID, Attendance.WORKDAY)
        )


@dataclass
class QueryAttendFactory:
    # staff_id: int
    # filter_from_day: date
    # filter_to_day: date
    # part_time_flag: bool

    _instances: Dict[int, "AttendanceQuery"] = field(default_factory=dict)
    # _instances: Optional["AttendanceQuery"] = field(default=None)  # field(default_factory=AttendanceQuery)

    def get_instance(self, staff_id: int) -> "AttendanceQuery":
        if staff_id not in self._instances:
            # if self._instances is None:
            self._instances[staff_id] = AttendanceQuery(
                # self.filter_from_day,
                # self.filter_to_day,
                # self.part_time_flag,
                staff_id=staff_id,
            )
        return self._instances[staff_id]
