size = int(input())
values = list(map(int, input().split()))
print(sum(values[index] >= values[index - 1] for index in range(1, size)))
