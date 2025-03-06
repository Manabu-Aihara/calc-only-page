from datetime import date
from typing import Dict

import pandas as pd
from pandas import Series

from .attendance_query_class import QueryAttendFactory, AttendanceQuery
from .attendance_calc_lib import calc_attendance_of_term


# pymysql.err.OperationalError: (1241, 'Operand should contain 1 column(s)')
def get_result_dataframe(
    from_day: date, to_day: date, part_flag: bool, *staff_ids: int
) -> Series:
    attendance_query_factory = QueryAttendFactory(
        filter_from_day=from_day, filter_to_day=to_day, part_time_flag=part_flag
    )
    query_attend_dict: Dict[int, AttendanceQuery] = {}
    series_dict: Dict[int, Series] = {}
    for staff_id in staff_ids:
        query_attend_instance = attendance_query_factory.get_instance(staff_id=staff_id)
        query_attend_dict[staff_id] = query_attend_instance

        series_dict[staff_id] = calc_attendance_of_term(query_attend_dict[staff_id])
        print(series_dict)

    result_df = pd.DataFrame(series_dict)
    print(result_df)
