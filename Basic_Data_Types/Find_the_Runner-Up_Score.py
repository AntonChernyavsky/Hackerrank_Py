'''
    Task: https://www.hackerrank.com/challenges/find-second-maximum-number-in-a-list/problem
'''

if __name__ == '__main__':
    n = int(input())
    arr = map(int, input().split())

    arr = list(arr)
    arr.sort()
    a = arr.index(max(arr))
    print(arr[a-1])