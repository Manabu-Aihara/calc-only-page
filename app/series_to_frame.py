from datetime import datetime, date
from typing import Dict, List, Tuple
import time
import cProfile
import pstats

from dateutil.relativedelta import relativedelta
import pandas as pd
from pandas import Series, DataFrame

from .models import User
from .attendance_query_class import QueryAttendFactory, AttendanceQuery
from .users_query import get_conditional_users_query
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


def calc_3d_attendance(
    staff_id: int,
    attendance_query_instance: AttendanceQuery,
    from_day: date = date(2024, 9, 1),
    to_day: date = date(2025, 1, 31),
) -> DataFrame:
    # from datetime import time は不可
    # パフォーマンス測定開始
    # start_time = time.perf_counter()
    c_profile = cProfile.Profile()
    c_profile.enable()

    series_dict: Dict[int, Series] = {}
    # もし、一月毎に出力したかったら
    # for i in range(1, 25):
    #     past_from_day = from_day + relativedelta(months=i)
    #     past_to_day = to_day + relativedelta(months=i, days=-1)
    attendance_query_instance.set_data(
        filter_from_day=from_day,
        filter_to_day=to_day,
    )
    the_person_query = attendance_query_instance.get_clerical_attendance()
    series_dict[staff_id] = calc_attendance_of_term(
        from_day=from_day, to_day=to_day, attendance_query=the_person_query
    )

    past_2years_df = pd.DataFrame(series_dict)
    # extract_row = past_2years_df.loc[
    #     ["実働日数", "年休（全日）", "年休（半日）", "時間休", "中抜け"]
    # ]
    extract_row = past_2years_df.iloc[[7, 8, 9, 21, 22]]
    # sum_result = extract_row.apply(sum, axis=1)
    extract_df = pd.DataFrame(
        extract_row,
        # (゜o゜;抽出した後、インデックスを付けてはいけない → 値がNaNになる
        # index=[
        #     "実働日数",
        #     "年休（全日）",
        #     "年休（半日）",
        #     "時間休",
        #     "中抜け",
        # ],
    )
    c_profile.disable()
    c_stats = pstats.Stats(c_profile)
    c_stats.sort_stats("cumtime").print_stats(10)

    return extract_df


def put_vertical_dataframe(part_flag: int):
    request_flag: bool = False if part_flag == 1 else True
    target_users: List[Tuple[User, int]] = get_conditional_users_query(
        part_time_flag=request_flag
    )
    df_list: List[DataFrame] = []
    attendance_query_factory = QueryAttendFactory()
    for target_user, contract in target_users:
        query_instance = attendance_query_factory.get_instance(target_user.STAFFID)
        extract_calc_df = calc_3d_attendance(target_user.STAFFID, query_instance)
        extract_calc_df.columns = [target_user.STAFFID]
        df_list.append(extract_calc_df)

    # print(f"!!!Value of 201: {[df.iloc[:] for df in df_list]}")
    print(f"What are shape and index?: {[(df.shape, df.index) for df in df_list]}")
    suite_df = pd.concat(df_list, axis=1)
    result_vertical_df = pd.DataFrame(suite_df)
    return result_vertical_df
