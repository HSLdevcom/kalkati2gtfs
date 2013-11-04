import itertools


def to_booleans(arr):
    return map(lambda a: True if a == '1' else False, arr)

def splice(arr, amt):
    ret = list()

    for i in range(0, amt + 1, 7):
        ret.append(arr[i: i + amt])

    return ret

def true_for_all(days):
    weeks = splice(days, 7)
    capture = map(all, zip(*weeks))

    return list(itertools.chain(*map(lambda week: map(
        lambda v: v[1] and capture[v[0] % 7], enumerate(week)),
        weeks)))

def true_for_some(days, trueAll):
    return map(lambda (a, b): a and not b, zip(days, trueAll))

def main():
    days = to_booleans(list('10010010100001'))
    overlaps = true_for_all(days)
    sub = true_for_some(days, overlaps)

    print 'days', days
    print 'overlaps', overlaps
    print 'sub', sub

if __name__ == '__main__':
    main()