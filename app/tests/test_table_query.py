import pytest
from pytest_mock import MockFixture
from typing import Dict, List
from datetime import date
from itertools import groupby

from app.attendance_contract_query import ContractTimeAttendance
from app.result_collect_lib import (
    collect_calculation_attend,
    extract_row,
    put_vertical_dataframe,
)


from_day = date(2024, 3, 1)
to_day = date(2025, 2, 28)


@pytest.fixture
def perfect_query():
    contract_time_obj = ContractTimeAttendance(
        staff_id=189, filter_from_day=from_day, filter_to_day=to_day
    )
    return contract_time_obj.get_perfect_contract_attendance()


@pytest.mark.skip
def test_start_day_group(perfect_query):
    contract_summary: Dict[str, list] = {}
    for key, group in groupby(perfect_query, lambda x: (x[1].END_DAY, x[2].END_DAY)):
        contract_info_list = list(group)
        contract_work_list = []
        contract_holiday_list = []
        for contract_info in contract_info_list:
            work_time = (
                contract_info[3]
                if contract_info[1].CONTRACT_CODE != 2
                else contract_info[1].PART_WORKTIME
            )
            holiday_time = (
                contract_info[2].HOLIDAY_TIME
                if contract_info[2] is not None
                else contract_info[3]
            )
            contract_work_list.append(
                (contract_info[0].WORKDAY, work_time, holiday_time)
            )
            contract_holiday_list.append(
                (contract_info[0].WORKDAY, work_time, holiday_time)
            )
        # print(type(key[0]))
        # assert isinstance(holiday_contract, StaffHolidayContract)
        contract_summary[f"{key[0]}"] = contract_work_list
        contract_summary[f"{key[1]}"] = contract_holiday_list

    # print(part_contract_summary)
    for start_day, summary in contract_summary.items():
        print(f"Start day for key: {start_day}")
        for item in summary:
            print(f"{item[0]}: work time: {item[1]}, holiday time: {item[2]}")


@pytest.mark.skip
def test_perfect_query(perfect_query):
    for a, jc, jh, w in perfect_query:
        print(f"{a.WORKDAY}, {jc.CONTRACT_CODE}, {jc.PART_WORKTIME}, {jh.HOLIDAY_TIME}")


# @pytest.mark.skip
def test_collect_calculation_attend(mocker: MockFixture):
    mock_date = mocker.patch(
        "app.result_collect_lib.config_from_to", return_value=(from_day, to_day)
    )
    result_dict = collect_calculation_attend(210)
    for key, value in result_dict.items():
        print(f"Date type key: {key}")
        print(f"Series value: {value}")
    # extracted_row = extract_row(result_dict)
    # print(extracted_row)

    assert mock_date.called


@pytest.mark.skip
def test_put_vertical_dataframe(mocker: MockFixture):
    mock_date = mocker.patch(
        "app.result_collect_lib.config_from_to", return_value=(from_day, to_day)
    )
    result_df = put_vertical_dataframe(2)
    print(result_df)
    assert mock_date.called
