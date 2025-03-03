from datetime import date

import pandas as pd
from pandas import DataFrame

from .attendance_query_class import QueryAttendFactory
from .attendance_calc_lib import calc_attendance_of_month


# IDフィルター除く場合
def series_to_dataframe1(from_day: date, to_day: date) -> DataFrame:
    # attendance_query_obj = AttendanceQuery(current_staff, from_day, to_day)
    # attendance_queries = attendance_query_obj.get_clerical_attendance(False)
    # ここまで…
    # attendance_queries.filter
    print("")


# IDフィルター入れる場合
def series_to_dataframe2(from_day: date, to_day: date) -> DataFrame:
    query_attend_factory = QueryAttendFactory()
    query_attend_obj = query_attend_factory.get_instance()
    query_attend_obj.set_data()
    the_query = query_attend_obj.get_clerical_attendance(True)
