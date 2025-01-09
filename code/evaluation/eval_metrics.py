"""
Imports
"""


"""
Helper Functions
"""
def find_longest_substring_match(unmatched_output, unmatched_correct, output_string, correct_string):
    # print(f"Length o_ix: { len(unmatched_output)}")
    # print(f"Length c_ix: { len(unmatched_correct)}")
    for o_ix in range(0, len(unmatched_output)):
        for c_ix in range(0, len(unmatched_correct)):
            
            # print(f"pair: {o_ix}, {c_ix}")
            a_o, b_o = unmatched_output[o_ix]
            a_c, b_c = unmatched_correct[c_ix]

            sublength = min(len(get(output_string, unmatched_output[o_ix])), len(get(correct_string, unmatched_correct[c_ix])))
            for length in range(sublength, 0, -1):
                print(f"length: {length}")
                substrings_output = generate_substrings(get(output_string,unmatched_output[o_ix]), length)
                substrings_correct = generate_substrings(get(correct_string,unmatched_correct[c_ix]), length)
                
                for i in range(len(substrings_output)):
                    for j in range(len(substrings_correct)):
                        if substrings_output[i] == substrings_correct[j]:                            
                            # print(f"Match found. Length, {length}. Indices. output: {i}, correct: {j}")
                            a__o, b__o = a_o + i, a_o + i + length
                            a__c, b__c = a_c + j, a_c + j + length
                            
                            new_output = []
                            new_correct = []
                            
                            if a__o - 1 >= a_o + 1 :
                                new_output += [(a_o, a__o - 1)]
                            
                            if b__o + 1 <= b_o - 1:
                                new_output += [(b__o + 1, b_o)]
                                
                            if a__c - 1 >= a_c + 1 :
                                new_correct += [(a_c, a__c - 1)]
                            
                            if b__c + 1 <= b_c - 1:
                                new_correct += [(b__c + 1, b_c)]
                                                            
                            return o_ix, c_ix, new_output, new_correct, (a__o, b__o, a__c, b__c)
    
    return None
                            
def load_file(f_path):
    with open(f_path, mode='r') as fp:
        data_string = "\n".join([x.strip() for x in fp.readlines()])

    return data_string

def generate_substrings(text, length):    
    assert length >= 1
    
    start_ix = 0
    max_ix = len(text)
    end_ix = max_ix - length + 1
    
    substring_list = []
        
    for i in range(start_ix, end_ix, 1):
        substring = text[i:(i+length)]
        substring_list.append(substring)
    
    return substring_list
           
def get(text, ixrange):
    return text[ixrange[0]:ixrange[1] ] 
 
def merge(numbers, merge_index):

    new_list = []
    for i in range(len(numbers)):
        if i == merge_index :
            new_list.append(numbers[i])
        elif i == merge_index+ 1:
            continue
        else: # > merge_index + 1
            if numbers[i] > numbers[merge_index + 1]:
                new_list.append(numbers[i] - 1)
            else:
                new_list.append(numbers[i])
                
    return new_list
    
def reduce(base_list):    
    while True:  # if we find any consecutive numbers ,we should merge 
        merge_index = None
        for i in range(len(base_list) - 1):
            if base_list[i] + 1 == base_list[i + 1]: # we found a match
                merge_index = i
                break
        if merge_index is not None: 
            base_list = merge(base_list, merge_index)
        else: # no merges found 
            break 
    
    return base_list    
    
def move_counting(matches):
    # series of (a__o, b__o, a_c, b_c)
    
    # we need to sort these by the third elmeent
    matches.sort(key=lambda x: x[2])
    reference_permutation = list(enumerate(matches))
    output_permutation = reference_permutation.copy()
    output_permutation.sort(key=lambda x: x[1][0])
    
    # removing the length component for each move.. 
    output_permutation = [x[0] for x in output_permutation]
    reference_permutation = [x[0] for x in reference_permutation]
    
    count = 0
    iteration = 0
    while True:
        print("Length of output permutation: ", len(output_permutation))
        print("Iteration (count): ", iteration)
        
        if len(output_permutation) == 1:
            break  # out of the while loop. we reached the identity.
        
        index_ = 0
        num_red = 0
                
        for i in range(len(output_permutation)):
            permuted_list = output_permutation.copy()
            permute_element = output_permutation[i]
            del permuted_list[i]
            
            
            for j in range(len(permuted_list) + 1):
                print(f"i: {i}, j: {j}")
                new_list = permuted_list[:j] + [permute_element] + permuted_list[j:]
                new_list_reduced = reduce(new_list)
                number_reduces =  len(new_list) - len(new_list_reduced)
                
                if number_reduces > num_red:
                    num_red = number_reduces
                    index_ = (i, j, new_list_reduced)
                    
                # for our case, this can be more than 3... it can be as high as 13..
                print("Number reduces: ", number_reduces)

            if num_red > 5:
                break
                    
        if index_ != 0: # reduce by the max 
            output_permutation = index_[2]    

        count = count + 1
        iteration = iteration + 1

    return count 

"""
Basic Input Variables 
"""
firstpass_cost = 0
zoned_cost = 0
for OUTFILE_PATH in ['../../gold-data-creation/Boas_1902_Jesup_VolV_AMNH_pt1/firstpass/36.txt', '../../gold-data-creation/Boas_1902_Jesup_VolV_AMNH_pt1/zoned/36.txt']:
    REFFILE_PATH = '../../gold-data-creation/Boas_1902_Jesup_VolV_AMNH_pt1/gold/36.txt'

    """
    Code Begins
    """
    output_string = load_file(OUTFILE_PATH) 
    correct_string = load_file(REFFILE_PATH)

    print(len(output_string)) # 3000  --- length 1: 30000

    matches = []

    unmatched_output = [(0,len(output_string))]
    unmatched_correct = [(0,len(correct_string))]

    iteration_num = 1
    exit_flag = True 
    while exit_flag:
        print(f"Iteration number: {iteration_num}")
        iteration_num += 1
        
        if len(unmatched_correct) > 0 and len(unmatched_output)> 0:
            return_value = find_longest_substring_match(unmatched_output, unmatched_correct, output_string, correct_string)
            if return_value  is not None:
                o_ix, c_ix, new_output, new_correct, match_range = return_value 

                del unmatched_output[o_ix]
                del unmatched_correct[c_ix]

                unmatched_output += new_output
                unmatched_correct += new_correct

                matches.append(match_range)   
            else:
                exit_flag = False  
        else:
            exit_flag = False 
            
    print("Computing i/d/m")      
    if len(unmatched_output) > 0:
        deletions = sum([x[1] - x[0] for x in unmatched_output])
    else:
        deletions = 0
    if len(unmatched_correct) > 0:
        insertions = sum([x[1] - x[0] for x in unmatched_correct])
        # for x in unmatched_correct:
        #     print(f"{correct_string[x[0]:x[1]]}")
    else:
        insertions = 0  
    moves = move_counting(matches)
    print("-----------------")

    print("Insertions: ", insertions)
    print("Deletions: ", deletions)
    print("Moves: ", moves)

    print("-----------------")
    w_i, w_d, w_m = 1, 1, 2 # for T = 1
    cost = w_i * insertions + w_d * deletions + w_m * moves
    
    
    if "firstpass" in OUTFILE_PATH:
        print("Firstpass cost: ", cost)
        firstpass_cost = cost 
    else:
        print("Zoned cost: ", cost)
        zoned_cost = cost 

print("Calibrated cost: ", firstpass_cost - zoned_cost )


# Length of output permutation: 735





