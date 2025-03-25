from typing import List, Dict, Tuple, Any
from datetime import date, datetime, timedelta
from itertools import groupby

import pandas as pd
from pandas import Series, DataFrame

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


def collect_calculation_attend(staff_id: int) -> dict:
    from_day, to_day = config_from_to()

    # 諸々計算クラスファクトリー
    calc_time_factory = CalcTimeFactory()
    calculation_dict: Dict[Any, Series] = {}

    attendance_contract_obj = ContractTimeAttendance(
        staff_id=staff_id, filter_from_day=from_day, filter_to_day=to_day
    )
    perfect_queries_of_person = (
        attendance_contract_obj.get_perfect_contract_attendance()
    )

    counter: int = 0
    for index_, groups in groupby(
        perfect_queries_of_person,
        lambda x: (x[1].END_DAY, x[2].END_DAY) if x[2] is not None else x[1].END_DAY,
    ):
        group_list = list(groups)
        # groupbyのkey部分をいじっても、ろくなことが起きません
        # for idx in index_:
        # arg_end_day = to_day if idx > to_day else idx
        # arg_start_day = index_ + timedelta(days=1) if counter != 0 else from_day
        print(f"Column name: {index_}")
        calculation_instance = calc_time_factory.get_instance(staff_id=staff_id)
        calculation_series = calc_attendance_of_term(calculation_instance, group_list)

        calculation_dict[f"{index_}"] = calculation_series
        counter += 1

    print(f"Counter: {counter}")
    return calculation_dict
