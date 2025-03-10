import pytest
from datetime import date
import pprint
import cProfile
import pstats

from sqlalchemy import and_

from app.database_base import session
from app.models import StaffJobContract
from app.calc_work_classes2 import ContractTimeClass
from app.attendance_query_class import QueryAttendFactory
from app.series_to_frame import calc_3d_attendance
from app.main import put_vertical_dataframe

from_day = date(2024, 9, 1)
to_day = date(2025, 1, 31)


@pytest.mark.skip
def test_judge_hash():
    bool_result = ContractTimeClass.hashable(
        ContractTimeClass.get_contract_times(201, from_day=from_day, to_day=to_day)
    )
    assert bool_result is True


@pytest.mark.skip
def test_get_multi_contract():
    contract_work = (
        session.query(StaffJobContract)
        .filter(
            and_(
                StaffJobContract.STAFFID == 181,
                StaffJobContract.START_DAY <= to_day,
                StaffJobContract.END_DAY >= from_day,
            )
        )
        .order_by(StaffJobContract.START_DAY.desc())
        .all()
    )

    assert len(contract_work) == 2
    for cw in contract_work:
        print(f"start: {cw.START_DAY}, end: {cw.END_DAY}")


@pytest.fixture(name="attend_query")
def get_attend_query():
    attendance_query_factory = QueryAttendFactory()
    query_instance = attendance_query_factory.get_instance(staff_id=201)
    return query_instance


@pytest.mark.skip
def test_calc_3d_attendance(attend_query):
    test_result_df = calc_3d_attendance(201, attend_query, from_day, to_day)
    pprint.pprint(test_result_df, width=240)


def test_put_vertical_dataframe():
    test_df = put_vertical_dataframe(2)
    print(test_df)


@pytest.mark.skip
def test_run_perf():
    pr = cProfile.Profile()
    pr.runcall(test_put_vertical_dataframe)
    # pr.print_stats()
    status = pstats.Stats(pr)
    status.sort_stats("cumtime").print_stats(10)
