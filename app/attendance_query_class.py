from dataclasses import dataclass
from datetime import date

from sqlalchemy import and_
from sqlalchemy.orm import outerjoin

from .database_base import session
from .models import (
    User,
    CollateralTemplate,
    StaffJobContract,
    StaffHolidayContract,
    Attendance,
)


@dataclass
class AttendanceQuery:
    staff_id: int
    filter_from_day: date
    filter_to_day: date

    # sub_query: T = None
    # def __init__(self, staff_id: str, sub_query: T) -> None:
    #     self.staff_id = staff_id
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
        # print(f"Flag state: {part_timer_flag}")
        # if part_timer_flag is False:
        #     print("Passing filter")
        (
            attendance_filters.append(StaffJobContract.CONTRACT_CODE != 2)
            if part_timer_flag is False
            else attendance_filters.append(StaffJobContract.CONTRACT_CODE == 2)
        )
        return attendance_filters

    @staticmethod
    def _get_holiday_filter():
        attendance_filters = []
        attendance_filters.append(Attendance.STAFFID == StaffHolidayContract.STAFFID)
        attendance_filters.append(StaffHolidayContract.START_DAY <= Attendance.WORKDAY)
        attendance_filters.append(StaffHolidayContract.END_DAY >= Attendance.WORKDAY)
        return attendance_filters

    def _get_template_filter(self):
        attendance_filters = []
        attendance_filters.append(
            StaffJobContract.START_DAY <= self.filter_from_day
        )  # 2
        attendance_filters.append(StaffJobContract.END_DAY >= self.filter_to_day)  # 3
        attendance_filters.append(
            StaffJobContract.JOBTYPE_CODE == CollateralTemplate.JOBTYPE_CODE
        )
        attendance_filters.append(
            StaffJobContract.CONTRACT_CODE == CollateralTemplate.CONTRACT_CODE
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
    def get_templates(self):
        template_filters = [StaffJobContract.STAFFID == self.staff_id]
        template_filters += self._get_template_filter()
        return session.query(CollateralTemplate.TEMPLATE_NO).filter(
            and_(*template_filters)
        )

    @db_error_handler
    def _get_sub_parttime(self):
        attendance_filters = self._get_filter()[0:2] + self._get_holiday_filter()
        attendance_filters.append(Attendance.STAFFID == StaffHolidayContract.STAFFID)

        return (
            session.query(
                StaffHolidayContract.STAFFID,
                Attendance.WORKDAY,
                StaffHolidayContract.HOLIDAY_TIME,
            )
            .filter(and_(*attendance_filters))
            .subquery()
        )

    @db_error_handler
    def get_attendance_query(self):
        attendance_filters = (
            self._get_filter()
            + self._get_job_filter()[0:3]
            + self._get_template_filter()[-2:]
        )

        sub_query = self._get_sub_parttime()
        return (
            session.query(
                Attendance,
                User.FNAME,
                User.LNAME,
                StaffJobContract.JOBTYPE_CODE,
                StaffJobContract.CONTRACT_CODE,
                StaffJobContract.PART_WORKTIME,
                CollateralTemplate.TEMPLATE_NO,
                # getattr(self.sub_query.c, "HOLIDAY_TIME"),
                sub_query.c.HOLIDAY_TIME,
            )
            .filter(and_(*attendance_filters))
            .outerjoin(
                sub_query,
                and_(
                    sub_query.c.STAFFID == Attendance.STAFFID,
                    sub_query.c.WORKDAY == Attendance.WORKDAY,
                ),
            )
        )

    # 対象年月日の職種や契約時間をスタッフごとに纏める(サブクエリ)
    def _get_sub_clerk_query(self):
        return (
            session.query(
                StaffHolidayContract.STAFFID, StaffHolidayContract.HOLIDAY_TIME
            )
            .filter(
                StaffHolidayContract.START_DAY <= self.filter_to_day,
                StaffHolidayContract.END_DAY >= self.filter_to_day,
            )
            .subquery()
        )

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
