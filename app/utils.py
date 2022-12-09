def interval(l, n):
    w = (l[1] - l[0]) // n
    return [[l[0]+i*w, l[0]+(i+1)*w] for i in range(n)]
