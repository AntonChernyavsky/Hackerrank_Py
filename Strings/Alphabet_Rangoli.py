'''
    Task: https://www.hackerrank.com/challenges/alphabet-rangoli/problem
'''

import string;

def print_rangoli(size):
    strng=[]
    for i in range(n):
        l='-'.join(string.ascii_lowercase[i:n])
        strng.append((l[::-1]+l[1::]).center(4*n-3, '-'))
    strng=strng[::-1]+strng[1::]
    print('\n'.join(strng))

if __name__ == '__main__':
    n = int(input())
    print_rangoli(n)
