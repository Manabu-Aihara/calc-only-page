from datetime import datetime
from typing import TypeVar

from .database_base import session
from .models import User, StaffJobContract

"""
    第2引数（退職日）が今日を過ぎていても、今月なら対象とする
    @Params:
        query_instances: list<V>
        date_columns: str
    @Return
        result_data_list: list<V> 
    """
V = TypeVar("V")


def get_more_condition_users(
    query_instances: list[V], date_columun: str = "OUTDAY"
) -> list[V]:
    today = datetime.today()
    result_data_list = []
    for query_instance in query_instances:
        # 退職日
        date_c_name1: datetime = getattr(query_instance[0], date_columun)
        # if date_c_name0 is None:
        #     TypeError出してくれる
        if (
            date_c_name1 is None
            # date_c_name0.year == today.year and date_c_name0.month <= today.month
            or date_c_name1 > today
            or (
                date_c_name1.year == today.year
                # ここの == だね
                and date_c_name1.month == today.month
            )
        ):
            result_data_list.append(query_instance)
        # except TypeError:
        #     (
        #         print(f"{query_instance.STAFFID}: 入職日の入力がありません")
        #         if query_instance.STAFFID
        #         else print("入職日の入力がありません")
        #     )
        #     result_data_list.append(query_instance)

    return result_data_list


def get_conditional_users_query(part_time_flag: bool) -> list:
    filter_item = []
    (
        filter_item.append(StaffJobContract.CONTRACT_CODE != 2)
        if part_time_flag is False
        else filter_item.append(StaffJobContract.CONTRACT_CODE == 2)
    )
    users_without_condition = (
        session.query(User, StaffJobContract.CONTRACT_CODE)
        .join(StaffJobContract, StaffJobContract.STAFFID == User.STAFFID)
        .filter(*filter_item)
        .all()
    )
    return get_more_condition_users(users_without_condition)
