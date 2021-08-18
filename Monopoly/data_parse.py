'''
    Code to parse the monopoly code and the winning card numbers
'''

class Code():

    char_dict = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
    
    def __init__(self, input_str: str):
        self.num = 0
        self.input = input_str
    
    def __next__(self):
        num = self.num
        self.num += 1
        return self.input[num]

    def __str__(self):
        return self.input

    def composition(self):
        nums = 0
        chars = 0
        
        for char in self.input:
            try:
                char = int(char)
            except ValueError:
                chars += 1
            else:
                nums += 1

        return nums, chars

    def numberRepresent(self):
        return None  

class fileReader():

    file = []

    def __init__(self, file_name: str):
        codes = open(file_name)
        for code in codes:
            self.file.append(code[:-1])

    def txt(self):
        return self.file