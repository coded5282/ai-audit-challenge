import pandas as pd

def remove_numbers(file_name, updated_file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            if lines[i][0].isdigit():
                lines[i] = lines[i][lines[i].find('.')+2:]
    with open(updated_file_name, 'w') as f:
        f.writelines(lines)

#remove_numbers('./car_adjectives.txt', './updated_car_adjectives.txt')

def read_file(filename, output_filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    df = pd.DataFrame(lines, columns=['Review'])
    df.to_csv(output_filename + '.tsv', sep='\t', index=False)
    return

read_file('./updated_car_adjectives.txt', './car_ad_reviews')
