'''
    Main python script running all of the bits of code
'''

from overhead import *

def main():
    
    str_list = dp.fileReader('codes.txt').txt()
    print(str_list)
    code_num = 0
    for item in str_list:
        
        code_str = f'code{code_num}'
        locals()[code_str] = dp.Code(item)
        
        print(f'Composition of {str(locals()[code_str])}')
        nums, chars = locals()[code_str].composition()
        print(f'Numbers: {nums}\nCharacters: {chars}\n')
        print(f'Total: {nums + chars}\n')
        code_num += 1

main()