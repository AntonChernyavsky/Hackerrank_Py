'''
    Task: https://www.hackerrank.com/challenges/nested-list/problem
'''

if __name__ == '__main__':
    l=[]
    for _ in range(int(input())):
        name = input()
        score = float(input())
        l.append([name, score])        

    def getName(inPutStr):
        return inPutStr[0]
    def getScore(inPutInt):
        return inPutInt[1]

    l.sort(key=getScore, reverse=True)
    val=min(l, key=getScore)
    idx=l.index(val)

    val=l[idx-1][1]
    l.sort(key=getName)
    
    for i in range(len(l)):
        if l[i][1]==val:
             print(l[i][0])