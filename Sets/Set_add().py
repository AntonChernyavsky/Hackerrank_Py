'''
    Task: https://www.hackerrank.com/challenges/py-set-add/problem
'''

if __name__ == "__main__":
    n = int(input())
    s = set()
    for i in range(n):
        s.add(input())
    print(len(s))
