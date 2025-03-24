import pytest
from typing import Dict
from datetime import date
from itertools import groupby

from app.models import StaffHolidayContract
from app.attendance_contract_query import ContractTimeAttendance
from app.result_collect_lib import collect_calculation_attend


from_day = date(2023, 4, 1)
to_day = date(2025, 3, 31)


@pytest.fixture
def perfect_query():
    contract_time_obj = ContractTimeAttendance(
        staff_id=135, filter_from_day=from_day, filter_to_day=to_day
    )
    return contract_time_obj.get_perfect_contract_attendance()


@pytest.mark.skip
def test_start_day_group(perfect_query):
    part_contract_summary: Dict[str, list] = {}
    for key, group in groupby(perfect_query, lambda x: (x[1], x[3])):
        contract_info_list = list(group)
        contract_work_list = []
        contract_holiday_list = []
        for contract_info in contract_info_list:
            holiday_contract: StaffHolidayContract = contract_info[1]
            work_time = contract_info[2]
            holiday_time = holiday_contract.HOLIDAY_TIME
            contract_work_list.append((work_time, holiday_time))
            contract_holiday_list.append((work_time, holiday_time))
        # print(type(key[0]))
        # assert isinstance(holiday_contract, StaffHolidayContract)
        part_contract_summary[f"{key[0].START_DAY}"] = set(contract_holiday_list)
        part_contract_summary[f"{key[1]}"] = set(contract_work_list)

    # print(part_contract_summary)
    for start_day, summary in part_contract_summary.items():
        print(f"Start day for key: {start_day}")
        for item in summary:
            print(f"Contract work time: {item[0]}, holiday time: {item[1]}")


def test_perfect_query(perfect_query):
    for a, jc, jh, w in perfect_query:
        print(f"{a.WORKDAY}, {jc.CONTRACT_CODE}, {jh.HOLIDAY_TIME}")


@pytest.mark.skip
def test_collect_calculation_attend():
    test_result = collect_calculation_attend(20)
    for key, value in test_result.items():
        print(f"Seperation: {key}")
        print(f"Series data: {value}")
