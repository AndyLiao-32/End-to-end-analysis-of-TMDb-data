""" wrangling.py - utilities to supply data to the templates.

This file contains a pair of functions for retrieving and manipulating data
that will be supplied to the template for generating the table."""
import csv

def username():
    return 'tliao32'

def data_wrangling():
    with open('data/movies.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        table = list()
        count = 0
        # Feel free to add any additional variables
        ...
        
        # Read in the header
        for header in reader:
            break
        
        # Read in each row
        for row in reader:
            table.append(row)
            
            # Only read first 100 data rows - [2 points] Q5.a
            count += 1
            
            # if read 100 files, break
            if count == 100: break
            ...

        # Order table by the last column - [3 points] Q5.b
        # print(table[0][2])
        new_table = []
        # max = table[0]
        # print(max)

        '''
        loop through all 100 items in the table and switch bigger value to the top, 
        smaller one to the bottom, then assign each item into new_table to make a sorted table.
        '''
        while table:
            max = table[0]  
            for item in table: 
                if float(item[2]) > float(max[2]):
                    max = item
            new_table.append(max)
            table.remove(max)    

        # print(new_table[0])

        ...
    
    return header, new_table

