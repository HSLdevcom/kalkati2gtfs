def to_booleans(arr):
    return map(lambda a: True if a == '1' else False, arr)

def splice(arr, amt):
    ret = list()

    for i in range(0, amt + 1, 7):
        ret.append(arr[i: i + amt])

    return ret

def true_for_all(weeks):
    return map(all, zip(*weeks))

def true_for_some(weeks, trueAll):
    return map(lambda week: map(
        lambda v: v[1] and not trueAll[v[0] % 7], enumerate(week)),
        weeks)

def main():
    a = to_booleans(list('10010010100001'))
    weeks = splice(a, 7)
    overlaps = true_for_all(weeks)
    sub = true_for_some(weeks, overlaps)

    print 'weeks', weeks
    print 'overlaps', overlaps
    print 'sub', sub

if __name__ == '__main__':
    main()