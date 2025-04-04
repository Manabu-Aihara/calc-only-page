from typing import List, Dict, Tuple, Any
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from itertools import groupby

import pandas as pd
from pandas import Series, DataFrame

from .database_base import session
from .models import StaffJobContract, StaffHolidayContract, User
from .attendance_contract_query import ContractTimeAttendance
from .calc_work_classes3 import CalcTimeFactory
from .attendance_calc import calc_attendance_of_term
from .users_query_lib import get_conditional_users_query

"""
    2年遡り、年休に使うので4月、10月
    @Return:
        : tuple<date, date> 契約労働（時間）、契約休暇（時間）
    """


def config_from_to() -> Tuple[date, date]:
    today = datetime.today()
    from_day4 = date(year=(today.year - 2), month=4, day=1)
    to_day4 = date(year=today.year, month=3, day=31)
    from_day10 = date(year=(today.year - 2), month=10, day=1)
    to_day10 = date(year=today.year, month=9, day=30)
    if today.month in [4, 5, 6, 7, 8, 9]:
        return from_day10, to_day10
    else:
        return from_day4, to_day4


"""
    入職日及び、契約休暇初日を返す
    @Params:
        : int 対象スタッフ
        : StaffJobContract | StaffHolidayContract
    @Return:
        : date | None パートでなければ、None
    """


def get_in_day(
    staff_id: int, contract_table: StaffJobContract | StaffHolidayContract
) -> date | None:
    in_day_query = (
        session.query(contract_table.START_DAY)
        .filter(contract_table.STAFFID == staff_id)
        .order_by(contract_table.START_DAY.asc())
        .first()
    )
    return in_day_query.START_DAY if in_day_query is not None else None


"""
    @Param:
        : int 対象スタッフ
    @Return:
        : dict<str, Series>
    """


def collect_calculation_attend(staff_id: int) -> dict:
    from_day, to_day = config_from_to()
    # 入職2年未満なら、get_in_day
    demand_from_day = (
        get_in_day(staff_id, StaffJobContract)
        if from_day < get_in_day(staff_id, StaffJobContract)
        else from_day
    )

    # 諸々計算クラスファクトリー
    calc_time_factory = CalcTimeFactory()
    # 結果物初期化
    calculation_dict: Dict[str, Series] = {}

    # クエリーオブジェクト
    attendance_contract_obj = ContractTimeAttendance(
        staff_id=staff_id, filter_from_day=demand_from_day, filter_to_day=to_day
    )
    # 契約期間ごとの契約労働・休暇時間クエリー
    perfect_queries_of_person = (
        attendance_contract_obj.get_perfect_contract_attendance()
    )

    # キーの1個目
    start_day_key_list = [demand_from_day]
    loop_key_index: int = 0

    # groupby 契約期間ごとにSeriesで出してくれる、ユーティリティ関数
    # 各END_DAY（個数分）をキーにする
    for index_, groups in groupby(
        perfect_queries_of_person,
        lambda x: (x[1].END_DAY, x[2].END_DAY) if x[2] is not None else x[1].END_DAY,
    ):
        group_list = list(groups)

        calculation_instance = calc_time_factory.get_instance(staff_id=staff_id)
        calculation_series = calc_attendance_of_term(
            calculation_instance, group_list, staff_id
        )

        # 2個目以降のキー名は、契約期間の最終勤務日の翌月の1日
        # tmp_next_month: date = calculation_series.name + relativedelta(months=1)
        # update_date = tmp_next_month.replace(day=1)
        # 🙆月途中の契約変更もあり得るのでこっち
        # 2個目以降のキー名は、契約期間の最終勤務日+1
        start_day_key_list.append(calculation_series.name + relativedelta(days=1))

        calculation_dict[f"{staff_id}: {start_day_key_list[loop_key_index]}"] = (
            calculation_series
        )
        loop_key_index += 1

    print(f"Key list: {start_day_key_list}")
    return calculation_dict


def extract_row(dict_data: dict) -> DataFrame:
    conv_df = pd.DataFrame(data=dict_data)
    return conv_df.iloc[[0, 1, 9, 10, 11, 23, 24]]


def put_vertical_dataframe(team_code: int) -> DataFrame:
    target_users: List[Tuple[User, int]] = get_conditional_users_query(
        team_code=team_code
    )
    df_list: List[DataFrame] = []
    columns = []
    for target_user, team in target_users:
        dict_calc_data = collect_calculation_attend(target_user.STAFFID)
        need_row = extract_row(dict_data=dict_calc_data)
        df_list.append(need_row)
        columns.append(target_user.STAFFID)

    print(f"Column title: {columns}")
    print(f"What are shape and index?: {[(df.shape, df.index) for df in df_list]}")
    return pd.concat(df_list, axis=1)
    # 単体テストのときは、こちらがおすすめ
    # return pd.concat(df_list, axis=1).T
