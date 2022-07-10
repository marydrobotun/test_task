
def task(array):
    for i, item in enumerate(array):
        if array[i] == '0':
            return i


print(task("111111111110000000000000000"))
# >> OUT: 11
