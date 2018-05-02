'''
    Task: https://www.hackerrank.com/challenges/symmetric-difference/problem
'''

n=input()
s1=set(map(int, input().split()))
m=input()
s2=set(map(int, input().split()))
out=sorted(s1.difference(s2).union(s2.difference(s1)))
for elem in out:
    print(elem)