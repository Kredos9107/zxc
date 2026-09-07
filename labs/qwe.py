n, k = map(int, input().split())
s = []


for _ in range(n):
    s.append(input().strip())

def test(x):
    if x == 0:
        return 1
    N = 4 * n + 2
    S = 0
    T = 4 * n + 1
    C = [[0] * N for _ in range(N)]
    
    for i in range(n):
        C[S][1 + i] = x
        C[1 + i][1 + n + i] = k


    for j in range(n):
        C[2 * n + 1 + j][3 * n + 1 + j] = k
        C[3 * n + 1 + j][T] = x


    for i in range(n):
        for j in range(n):
            if s[i][j] == '1':
                C[1 + i][3 * n + 1 + j] = 1
            else:
                C[1 + n + i][2 * n + 1 + j] = 1
    
    F = 0
    while True:


        P = [-1] * N
        Q = [S]
        P[S] = S

        for v in Q:
            k1=v
            for to in range(N):
                if P[to] == -1 and C[v][to] > 0:
                    P[to] = v
                    Q.append(to)
        if P[T] == -1:
            break
        v = T

        A = 10**9
        while v != S:
            k1=v
            u = P[v]
            if C[u][v] < A:
                A = C[u][v]
            v = u
        v = T

        while v != S:


            u = P[v]
            C[u][v] -= A
            C[v][u] += A
            v = u
        F += A
    return F == n * x


L, R = 0, n
R2 = 0

while L <= R:

    M = (L + R) // 2
    if test(M):


        R2 = M
        L = M + 1
    else:
        R = M - 1


print(R2)