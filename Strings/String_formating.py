'''
    Task: https://www.hackerrank.com/challenges/python-string-formatting/problem
'''

def print_formatted(number):
    width=len(bin(n)[2:])
    for i in range(1, n+1):
        str='{0:{width}} {0:{width}o} {0:{width}X} {0:{width}b}'.format(i, width=width) 
        print(str)

if __name__ == '__main__':
    n = int(input())
    print_formatted(n)