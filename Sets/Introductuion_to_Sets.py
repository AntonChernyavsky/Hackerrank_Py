'''
    Task: https://www.hackerrank.com/challenges/py-introduction-to-sets/submissions/code/71706693
'''

def average(array):
    array=set(array)
    return sum(array)/len(array)

if __name__ == '__main__':
    n = int(input())
    arr = list(map(int, input().split()))
    result = average(arr)
    print(result)