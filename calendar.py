from datetime import date, timedelta
import itertools


def to_ints(arr):
    return map(int, arr)

def splice(arr, amt):
    if len(arr) <= amt:
        return [arr]

    ret = list()

    for i in range(0, amt + 1, amt):
        ret.append(arr[i: i + amt])

    return ret

def true_for_all(days):
    weeks = splice(days, 7)
    padded_weeks = map(lambda week: atleast(week, 7, 1), weeks)
    return to_ints(map(all, zip(*padded_weeks)) * len(weeks))[0:len(days)]

def atleast(arr, amt, value=0):
    if(len(arr) < amt):
        return arr + [value] * (amt - len(arr))

    return arr

def true_for_week(true_all, first_date):
    offset = 7-first_date.weekday()
    # if there's data for less than a week, expand with zeros
    true_all = atleast(true_all, 7)
    true_week = true_all[:7]
    # rotate the week to start on monday
    return (true_week+true_week)[offset: offset + 7]


def true_for_some(days):
    return map(lambda (a, b): 1 if a and not b else 0, zip(days, true_for_all(days)))

def get_date(str):
    return date(*map(int, str.split('-')))

def get_dates(arr, first_date):
    return filter(lambda a: a, map(lambda (i, v): v and first_date + timedelta(days=i), enumerate(arr)))

def main():
    first_date = get_date('2013-11-03')
    days = to_ints(list('10010010100001'))
    overlaps = true_for_all(days)
    sub = true_for_some(days)
    sub_dates = get_dates(sub, first_date)
    week_overlaps = true_for_week(overlaps, first_date)

    print first_date.weekday() # should be 6 for Sunday
    print 'days', days
    print 'overlaps', overlaps
    print 'week overlaps', week_overlaps
    print 'sub', sub
    print 'sub dates', sub_dates

    for day in "04 05 06 07 08 09 10".split():
        print true_for_week(true_for_all(to_ints(list("01111111"))), get_date("2013-11-"+day))

if __name__ == '__main__':
    main()