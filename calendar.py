from datetime import date, timedelta
import itertools


def to_ints(arr):
    return map(int, arr)

def splice(arr, amt):
    if len(arr) < amt:
        return [arr]

    ret = list()

    for i in range(0, amt + 1, 7):
        ret.append(arr[i: i + amt])

    return ret

def true_for_all(days):
    weeks = splice(days, 7)
    capture = atleast(map(all, zip(*weeks)), 7)

    return list(itertools.chain(*map(lambda week: map(
        lambda (i, v): 1 if v and capture[i % 7] else 0, enumerate(week)),
        weeks)))

def atleast(arr, amt):
    if(len(arr) < amt):
        return arr + [0] * (amt - len(arr))

    return arr

def true_for_week(true_all, first_date):
    offset = first_date.weekday()

    return true_all[offset: offset + 7]

def true_for_some(days, true_all):
    return map(lambda (a, b): 1 if a and not b else 0, zip(days, true_all))

def get_date(str):
    return date(*map(int, str.split('-')))

def get_dates(arr, first_date):
    return filter(lambda a: a, map(lambda (i, v): v and first_date + timedelta(days=i), enumerate(arr)))

def main():
    first_date = get_date('2013-11-03')
    days = to_ints(list('10010010100001'))
    overlaps = true_for_all(days)
    sub = true_for_some(days, overlaps)
    sub_dates = get_dates(sub, first_date)
    week_overlaps = true_for_week(overlaps, first_date)

    print first_date.weekday() # should be 6 for Sunday
    print 'days', days
    print 'overlaps', overlaps
    print 'week overlaps', week_overlaps
    print 'sub', sub
    print 'sub dates', sub_dates

if __name__ == '__main__':
    main()