import datetime as dt


def gen_date_list(start_date, days):
    date_obj = dt.datetime.strptime(str(start_date), "%Y%m%d")
    y, m, d = date_obj.year, date_obj.month, date_obj.day
    date_list = [date_obj.strftime("%Y/%m/%d")]
    for i in range(1, days + 1):
        date_list.append((date_obj - dt.timedelta(days=i)).strftime("%Y/%m/%d"))
    return date_list[::-1], y, m, d


def clean_mixed_item(data):
    """把 list 裡面混有日期和事件的部分切分開
    ex: ['1615大山', '除權息', '09/08', '星期日']
    """
    new_data = []
    for i, lst in enumerate(data):
        mixed = 0
        for j, item in enumerate(lst):
            if j and "/" in item:
                mixed = j
        if mixed:
            new_data.append(lst[:mixed])
            new_data.append(lst[mixed:])
        else:
            new_data.append(lst)
    data = new_data.copy()
    del new_data
    return data


def gen_date_positions(data):
    """紀錄 data list 中日期 item 的位置
    這樣才知道要在哪邊切分時間
    """
    date_ids = []
    for i, lst in enumerate(data):
        for item in lst:
            if "/" in item:
                date_ids.append(i)
    return date_ids


def arrange_events(data, date_ids, date_list):
    """把整個列表的事件分時間、單項切乾淨"""
    events = {k: [] for k in date_list}
    for i, idx in enumerate(date_ids):
        # 切分各個時間的事件 list
        if i == len(date_ids) - 1:
            _events = data[date_ids[i] :]
        else:
            _events = data[date_ids[i] : date_ids[i + 1]]
        # 把兩個事件連在一起的 item 切分開
        clean_events = []
        for eve_lst in _events[1:]:
            digit_ids = []
            for j, eve in enumerate(eve_lst):
                if [s for s in eve if s.isdigit()]:
                    digit_ids.append(j)
            if digit_ids:
                for j, eve_id in enumerate(digit_ids):
                    # 切出乾淨的單個事件
                    if j == len(digit_ids) - 1:
                        _eve_lst = eve_lst[digit_ids[j] :]
                    else:
                        _eve_lst = eve_lst[digit_ids[j] : digit_ids[j + 1]]
                    # 把股票代號和名稱切分開
                    if len(_eve_lst) == 2:
                        if _eve_lst[0][0].isdigit():
                            _eve_lst = [_eve_lst[0][:4], _eve_lst[0][4:], _eve_lst[1]]
                        else:
                            _eve_lst = ["", _eve_lst[0], _eve_lst[1]]
                    if len(_eve_lst) == 3:
                        clean_events.append(_eve_lst)
                    else:
                        print(_eve_lst)
        events.update({date_list[i]: clean_events})
    return events
