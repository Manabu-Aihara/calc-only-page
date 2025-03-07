import pytest
from datetime import date

from app.models import User, TableOfCount
from app.attendance_query_class import QueryAttendFactory, AttendanceQuery
from app.attendance_calc_lib import calc_attendance_of_term
from app.series_to_frame import get_result_dataframe

from_day = date(2024, 10, 1)
to_day = date(2024, 10, 31)
# users = (201, 206, 207, 216, 217, 237)
users = (201, 3)


@pytest.fixture(name="aq")
def setup_attendance_query():
    attendance_query_factory = QueryAttendFactory(from_day, to_day, True)
    attendance_query_obj = attendance_query_factory.get_instance(3)
    # attendance_query_obj.set_data(from_day, to_day, True)
    # attendance_query = attendance_query_obj.get_clerical_attendance()
    return attendance_query_obj


@pytest.mark.skip
def test_calc_attendance_of_month(aq):
    test_result_series = calc_attendance_of_term(aq)
    print(test_result_series)


@pytest.mark.skip
# @pytest.mark.parametrize("From, To, Users", from_day, to_day, users)
def test_get_result_dataframe():
    # test_result_df = get_result_dataframe(from_day, to_day, True, users)
    # print(test_result_df)
    get_result_dataframe(from_day, to_day, True, users)


def test_query_factory():
    attendance_query_factory = QueryAttendFactory(staff_id=201)
    attendance_query_obj = attendance_query_factory.get_instance()
    assert isinstance(attendance_query_obj, AttendanceQuery)


@pytest.mark.skip
def test_foreignkey():
    user = User(STAFFID=201)
    tc = TableOfCount(staff_id=201)

    user.count_totalling = [tc]
    print(user.count_totalling)
