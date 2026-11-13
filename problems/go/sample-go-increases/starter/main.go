package main

import "fmt"

func main() {
	var size int
	fmt.Scan(&size)
	values := make([]int, size)
	for index := range values {
		fmt.Scan(&values[index])
	}
	increases := 0
	fmt.Println(increases)
}
