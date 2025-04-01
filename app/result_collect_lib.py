from typing import List, Dict, Tuple, Any
from datetime import date, datetime, timedelta
from itertools import groupby

import pandas as pd
from pandas import Series, DataFrame

from .database_base import session
from .models import StaffJobContract, StaffHolidayContract
from .attendance_contract_query import ContractTimeAttendance
from .calc_work_classes3 import CalcTimeFactory
from .attendance_calc import calc_attendance_of_term


def config_from_to() -> Tuple[date, date]:
    today = datetime.today()
    from_day4 = date(year=(today.year - 2), month=4, day=1)
    to_day4 = date(year=today.year, month=3, day=31)
    from_day10 = date(year=(today.year - 2), month=10, day=1)
    to_day10 = date(year=today.year, month=9, day=30)
    if today.month in [4, 5, 6, 7, 8, 9]:
        return from_day10, to_day10
    else:
        return from_day4, to_day4


def get_in_day(
    staff_id: int, contract_table: StaffJobContract | StaffHolidayContract
) -> date | None:
    in_day_query = (
        session.query(contract_table.START_DAY)
        .filter(contract_table.STAFFID == staff_id)
        .order_by(contract_table.START_DAY.asc())
        .first()
    )
    return in_day_query.START_DAY if in_day_query is not None else None


def collect_calculation_attend(staff_id: int) -> dict:
    from_day, to_day = config_from_to()
    demand_from_day = (
        get_in_day(staff_id, StaffJobContract)
        if from_day < get_in_day(staff_id, StaffJobContract)
        else from_day
    )

    # 諸々計算クラスファクトリー
    calc_time_factory = CalcTimeFactory()
    # 結果物初期化
    calculation_dict: Dict[Any, Series] = {}

    attendance_contract_obj = ContractTimeAttendance(
        staff_id=staff_id, filter_from_day=demand_from_day, filter_to_day=to_day
    )
    perfect_queries_of_person = (
        attendance_contract_obj.get_perfect_contract_attendance()
    )

    start_day_key_list = []

    start_day_key_list = [demand_from_day]
    loop_key_index: int = 0

    for index_, groups in groupby(
        perfect_queries_of_person,
        lambda x: (x[1].END_DAY, x[2].END_DAY) if x[2] is not None else x[1].END_DAY,
    ):
        group_list = list(groups)

        calculation_instance = calc_time_factory.get_instance(staff_id=staff_id)
        calculation_series = calc_attendance_of_term(
            calculation_instance, group_list, staff_id
        )

        start_day_key_list.append(calculation_series.name + timedelta(days=1))

        calculation_dict[f"{start_day_key_list[loop_key_index]}"] = calculation_series
        loop_key_index += 1

    print(f"Key list: {start_day_key_list}")
    return calculation_dict
