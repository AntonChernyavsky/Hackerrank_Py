'''
    Task: https://www.hackerrank.com/challenges/np-zeros-and-ones/problem
'''

import numpy

tpl = tuple(map(int, input().split()))

zero_array = numpy.zeros(tpl, dtype = numpy.int)
ones_array = numpy.ones(tpl, dtype = numpy.int)
print(zero_array)
print(ones_array)