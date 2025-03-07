import pytest
from datetime import date
import pprint
import cProfile
import pstats

from sqlalchemy import and_

from app.database_base import session
from app.models import StaffJobContract
from app.calc_work_classes2 import ContractTimeClass
from app.series_to_frame import calc_vertical_attendance

from_day = date(2024, 8, 1)
to_day = date(2024, 9, 1)


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


def test_calc_vertical_attendance():
    test_result_df = calc_vertical_attendance(201, from_day, to_day, True)
    pprint.pprint(test_result_df, width=240)


@pytest.mark.skip
def test_run_perf():
    pr = cProfile.Profile()
    pr.runcall(test_calc_vertical_attendance)
    # pr.print_stats()
    status = pstats.Stats(pr)
    status.sort_stats("cumtime").print_stats(10)
