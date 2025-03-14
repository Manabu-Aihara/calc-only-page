from datetime import datetime, date
from typing import Dict, List, Tuple, Callable
import time
import cProfile
import pstats

from dateutil.relativedelta import relativedelta
import pandas as pd
from pandas import Series, DataFrame

from .models import User
from .attendance_query_class import QueryAttendFactory, AttendanceQuery
from .users_query import get_conditional_users_query
from .attendance_calc_lib import config_from_to, calc_attendance_of_term


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


"""
    Seriesから必要行を抽出しDataFrameで返す
    @Params
        : int to make DataFrame for dict
        : AttendanceQuery QueryAttendFactory make instance
        : Callable = attendance_calc_lib.calc_attendance_of_term
    @Return
        : DataFrame
    """


def extract_to_dataframe(
    staff_id: int,
    attendance_query_instance: AttendanceQuery,
    func: Callable[..., Series] = calc_attendance_of_term,
) -> DataFrame:
    # from datetime import time は不可
    # パフォーマンス測定開始
    # start_time = time.perf_counter()
    c_profile = cProfile.Profile()
    c_profile.enable()

    series_dict: Dict[int, Series] = {}
    from_day, to_day = config_from_to()
    # もし、一月毎に出力したかったら
    # for i in range(1, 25):
    #     past_from_day = from_day + relativedelta(months=i)
    #     past_to_day = to_day + relativedelta(months=i, days=-1)

    attendance_query_instance.set_data(
        filter_from_day=from_day,
        filter_to_day=to_day,
    )
    the_person_query = attendance_query_instance.get_clerical_attendance()

    series_dict[staff_id] = func(attendance_query=the_person_query)
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

    # end_time = time.perf_counter()
    # run_time = end_time - start_time
    # pref_result = f"実行時間: {run_time}秒"
    # print(pref_result)

    return extract_df


"""
    複数人分のDataFrame
    @Param
        : int 1なら常勤、2はパート
    @Return
        : DataFrame
    """


def put_vertical_dataframe(part_flag: int) -> DataFrame:
    request_flag: bool = False if part_flag == 1 else True
    target_users: List[Tuple[User, int]] = get_conditional_users_query(
        part_time_flag=request_flag
    )
    df_list: List[DataFrame] = []
    attendance_query_factory = QueryAttendFactory()
    for target_user, contract in target_users:
        query_instance = attendance_query_factory.get_instance(target_user.STAFFID)
        extract_calc_df = extract_to_dataframe(target_user.STAFFID, query_instance)
        # extract_calc_df.columns = [target_user.STAFFID]
        df_list.append(extract_calc_df)

    # print(f"!!!Value of 201: {[df.iloc[:] for df in df_list]}")
    print(f"What are shape and index?: {[(df.shape, df.index) for df in df_list]}")
    suite_df = pd.concat(df_list, axis=1)
    result_vertical_df = pd.DataFrame(suite_df)
    return result_vertical_df
