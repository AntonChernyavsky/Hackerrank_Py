'''
    Task: https://www.hackerrank.com/challenges/designer-door-mat/problem
'''

n, m = map(int, input().split())

width=m
a,b=1,1
for i in range(1, n, 2): 
     print(str('.|.'*i).center(width, '-'))
print ('WELCOME'.center(width, '-'))
for i in reversed(range(1, n, 2)):    
    print(str('.|.'*i).center(width, '-'))
