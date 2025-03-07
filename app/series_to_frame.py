from datetime import datetime, date
from typing import Dict
import time
import cProfile
import pstats

from dateutil.relativedelta import relativedelta
import pandas as pd
from pandas import Series, DataFrame

from .attendance_query_class import QueryAttendFactory, AttendanceQuery
from .attendance_calc_lib import calc_attendance_of_term


# 🙅‍♀pymysql.err.OperationalError: (1241, 'Operand should contain 1 column(s)')
def get_result_dataframe(
    from_day: date, to_day: date, part_flag: bool, *staff_ids: int
) -> DataFrame:
    attendance_query_factory = QueryAttendFactory(
        filter_from_day=from_day, filter_to_day=to_day, part_time_flag=part_flag
    )
    query_attend_dict: Dict[int, AttendanceQuery] = {}
    series_dict: Dict[int, Series] = {}
    for staff_id in staff_ids:
        query_attend_instance = attendance_query_factory.get_instance(staff_id=staff_id)
        query_attend_dict[staff_id] = query_attend_instance
        query_attend = query_attend_dict[staff_id].get_clerical_attendance()
        series_dict[staff_id] = calc_attendance_of_term(from_day, to_day, query_attend)
        print(series_dict)

    result_df = pd.DataFrame(series_dict)
    print(result_df)


def calc_vertical_attendance(
    staff_id: int, from_day: date, to_day: date, part_flag: bool
) -> DataFrame:
    # from datetime import time は不可
    # パフォーマンス測定開始
    # start_time = time.perf_counter()
    c_profile = cProfile.Profile()
    c_profile.enable()

    attendance_query_factory = QueryAttendFactory()
    attendance_query_instance = attendance_query_factory.get_instance(staff_id=staff_id)
    series_dict: Dict[int, Series] = {}
    for i in range(1, 6):
        past_from_day = from_day + relativedelta(months=i)
        past_to_day = to_day + relativedelta(months=i, days=-1)
        attendance_query_instance.set_data(
            filter_from_day=past_from_day,
            filter_to_day=past_to_day,
            part_time_flag=part_flag,
        )
        the_person_query = attendance_query_instance.get_clerical_attendance()
        series_dict[past_from_day] = calc_attendance_of_term(
            from_day=from_day, to_day=to_day, attendance_query=the_person_query
        )
        print(f"〜{past_from_day}〜")

    past_2years_df = pd.DataFrame(series_dict)
    # extract_row = past_2years_df.loc[
    #     ["年休（全日）", "年休（半日）", "時間休", "中抜け"]
    # ]
    extract_row = past_2years_df.iloc[[8, 9]]
    sum_result = extract_row.apply(sum, axis=1)
    c_profile.disable()
    c_stats = pstats.Stats(c_profile)
    c_stats.sort_stats("cumtime").print_stats(10)

    return sum_result
