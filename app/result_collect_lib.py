from typing import List, Dict, Tuple, Any
from datetime import date, datetime
from itertools import groupby

from pandas import Series

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


def collect_calculation_attend(staff_id: int):
    from_day, to_day = config_from_to()

    # 諸々計算クラスファクトリー
    calc_time_factory = CalcTimeFactory(from_day=from_day, to_day=to_day)
    result_dict: Dict[Any, Series] = {}

    attendance_contract_obj = ContractTimeAttendance(
        staff_id=staff_id, filter_from_day=from_day, filter_to_day=to_day
    )
    person_for_calc_queries = attendance_contract_obj.get_perfect_contract_attendance()

    calculation_instance = calc_time_factory.get_instance(staff_id=staff_id)
    for index_, groups in groupby(person_for_calc_queries, lambda x: x[1]):
        group_list = list(groups)
        calclation_series = calc_attendance_of_term(calculation_instance, group_list)
        result_dict[f"{index_.START_DAY}"] = calclation_series

    return result_dict
