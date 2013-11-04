from datetime import date
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

def true_for_week(trueAll, firstDate):
    offset = firstDate.weekday()

    return trueAll[offset: offset + 7]

def true_for_some(days, trueAll):
    return map(lambda (a, b): 1 if a and not b else 0, zip(days, trueAll))

def get_date(str):
    return date(*map(int, str.split('-')))

def main():
    firstDate = get_date('2013-11-03')
    days = to_ints(list('10010010100001'))
    overlaps = true_for_all(days)
    sub = true_for_some(days, overlaps)
    weekOverlaps = true_for_week(overlaps, firstDate)

    print firstDate.weekday() # should be 6 for Sunday
    print 'days', days
    print 'overlaps', overlaps
    print 'week overlaps', weekOverlaps
    print 'sub', sub

if __name__ == '__main__':
    main()