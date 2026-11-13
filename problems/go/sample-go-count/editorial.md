## 考え方

N個の測定値のうち、0以上の値が何個あるか数えてください。

公開例の0、7、4は0以上なので3個です。0も数える点と、個数を出力する点を確認します。

## 解答例（Python）

```python
size = int(input())
values = list(map(int, input().split()))
print(sum(value >= 0 for value in values))
```

問題の入力形式に従って標準入力から読み、答えだけを標準出力へ出します。
