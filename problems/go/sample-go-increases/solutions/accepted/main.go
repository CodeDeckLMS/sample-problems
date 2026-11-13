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
	for index := 1; index < size; index++ {
		if values[index] > values[index-1] {
			increases++
		}
	}
	fmt.Println(increases)
}
