package main

import "fmt"

func main() {
	var size int
	fmt.Scan(&size)
	count := 0
	for index := 0; index < size; index++ {
		var value int
		fmt.Scan(&value)
		if value >= 0 {
			count++
		}
	}
	fmt.Println(count)
}
