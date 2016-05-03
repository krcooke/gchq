#!/usr/bin/python

import time
from PIL import Image
from PIL import ImageOps
import numpy as np


def build_possibilities (row):

    sum_black = sum(row)
    length = len(row)
    gaps = length - 1
    output = []

    # the max amount of white is 25 - the sum of black
    max_white = 25 - sum_black

    # to itterate through the starting point 0 to 24
    max_start = 25 - sum_black - gaps
    start = 0
    start_offset = 0
    
    while (start <= max_start) :
        output_rows = recursive_block(row, max_white)
        padding = [0 for i in range(0, start_offset)]
        combined_padding = []
        for i in output_rows :
            combined_padding.append(padding + i)
        output += combined_padding
        max_white -= 1 
        start += 1
        start_offset += 1

    return output

# Recursive block setter
def recursive_block(input_blocks, input_white) :

    white = int(input_white)
    # Resultset
    result_set = []

    # sets the first item in the block list, sets it black and 1 white block
    current_block = input_blocks[0]
    remaining_blocks = input_blocks[1:]
    new_block = [1 for i in range(0, current_block)]

    # If the final block, then just pad out with 0 and return it
    if len(input_blocks) == 1:
        padding = [0 for i in range(0, white)]
        return [new_block + padding]

    # Decrement the the white space and add one to the block
    white -= 1
    new_block.append(0)

    # then loops from 0 to remaining white space - remaining blocks + 1
    # e.g. 5 white - 2 blocks + 1
    # e.g. 10 white - 3 blocks + 1
    spare_white = white - len(remaining_blocks) + 1
    
    # If we have no spare whites, then no need to loop adding extra white spaces
    combined_results = []
    if spare_white < 1 :
        combinations = recursive_block(remaining_blocks, white)

        for i in combinations :
            joined_result = new_block + i
            combined_results.append(joined_result)

    else :
        while spare_white >= 0:
            # calls itself with the current row, remaining blocks and remaining white space
            # If no blocks left, pad out with white
            combinations = recursive_block(remaining_blocks, white)

            for i in combinations :
                joined_result = new_block + i
                combined_results.append(joined_result)
            new_block.append(0)
            white -= 1
            spare_white -= 1

    return combined_results

# opens the files and builds the combinations
def get_combinations(input_file) :
    loaded_file = open(input_file, 'r')
    lines = list(loaded_file)
    combinations = []
    for line in lines :
        csv_str = line.split(',')
        row = [int(i) for i in csv_str]
        combinations.append(build_possibilities(row))
    loaded_file.close
    return combinations

# Loops through all of the options of a row/column and find the constant
def find_certain_values (combinations, answer, zeros) :

    # Looping through the 25 rows/columns
    for row_index in range(25) :
        row = combinations[row_index]

        # If there is only row, then just set the row
        if len(row) == 1 :
            answer[row_index] = row[0]
            zeros[row_index] = row[0]
            continue

        # loop through the combinations and do logical AND of the answers
        new_row_0 = [0 for x in range(25)]
        new_row_1 = [1 for x in range(25)]

        for i in range(25) :
            new_row_0[i] = row[0][i] & row[1][i]
            new_row_1[i] = row[0][i] | row[1][i]
            
        for combination_index in range(2,len(row)) :
            current_row = row[combination_index]
            for i in range(25) :
                new_row_0[i] = new_row_0[i] & current_row[i]
                new_row_1[i] = new_row_1[i] | current_row[i]

        # OR it with the current answer
        for i in range(25) :
            answer[row_index][i] = answer[row_index][i] | new_row_0[i]
            zeros[row_index][i] = zeros[row_index][i] & new_row_1[i]

# Printing csv files
def dump_output (itteration):
    filename = '/tmp/result_' + str(itteration)
    output_results = open(filename + '.csv', 'wb')

    a = np.array(answer)
    n = 8 
    result = np.kron(a, np.ones((n,n)))
    for i in result :
        output_results.write(bytes(",".join(str(int(x)) for x in i) + "\n", 'UTF-8'))
    output_results.close()

    img = Image.new('1', (200, 200))
    pixels = img.load()

    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pixels[i, j] = not int(result[i][j])
    img.save(filename + '.bmp')

# Read the combinations for each row and delete options that are not viable
def scan_combinations (combinations, answer, zeros) :

    # Loop through the rows/columns
    for row_index in range(25) :
        row = combinations[row_index]

        current_answer_0 = answer[row_index]
        current_answer_1 = zeros[row_index]

        remaining_combinations = []
        combinations_count = len(combinations[row_index])
        for combination in row :

            viable = 1
            for i in range(25) :
                if (current_answer_0[i] == 1) & (combination[i] != 1) :
                    viable = 0
                    break
                if (current_answer_1[i] == 0) & (combination[i] == 1) :
                    viable = 0
                    break

            if viable == 1 :
                remaining_combinations.append(combination)
        combinations[row_index] = remaining_combinations
        if len(combinations[row_index]) < combinations_count :
            print('Reducing combinations: ', combinations_count, '->', len(combinations[row_index]))

# Set initial values we already know
def set_initial_inputs (input_file, answer) :

    loaded_file = open(input_file, 'r')
    lines = list(loaded_file)
    for line in lines :
        csv_str = line.split(',')
        x = csv_str[0]
        y = csv_str[1]
        answer[int(x)][int(y)] = 1
    loaded_file.close
    
# Main program
# Initialise the answer grid
answer = [[0 for x in range(25)] for x in range(25)]
zeros = [[1 for x in range(25)] for x in range(25)]

# Reads in the instructions and returns combinations for each instructiuon row
rows_combinations = get_combinations('../data/input_horizontal.csv')
columns_combinations = get_combinations('../data/input_vertical.csv')

# Set the initial values we already know
set_initial_inputs('../data/input_answer.csv', answer)

# Analysis the combinations for the rows/columns and find the definite options...
#XXX Change this so that it tests the number of combinations is tested.
for i in range(7) :
    print ("Itteration: ", i)
    find_certain_values(rows_combinations, answer, zeros)
    answer = list(map(list, zip(*answer)))
    zeros = list(map(list, zip(*zeros)))
    find_certain_values(columns_combinations, answer, zeros)
    answer = list(map(list, zip(*answer)))
    zeros = list(map(list, zip(*zeros)))
    scan_combinations(rows_combinations, answer, zeros)
    answer = list(map(list, zip(*answer)))
    zeros = list(map(list, zip(*zeros)))
    scan_combinations(columns_combinations, answer, zeros)
    answer = list(map(list, zip(*answer)))
    zeros = list(map(list, zip(*zeros)))
    dump_output(i)
