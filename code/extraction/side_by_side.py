import json 
import os 

# RUN COMMAND
# python code/extraction/side_by_side.py

# Preprocessing function to create a Words json
def get_words_from_json(json_input):

    # Step 1: Get all the words in a separate JSON. 
    # print('getting all the words in a separate json')
    words_json_input = {}
    word_count = 0
    for key1 in json_input.keys():
        if key1 != "fulltext":
            block = json_input[key1]
            if 'paras' in block.keys():
                paras_input = block['paras']
                for para in paras_input:
                    if 'words' in para.keys():
                        words = para['words']
                        for word in words:
                            words_json_input[str(word_count)] = word
                            word_count += 1
    
    # Step 2: Find which words are duplicates. 
    # print("Finding which words are duplicates")
    duplicates = []
    for k in words_json_input.keys():
        bbox1 = words_json_input[k]['bounding_box']
        xrange1 = set(range(bbox1[0][0], bbox1[1][0]))
        yrange1 = set(range(bbox1[0][1], bbox1[3][1]))
    
        for k2 in words_json_input.keys():
            if k2 != k:
                bbox2 = words_json_input[k2]['bounding_box']
                xrange2 = set(range(bbox2[0][0], bbox2[1][0]))
                yrange2 = set(range(bbox2[0][1], bbox2[3][1]))
                
                # check overlap 
                try:
                    xratio1 = len(xrange1.intersection(xrange2))/len(xrange1)
                    yratio1 = len(yrange1.intersection(yrange2))/len(yrange1)
                    
                    xratio2 = len(xrange2.intersection(xrange1))/len(xrange2)
                    yratio2 = len(yrange2.intersection(yrange1))/len(yrange2)
                    
                    if xratio1 > 0.85 and yratio1 > 0.85 and xratio2 > 0.85 and yratio2 > 0.85: 
                        if (k,k2) not in duplicates and (k2, k) not in duplicates:
                            duplicates.append((k, k2))
                except  ZeroDivisionError:
                    pass
          
                   
    # print("Duplicates are:")
    # print(duplicates)
    # Step 3: Randomly delete one of the 2 for each entry
    try:
        for d in duplicates:
            words_json_input.pop(d[0])
    except:
        pass
    
    return words_json_input

def group_words_by_line(sorted_midpoints, margin=50):
    
    line_level_data = []
    
    group = []
    for i in range(len(sorted_midpoints)):
        if len(group) == 0:
            group.append(sorted_midpoints[i])
        else:
            average = sum([x[1] for x in group])/len(group)
            if sorted_midpoints[i][1] > average + 50:
                line_level_data.append(group)
                group = [sorted_midpoints[i]]
            else:
                group.append(sorted_midpoints[i])
    line_level_data.append(group)
    return line_level_data

def get_line(loaded_words):
        
   # get the mid-point of all the word-level boxes. 
   ix_mid_y = []
   for word_ix in loaded_words.keys():
       bounding_box = loaded_words[word_ix]['bounding_box'] # [[3047, 3869], [3062, 3869], [3061, 3933], [3046, 3933]]
       top_left, _, _, bottom_left = bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3]
       mid_y = (top_left[1] + bottom_left[1])/2
       loaded_words[word_ix]['mid-y'] = mid_y
       ix_mid_y.append((word_ix, mid_y))
   sorted_mid_y_ix = sorted(ix_mid_y, key = lambda x: x[1])
   
   line_level_groups = group_words_by_line(sorted_mid_y_ix)
   
   line_level_word_groups = []
   for group in line_level_groups:
       ixs = [x[0] for x in group]
       word_group = [loaded_words[word_ix] for word_ix in loaded_words.keys() if word_ix in ixs]
       line_level_word_groups.append(word_group)

   return line_level_word_groups

def sort_x_axis(line):
    word_ixs = []
    for word in line:
        bounding_box = word['bounding_box']
        top_left, top_right, _, _ = bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3]
        mid_x = (top_left[0] + top_right[0])/2
        word['mid-x'] = mid_x
        word['top-left-x'] = top_left[0]
        word['top-right-x'] = top_right[0]
        word_ixs.append((word, mid_x))
    
    sorted_word_ixs = sorted(word_ixs, key = lambda x: x[1])
    sorted_line = [x[0] for x in sorted_word_ixs]
    
    # sorted_ixs = [x[1] for x in sorted_word_ixs]
    jumps = []
    for i in range(len(sorted_line) - 1):
        jumps.append(sorted_line[i + 1]['top-left-x'] - sorted_line[i]['top-right-x'])
    
    # first see
    
        
    # print(jumps)
    # print([x> 300 for x in jumps])
    # if a jump is > 300 and it is the middle of the page, then we know that we have a split. 
    # and we can get the two anchors (probably for title, or for an image)
    
    
    
    return sorted_line

