# A simple sorting function with a mistake
def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - i - 1):
            if arr[j] > arr[j + 1]:  # Sorting condition
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return   # What if the input is not a list?
