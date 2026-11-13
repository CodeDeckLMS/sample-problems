size = int(input())
values = list(map(int, input().split()))
print(sum(value >= 0 for value in values))
