## 考え方

N個の測定値を順番に比べ、直前の値より大きくなった回数を求めてください。同じ値は数えません。

公開例は3から5、5から9の2回増えます。途中の5から5は同じ値なので数えません。

## 解答例（Python）

```python
size = int(input())
values = list(map(int, input().split()))
print(sum(values[index] > values[index - 1] for index in range(1, size)))
```

問題の入力形式に従って標準入力から読み、答えだけを標準出力へ出します。
