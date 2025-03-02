from dataclasses import dataclass, field, InitVar
from datetime import date
from typing import Dict

from .database_base import session
from .models import (
    User,
    StaffJobContract,
    Attendance,
)


@dataclass
class AttendanceQuery:
    staff_id: int
    filter_from_day: date
    filter_to_day: date
    # staff_id: InitVar[int]

    # def set_data(
    #     self,
    #     staff_id: int,
    #     filter_from_day: date,
    #     filter_to_day: date,
    # ):
    #     self.staff_id = staff_id
    #     self.filter_from_day = filter_from_day
    #     self.filter_to_day = filter_to_day

    def _get_filter(self) -> list:
        attendance_filters = []
        attendance_filters.append(Attendance.STAFFID == self.staff_id)
        attendance_filters.append(
            Attendance.WORKDAY.between(self.filter_from_day, self.filter_to_day)
        )
        attendance_filters.append(Attendance.STAFFID == User.STAFFID)
        return attendance_filters

    @staticmethod
    def _get_job_filter(part_timer_flag: bool = False):
        attendance_filters = []
        attendance_filters.append(Attendance.STAFFID == StaffJobContract.STAFFID)
        attendance_filters.append(StaffJobContract.START_DAY <= Attendance.WORKDAY)
        attendance_filters.append(StaffJobContract.END_DAY >= Attendance.WORKDAY)
        (
            attendance_filters.append(StaffJobContract.CONTRACT_CODE != 2)
            if part_timer_flag is False
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
    def get_clerical_attendance(self, part_timer_flag: bool):
        clerk_filters = self._get_filter() + self._get_job_filter(part_timer_flag)

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
            # .order_by(Attendance.STAFFID, Attendance.WORKDAY)
        )


@dataclass
class QueryAttendFactory:
    _instances: Dict[int, "AttendanceQuery"] = field(default_factory=dict)

    def get_instance(self, staff_id: int) -> "AttendanceQuery":
        if staff_id not in self._instances:
            self._instances[staff_id] = AttendanceQuery(staff_id)
        return self._instances[staff_id]
