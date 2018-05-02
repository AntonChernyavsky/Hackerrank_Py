'''
    Task: https://www.hackerrank.com/challenges/np-transpose-and-flatten/problem
'''

import numpy

N, M = map(int, input().split())
my_array = numpy.array([input().split() for _ in range(N)], int)
print(numpy.transpose(my_array))
print(my_array.flatten())