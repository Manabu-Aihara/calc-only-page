from typing import List, Dict, Tuple
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd
from pandas import Series

from .calc_work_classes2 import CalcTimeFactory, output_rest_time


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


def calc_attendance_of_term(attendance_query) -> Series:
    from_day, to_day = config_from_to()

    pds = pd.Series
    calc_time_factory = CalcTimeFactory(from_day=from_day, to_day=to_day)
    # 欠勤扱いコード
    n_absence_list: List[str] = ["8", "17", "18", "19", "20"]

    actual_time_sum: float = 0.0
    # 【項目11】実働時間計：60進数
    actual_time60: float = 0.0
    # 【項目12】実働時間計：10進数
    actual_time_rnd: Decimal = 0.0

    real_work_times = []
    # 【項目13】リアル労働時間計：60進数
    real_time: float = 0.0

    over_times = []
    # 【項目17】残業時間計：60進数
    over60: float = 0.0
    # 【項目18】残業時間計：10進数
    over10_rnd: Decimal = 0.0

    nurse_holiday_works = []
    # 【項目22】看護師休日労働時間計：60進数
    holiday_work60: float = 0.0
    # 【項目23】看護師休日労働時間計：10進数
    holiday_work10_rnd: Decimal = 0.0

    # 【項目7】オンコール平日
    on_call_cnt: int = 0
    # 【項目8】オンコール休日
    on_call_holiday_cnt: int = 0
    # 【項目9】オンコール対応
    on_call_correspond_cnt: int = 0
    # 【項目10】エンゼル対応
    engel_correspond_cnt: int = 0

    # 【項目14】
    workday_count: int = 0
    # 【項目15】年休全日
    holiday_cnt: int = 0
    # 【項目16】年休半日
    half_holiday_cnt: int = 0
    # 【項目19】遅刻
    late_cnt: int = 0
    # 【項目20】早退
    leave_early_cnt: int = 0
    # 【項目21】欠勤
    absence_cnt: int = 0
    # 【項目24】出張全日
    trip_cnt: int = 0
    # 【項目25】出張半日
    half_trip_cnt: int = 0
    # 【項目26】リフレッシュ
    reflesh_cnt: int = 0
    # 【項目27】走行距離
    distance_sum: float = 0.0

    # 【項目28】時間休
    timeoff: int = 0
    # 【項目29】中抜け
    halfway_through: int = 0

    for (
        one_person_attendance,
        contract_code,
    ) in attendance_query:

        on_call_holiday_cnt += (
            1
            if one_person_attendance.ONCALL != "0"
            and one_person_attendance.WORKDAY.weekday() in [5, 6]
            else 0
        )
        on_call_cnt += (
            1
            if one_person_attendance.ONCALL != "0"
            and one_person_attendance.WORKDAY.weekday() not in [5, 6]
            else 0
        )
        on_call_correspond_cnt += (
            int(one_person_attendance.ONCALL_COUNT)
            if not isinstance(one_person_attendance.ONCALL_COUNT, type(None))
            and one_person_attendance.ONCALL_COUNT != ""
            and one_person_attendance.ONCALL_COUNT != "0"
            else 0
        )
        engel_correspond_cnt += (
            int(one_person_attendance.ENGEL_COUNT)
            if not isinstance(one_person_attendance.ENGEL_COUNT, type(None))
            and one_person_attendance.ENGEL_COUNT != ""
            and one_person_attendance.ENGEL_COUNT != "0"
            else 0
        )
        distance_sum += (
            float(one_person_attendance.MILEAGE)
            if not isinstance(one_person_attendance.MILEAGE, type(None))
            and one_person_attendance.MILEAGE != ""
            and one_person_attendance.MILEAGE != "0.0"
            else 0
        )
        # print(
        #     f"Inner Count log: {on_call_cnt} {on_call_cnt_cnt} {on_call_holiday_cnt} {engel_int_cnt}"
        # )

        holiday_cnt += 1 if one_person_attendance.NOTIFICATION == "3" else 0
        half_holiday_cnt += (
            1
            if one_person_attendance.NOTIFICATION == "4"
            or one_person_attendance.NOTIFICATION2 == "4"
            else 0
        )
        late_cnt += (
            1
            if one_person_attendance.NOTIFICATION == "1"
            or one_person_attendance.NOTIFICATION2 == "1"
            else 0
        )
        leave_early_cnt += (
            1
            if one_person_attendance.NOTIFICATION == "2"
            or one_person_attendance.NOTIFICATION2 == "2"
            else 0
        )
        absence_cnt += 1 if one_person_attendance.NOTIFICATION in n_absence_list else 0
        trip_cnt += 1 if one_person_attendance.NOTIFICATION == "5" else 0
        half_trip_cnt += (
            1
            if one_person_attendance.NOTIFICATION == "6"
            or one_person_attendance.NOTIFICATION2 == "6"
            else 0
        )
        reflesh_cnt += 1 if one_person_attendance.NOTIFICATION == "7" else 0
        # print(
        #     f"Inner Count log: {holiday_cnt} {half_holiday_cnt} {late_cnt} {leave_early_cnt} {absence_cnt} {trip_cnt} {half_trip_cnt}"
        # )

        real_time_sum_append = real_work_times.append
        over_time_append = over_times.append
        nurse_holiday_append = nurse_holiday_works.append
        # setting_time.staff_id = one_person_attendance.STAFFID
        # setting_time.sh_starttime = one_person_attendance.STARTTIME
        # setting_time.sh_endtime = one_person_attendance.ENDTIME
        # setting_time.notifications = (
        #     one_person_attendance.NOTIFICATION,
        #     one_person_attendance.NOTIFICATION2,
        # )
        # setting_time.sh_overtime = one_person_attendance.OVERTIME
        # setting_time.sh_holiday = one_person_attendance.HOLIDAY
        setting_time = calc_time_factory.get_instance(one_person_attendance.STAFFID)
        setting_time.set_data(
            one_person_attendance.STARTTIME,
            one_person_attendance.ENDTIME,
            (
                one_person_attendance.NOTIFICATION,
                one_person_attendance.NOTIFICATION2,
            ),
            one_person_attendance.OVERTIME,
            one_person_attendance.HOLIDAY,
        )

        print(f"ID: {one_person_attendance.STAFFID}")
        actual_work_time = setting_time.get_actual_work_time()
        calc_real_time = setting_time.get_real_time()
        over_time = setting_time.get_over_time()
        nurse_holiday_work_time = setting_time.calc_nurse_holiday_work()
        # except TypeError as e:
        #     msg = f"{e}: {one_person_attendance.STAFFID}"
        #     return render_template(
        #         "error/403.html", title="Exception message", message=msg
        #     )
        # else:
        # real_time_sum.append(calc_real_time)
        real_time_sum_append(calc_real_time)
        if one_person_attendance.OVERTIME == "1" and contract_code != 2:
            # over_time_0.append(over_time)
            over_time_append(over_time)
        if nurse_holiday_work_time != 9.99:
            # syukkin_holiday_times_0.append(nurse_holiday_work_time)
            nurse_holiday_append(nurse_holiday_work_time)

        print(f"{one_person_attendance.WORKDAY.day} 日")
        # print(f"Real time: {calc_real_time}")
        # print(f"Actual time: {actual_work_time}")
        # print(f"Real time list: {real_work_times}")
        # print(f"Over time list: {over_times}")
        # print(f"Nurse holiday: {nurse_holiday_works}")

        # ここで宣言された変数は“+=”不可
        # work_time_sum_60: float = 0.0
        # 🙅 work_time_sum_60 += AttendanceDada[one_person_attendance.WORKDAY.day][14]

        actual_second = actual_work_time.total_seconds()
        workday_count += 1 if actual_second != 0.0 else 0

        actual_time_sum += actual_second
        time_sum_normal = actual_time_sum / 3600
        # 【項目12】
        actual_time_rnd = Decimal(time_sum_normal).quantize(
            Decimal("0.01"), ROUND_HALF_UP
        )

        w_h = actual_time_sum // (60 * 60)
        w_m = (actual_time_sum - w_h * 60 * 60) // 60
        # 【項目11】
        actual_time60 = w_h + w_m / 100

        real_sum: int = sum(real_work_times)
        w_h = real_sum // (60 * 60)
        w_m = (real_sum - w_h * 60 * 60) // 60
        # 【項目13】
        real_time = w_h + w_m / 100
        # real_time_10 = real_sum / (60 * 60)

        over_sum: int = sum(over_times)
        o_h = over_sum // (60 * 60)
        o_m = (over_sum - o_h * 60 * 60) // 60
        # 【項目17】
        over60 = o_h + o_m / 100

        over10 = over_sum / (60 * 60)
        # 【項目18】
        over10_rnd = Decimal(over10).quantize(Decimal("0.01"), ROUND_HALF_UP)

        sum_nrs: int = sum(nurse_holiday_works)
        h_h = sum_nrs // (60 * 60)
        h_m = (sum_nrs - h_h * 60 * 60) // 60
        # 【項目22】
        holiday_work60 = h_h + h_m / 100

        holiday_work_10 = sum_nrs / (60 * 60)
        # 【項目23】
        holiday_work10_rnd = Decimal(holiday_work_10).quantize(
            Decimal("0.01"), ROUND_HALF_UP
        )

        sum_dict: Dict[str, int] = output_rest_time(
            one_person_attendance.NOTIFICATION, one_person_attendance.NOTIFICATION2
        )
        timeoff += sum_dict.get("Off")
        halfway_through += sum_dict.get("Through")

    result_series = pds(
        [
            on_call_cnt,
            on_call_holiday_cnt,
            on_call_correspond_cnt,
            engel_correspond_cnt,
            actual_time60,
            actual_time_rnd,
            real_time,
            workday_count,
            holiday_cnt,
            half_holiday_cnt,
            over60,
            over10_rnd,
            late_cnt,
            leave_early_cnt,
            absence_cnt,
            holiday_work60,
            holiday_work10_rnd,
            trip_cnt,
            half_trip_cnt,
            reflesh_cnt,
            distance_sum,
            timeoff,
            halfway_through,
        ],
        index=[
            "オンコール平日担当回数",
            "オンコール土日担当回数",
            "オンコール対応件数",
            "エンゼルケア対応件数",
            "実働時間計",
            "実働時間計（１０進法）",
            "リアル実働時間",
            "実働日数",
            "年休（全日）",
            "年休（半日）",
            "時間外",
            "時間外（１０進法）",
            "遅刻",
            "早退",
            "欠勤",
            "祝日手当時間",
            "祝日手当時間（１０進法）",
            "出張（全日）",
            "出張（半日）",
            "リフレッシュ休暇",
            "走行距離",
            "時間休",
            "中抜け",
        ],
        name=one_person_attendance.STAFFID,
    )

    return result_series
