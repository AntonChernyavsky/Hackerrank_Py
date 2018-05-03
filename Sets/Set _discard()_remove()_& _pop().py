'''
    Task: https://www.hackerrank.com/challenges/py-set-discard-remove-pop/problem
'''

n = int(input())
s = set(map(int, input().split()))
cmd_num = int(input())
for i in range(cmd_num):
    elem=input().split()
    cmd = 's.'+elem[0]+'('+''.join(elem[1:])+')'
    eval(cmd)
print(sum(s))
