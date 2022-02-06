# this function takes two dictionary as parameter each contains a start_date and end_date and check whether
# these two date range overlaps each other  . if overlaps it returns True

def date_range_check(date1, date2):
    d1 = date2["start_date"]
    d2 = date2["end_date"]

    if date1["start_date"] <= d1 and date1["end_date"] >= d1:
        return True
    if date1["start_date"] <= d2 and date1["end_date"] >= d2:
        return True
    if date1["start_date"] <= d1 and date1["end_date"] >= d2:
        return True
    if date1["start_date"] >= d1 and date1["end_date"] <= d2:
        return True

    return False
