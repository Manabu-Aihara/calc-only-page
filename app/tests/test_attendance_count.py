import pytest
from datetime import date

from app.models import User, TableOfCount
from app.attendance_query_class import AttendanceQuery
from app.attendance_calc_lib import calc_attendance_of_month


@pytest.fixture(name="aq")
def setup_attendance_query():
    from_day = date(2024, 12, 1)
    to_day = date(2024, 12, 31)
    attendance_query_obj = AttendanceQuery(
        201, filter_from_day=from_day, filter_to_day=to_day
    )
    attendance_query = attendance_query_obj.get_clerical_attendance(True)
    return attendance_query


# @pytest.mark.skip
def test_calc_attendance_of_month(aq):
    test_result_series = calc_attendance_of_month(aq)

    # for query in aq:
    #     print(f"ID201: {query[0].WORKDAY} {query[1]}")
    print(test_result_series)


def test_foreignkey():
    user = User(STAFFID=201)
    tc = TableOfCount(staff_id=201)

    user.count_totalling = [tc]
    print(user.count_totalling)
