#encoding:utf-8
__author__ = 'qingqing'

from collections import Counter
import time

# count the value sim
def numSim(a,b):
    a = float(a)
    if(a*b==0)  and (abs(a-b)<3):
        return 0.8
    else:
        try:
            return 1.0 - abs(a-b)/max(a,b)
        except:
            return 1.0


# count the longest common subsequence
def longSim(L1,L2):
    m =len(L1)
    n = len(L2)
    if m == 0 and n == 0:
        return 1.0
    elif (m*n==0):
        if m<10 or n<10:
            return 0.3
        else:return 0.0
    else:
        c1 = Counter(L1)
        c2 = Counter(L2)
        d1 = dict(c1)
        d2 = dict(c2)
        count = 0
        for i in set(c1)&set(c2):
            count += min(d1[i],d2[i])
        return float(count)/max(m,n)


#count the jaccard
def jaccardSim(s1,s2):
    if len(s1) == 0.0 and len(s2) ==0.0:
        return 0.1
    else:
        return float(len(set(s1)&set(s2)))/len(set(s1)|set(s2))


#count the string edit distance2
def editDisSim2(s1,s2):
    m = len(s1)
    n = len(s2)
    if m == 0 and n == 0:
        return 1.0
    elif (m*n==0):
        if m<10 or n<10:
            return 0.3
        else:
            return 0.0
    else:
        colsize = m + 1
        matrix = []
        for i in range((m + 1) * (n + 1)):
            matrix.append(0)
        for i in range(colsize):
            matrix[i] = i
        for i in range(n + 1):
            matrix[i * colsize] = i
        for i in range(n + 1)[1:n + 1]:
            for j in range(m + 1)[1:m + 1]:
                cost = 0
                if s1[j - 1] == s2[i - 1]:
                    cost = 0
                else:
                    cost = 1
                minValue = matrix[(i - 1) * colsize + j] + 1
                if minValue > matrix[i * colsize + j - 1] + 1:
                    minValue = matrix[i * colsize + j - 1] + 1
                if minValue > matrix[(i - 1) * colsize + j - 1] + cost:
                    minValue = matrix[(i - 1) * colsize + j - 1] + cost
                matrix[i * colsize + j] = minValue
        return 1.0 -float(matrix[n * colsize + m]) / max(m,n)


#count the string edit distance1
def editDisSim(s1,s2):
    m =len(s1)
    n = len(s2)
    if m == 0 and n == 0:
        return 1.0
    elif (m*n==0):
        if m<10 or n<10:
            return 0.3
        else:return 0.0
    else:
        data = [[0 for c in range(n + 1)] for r in range(m + 1)]
        for r in range(m+1):
            for c in range(n+1):
                if not r or not c:
                    data[r][c]=r+c
                else:
                    data[r][c] = min(data[r][c - 1] + 1, data[r - 1][c] + 1, data[r - 1][c - 1] + (s1[r - 1] != s2[c - 1]))
        return 1.0-float(data[m][n])/max(m,n)


def main():

    k1 = 0
    k2 = 10
    s1 = "1111112222222333333459999"
    s2 = "11111233333334555555555567888888888889"
    set1 = ["chang","qing","a","b","c"]
    set2 = ["changqing","chang"]

    print
    start = time.time()
    print numSim(k1,k2)
    end = time.time()
    print end-start

    print
    start = time.time()
    print editDisSim(s1,s2)
    end = time.time()
    print end-start

    print
    start = time.time()
    print editDisSim2(s1,s2)
    end = time.time()
    print end-start

    print
    start = time.time()
    print longSim(s1,s2)
    end = time.time()
    print end-start

    print
    start = time.time()
    print jaccardSim(s1,s2)
    end = time.time()
    print end-start

if __name__ == '__main__':

    main()