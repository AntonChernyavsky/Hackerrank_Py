'''
    Task: https://www.hackerrank.com/challenges/python-lists/problem
'''

if __name__ == '__main__':
    N = int(input())
    lst = []
    for _ in range(N):        
        l=input().split()
        cmd = l[0]
        attr = l[1:]   
        if cmd=='print':
            print(lst)
        else:
            exec('lst.'+cmd+'('+','.join(attr)+')')