def get_text(line,search_point_global_value=False):
    fulltext = ""
    if search_point_global_value == False: 
        for word in line:
            fulltext += word['text'].strip() + " "
        return fulltext + "\n"
    else:
        lefttext = ""
        righttext = ""
        for word in line:
            if word['top-right-x'] < search_point_global_value + 5:
                lefttext +=  word['text'].strip() + " "
            else:
                righttext += word['text'].strip() + " "
        return lefttext + "\n", righttext + "\n"

def single_column_text(line_level_representation):
    sorted_line_representations = []
    for line in line_level_representation:
        sorted_line_representations.append(sort_x_axis(line))
    
    overall_text = ""
    for line in sorted_line_representations:
        line_text = get_text(line).strip() + "\n"
        overall_text += line_text
    return overall_text
    
    
    
    
def get_anchors(line_level_representation):
    sorted_line_representations = []
    for line in line_level_representation:
        sorted_line_representations.append(sort_x_axis(line))
 
    # now, we have sorted the lines based on their x-coordinates. 
    # we need to figure out if there is a pattern/block of anchors. 
    right_side_xs = []
    mid_points = []
    for line in sorted_line_representations:
        # first, get the mid-point of the top-rights 
        top_right_list = [word['top-right-x'] for word in line] # for right aligment.. 
        right_side_xs.append(top_right_list)
        
        x_mid_point_rough = (line[0]['top-left-x'] + line[-1]['top-right-x'])/2
        mid_points.append(x_mid_point_rough)
                
    search_point_global = False 
    search_point_global_value = 0
    
    general_text = []
    left_column_text = []
    right_column_text = []
        
    for i in range(len(right_side_xs)):
        cur_line = right_side_xs[i]
        
        try:
            next_line = right_side_xs[i + 1]
        except IndexError:
            # print("last line")
            left, right = get_text(sorted_line_representations[i],search_point_global_value)
            left_column_text.append((left, i))
            right_column_text.append((right, i))
            break
        
        potential_candidates = []
        
        if abs(mid_points[i] - mid_points[i+1]) < 50 or search_point_global:
            if not search_point_global:
                search_point = (mid_points[i] + mid_points[i+1])/2
            else:
                search_point = search_point_global_value
            # look for coordinates that are in their range +-50
            # print(search_point)
            found = False
            for x1 in cur_line:
                if (not search_point_global and x1 < search_point + 100 and x1 > search_point - 100) or (search_point_global and x1 < search_point + 30 and x1 > search_point - 30) :
                    for x2 in next_line:
                        if x2 < x1 + 30 and x2 > x1 - 30:
                            potential_candidates.append((x1,x2))
                            search_point_global = True 
                            search_point_global_value = min(x1, x2)
                            
                            # we found a candidate
                            left, right = get_text(sorted_line_representations[i],search_point_global_value)
                            left_column_text.append((left, i))
                            right_column_text.append((right, i))                            
                            found = True 
                            break 
                    if found:
                        break
            
            # if potential_candidates = 0, then, we can see if there's a different anchor.. or if there is an image.
            if not found and search_point_global:
                left, right = get_text(sorted_line_representations[i],search_point_global_value)
                left_column_text.append((left, i))
                right_column_text.append((right, i))                
                 
        else:
            general_text.append((get_text(sorted_line_representations[i]),i))
            
        # print(cur_line, get_text(sorted_line_representations[i]).strip())
        # print(next_line, get_text(sorted_line_representations[i + 1]).strip())
        
        # print(potential_candidates) # across lines
    general_text = "".join([x[0] for x in general_text])
    left_text = "".join([x[0] for x in left_column_text])
    right_text = "".join([x[0] for x in right_column_text])
    
    overall_text = general_text + left_text + right_text
    # print("General Text: ", general_text)
    # print("Left Text: ", left_text)
    # print("Right Text: ", right_text)
    return overall_text
    
    
# tested: Boas_1909_KwakiutlofVnIsldVol2-wpics
DATA_PATH = "data/jsons/BOAS_1948_dictionary/"
OUT_PATH = "data/text/BOAS_1948_dictionary/"

json_filenames = sorted([x for x in os.listdir(DATA_PATH) if ".json" in x])

for json_filename in json_filenames:
    print(json_filename)
    with open(DATA_PATH + json_filename, "r") as file_pointer:
        loaded_file = json.load(file_pointer)
        
    # look at the bounding boxes, one line at a time. 
    # then, we will decide whether and where we want to split it.
    
    word_level_representation = get_words_from_json(loaded_file)
    line_level_representation = get_line(word_level_representation)
    # overall_text = get_anchors(line_level_representation)
    overall_text = single_column_text(line_level_representation)
    
    with open(OUT_PATH + json_filename.split(".")[0] + ".txt", "w") as write_p:
        write_p.writelines(overall_text)
    
    # if there is a huge gap between words, then they are definitely different columns 
    # and indicate the start of a story.. 
    
    # otherwise, except for the first line, keep splitting it?
    
    # the first line is probably just the title.
    # there might be some full-lines, before the story starts. 

    
    # figure out the margin
    # (either with title, the story will start
    # or, it will just be so from the top of the page, if it is a continutation. 
    
    # SAVE THIS TEXT TO FILE

    
