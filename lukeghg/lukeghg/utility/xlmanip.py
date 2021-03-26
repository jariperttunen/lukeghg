import openpyxl

def find_numeric_part(cell:str):
    for (index,x) in enumerate(cell):
        if x.isnumeric():
            break
    return index

def cut_cell_number(cell:str):
    index = find_numeric_part(cell)
    cell_ls = list(cell)
    cell_ls = cell_ls[:index]
    new_cell = "".join(cell_ls)
    return new_cell
