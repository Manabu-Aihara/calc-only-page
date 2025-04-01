from dataclasses import dataclass
from datetime import date

from sqlalchemy import and_, or_

from .database_base import session
from .models import (
    Attendance,
    Contract,
    StaffJobContract,
    StaffHolidayContract,
)


@dataclass
class ContractTimeAttendance:
    staff_id: int
    filter_from_day: date
    filter_to_day: date

    def _get_base_filter(self) -> list:
        attendance_filters = []
        attendance_filters.append(Attendance.STAFFID == self.staff_id)
        # pymysql.err.OperationalError: (1241, 'Operand should contain 1 column(s)')対策も、
        # 🙅ファクトリーにしているため、単体のインスタンスで値が合算される
        # attendance_filters.append(Attendance.STAFFID.in_(self.staff_id))
        attendance_filters.append(
            Attendance.WORKDAY.between(self.filter_from_day, self.filter_to_day)
        )
        return attendance_filters

    @staticmethod
    def _get_job_filter() -> list:
        attendance_filters = []
        # attendance_filters.append(Attendance.WORKDAY >= StaffJobContract.START_DAY)
        attendance_filters.append(Attendance.WORKDAY <= StaffJobContract.END_DAY)
        return attendance_filters

    @staticmethod
    def _get_holiday_filter() -> list:
        attendance_filters = []
        # attendance_filters.append(Attendance.WORKDAY >= StaffHolidayContract.START_DAY)
        attendance_filters.append(Attendance.WORKDAY <= StaffHolidayContract.END_DAY)
        return attendance_filters

    def get_atendance_of_term(self):
        # 一人の（基本）2年間の出退勤 テスト用
        need_to_filters = self._get_filter()
        return session.query(Attendance).filter(and_(*need_to_filters))

    # ここでは、契約労働・休暇をクエリで取得
    def get_regular_contract_attendance(self):
        base_filters = self._get_base_filter()
        job_filters = self._get_job_filter()

        regular_member_queries = (
            session.query(Attendance, StaffJobContract, Contract.WORKTIME)
            .join(StaffJobContract, StaffJobContract.STAFFID == Attendance.STAFFID)
            .join(Contract, Contract.CONTRACT_CODE == StaffJobContract.CONTRACT_CODE)
            .filter(
                and_(
                    *base_filters,
                    StaffJobContract.END_DAY > self.filter_from_day,
                    StaffJobContract.CONTRACT_CODE != 2,
                    *job_filters,
                )
            )
        )
        return regular_member_queries

    def get_part_contract_attendance(self):
        base_filters = self._get_base_filter()
        job_filters = self._get_job_filter()
        holiday_filters = self._get_holiday_filter()

        part_member_queries = (
            session.query(
                Attendance,
                StaffHolidayContract,
                StaffJobContract.PART_WORKTIME,
                # パート契約勤務時間を変えた場合
                StaffJobContract.START_DAY,
            )
            .join(
                StaffHolidayContract, StaffHolidayContract.STAFFID == Attendance.STAFFID
            )
            .join(
                StaffJobContract,
                StaffJobContract.STAFFID == StaffHolidayContract.STAFFID,
            )
            .filter(
                and_(
                    *base_filters,
                    StaffJobContract.CONTRACT_CODE == 2,
                    or_(
                        StaffJobContract.END_DAY > self.filter_from_day,
                        StaffHolidayContract.END_DAY > self.filter_from_day,
                    ),
                    or_(*job_filters, *holiday_filters),
                )
            )
        )
        return part_member_queries

    def get_perfect_contract_attendance(self):
        base_filters = self._get_base_filter()

        member_calc_for_queries = (
            session.query(
                Attendance, StaffJobContract, StaffHolidayContract, Contract.WORKTIME
            )
            .join(
                StaffJobContract,
                and_(
                    StaffJobContract.STAFFID == Attendance.STAFFID,
                    Attendance.WORKDAY >= StaffJobContract.START_DAY,  # この条件が重要
                    Attendance.WORKDAY <= StaffJobContract.END_DAY,
                ),
            )
            .join(Contract, Contract.CONTRACT_CODE == StaffJobContract.CONTRACT_CODE)
            .outerjoin(
                StaffHolidayContract,
                and_(
                    StaffHolidayContract.STAFFID == Attendance.STAFFID,
                    Attendance.WORKDAY
                    >= StaffHolidayContract.START_DAY,  # この条件も重要
                    Attendance.WORKDAY <= StaffHolidayContract.END_DAY,
                ),
            )
            .filter(
                and_(
                    *base_filters,
                    # Attendance.WORKDAY >= self.filter_from_day,
                )
            )
        )

        return member_calc_for_queries
