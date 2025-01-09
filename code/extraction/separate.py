from huggingface_hub import hf_hub_download
import fasttext
# from g2p import make_g2p
# transducer = make_g2p('kwk-boas', 'kwk-umista')
import os 
model_path = hf_hub_download(repo_id="facebook/fasttext-language-identification", filename="model.bin")
model = fasttext.load_model(model_path)
    

# We have the post-corrected text now. It contains some stray English words
# in the lines up top. 

# First step, is to isolate the English and the Kwak'wala. 
    # This should probably go in the masking stage itself. But it may not always be possible.. 
    

BOOKNAME = "Boas_1909_KwakiutlofVnIsldVol2"
FILENUMS =sorted([ x.split('_')[0] for x in os.listdir(f"../../data/text/{BOOKNAME}/filt/") if '.txt.out' in x])

for NUM in FILENUMS: 
    print(f"NUM: {NUM}")

    FILT_PATH = f"../../data/text/{BOOKNAME}/filt/"
    SRC_PATH = f"../../data/text/{BOOKNAME}/src/"
    MASK_PATH = f"../../data/text/{BOOKNAME}/tempmask/"
    MERGED_PATH = f"../../data/text/{BOOKNAME}/output/"

    SRC_FILENAME = f"{NUM}.txt"
    MASK_FILENAME = f"{NUM}.tempmask"
    FILT_FILENAME = f"{NUM}_masked.txt"
    POSTCORRECTED_FILENAME = f"{NUM}_masked.txt.out"
    
    # I need to read the filt file
    kwakwala_filtered_text = [] 
    # This list should have tuples of the form (index, boas_postcorrected, umista_postcorrected)
    with open(FILT_PATH + POSTCORRECTED_FILENAME, "r") as filt_fp:    
        read_filt_data = [x.strip() for x in filt_fp.readlines()]
         
        len_read_filt_data = len(read_filt_data)
        if len_read_filt_data == 0:
            print(f"Length 0, File {NUM}.txt")
            continue # next iteration
        
        first_line =  len_read_filt_data- 1
        second_line = len_read_filt_data - 1
        for rline in range(len(read_filt_data) - 1, -1, -1):
            sentence = read_filt_data[rline].strip()
            sentence_tokens = sentence.split(" ")
            
            
            prediction = model.predict(sentence)
            # print(prediction[0][0], sentence)
            
            line_length = len(sentence_tokens)   
            if line_length >= 3:
                second_line = rline
                if  first_line - second_line <= 3 :
                    if (prediction[0][0] != "__label__eng_Latn"):
                        first_line = second_line
              
        # Create a Kwak'wala only text filter. We need to transliterate this only                   
        for line in range(first_line, len(read_filt_data)):
            input_boas = read_filt_data[line]
            # output_umista = transducer(input_boas).output_string
            output_umista = ""
            kwakwala_filtered_text.append((line, input_boas,output_umista))

        # MASK INSERTION (after first_line) IN BOTH ORTHOGRAPHIES        
        # get the indices and the actual tokens out from Source and Mask files 
        with open(MASK_PATH + MASK_FILENAME, "r") as fp_mask:
            masks = [sorted(list(set(x.strip().split(" ")))) for x in fp_mask.readlines()]
        with open(SRC_PATH + SRC_FILENAME, "r") as fp_src:
            src_texts = [x.strip().split(" ") for x in fp_src.readlines()]
         
        # read the current temporary inputs (uncorrected)
        temp_in_f_name = FILT_PATH + FILT_FILENAME
        with open(temp_in_f_name, "r") as fp:
            temp_texts_input = [x.strip().split(" ") for x in fp.readlines()]
        
        # For lines from 'first_line' to end, we want to reinsert the masks
        mask_tokens = [] # this will contain the masked tokens for each line starting at 'first_line'
        for loc in range(first_line, len(masks)):
            sentence = src_texts[loc]  # this is the source sentence
            mask_sentence = masks[loc] # this contains mask indices
            mask_sentence_with_ix = []
            for mask_ix in mask_sentence:
                if mask_ix != '':
                    mask_ix = int(mask_ix)
                    mask_sentence_with_ix.append((mask_ix, sentence[mask_ix]))
            mask_tokens.append(mask_sentence_with_ix)
            
        # insert back the indices in the appropriate locations
        # what we could do is create a new list with the length of both current_output + mask.. then, we can fill it in
        final_texts_boas = []
        # final_texts_umista = []
                
        for temp_sentence_ix in range(0, len(kwakwala_filtered_text)): # starting at first_line
            
            temp_sentence_boas = kwakwala_filtered_text[temp_sentence_ix][1].strip().split(" ")
            # temp_sentence_umista = kwakwala_filtered_text[temp_sentence_ix][2].strip().split(" ")
            # print("Temp Sentence Boas", temp_sentence_boas)
            # print("Temp Sentence Umista", temp_sentence_umista)
            
            temp_input_sentence = temp_texts_input[temp_sentence_ix + first_line] # offset by first-line
            # print("Temp Input Sentence",temp_input_sentence)
            
            temp_mask = mask_tokens[temp_sentence_ix] 
            # print("Temp Mask",temp_mask)
            
            temp_output_length = len(temp_input_sentence) + len(temp_mask)
            # print("Temp Output Length",temp_output_length)
            
            final_text_boas = ['' for _ in range(temp_output_length)]
            # final_text_umista = ['' for _ in range(temp_output_length)]
            
            # Insert the masks back in the right location
            if len(temp_mask) > 0:
                for masked in temp_mask:
                    final_text_boas[masked[0]] = masked[1]
                    # final_text_umista[masked[0]] = masked[1]
        
            # fill in the empty spots with our text..
            pointer = 0
            for ix in range(len(final_text_boas)):
                if final_text_boas[ix] == '' and pointer < len(temp_sentence_boas):
                    final_text_boas[ix] = temp_sentence_boas[pointer]
                    pointer += 1
                                
            # pointer = 0
            # for ix in range(len(final_text_umista)):
                # if final_text_umista[ix] == '' and pointer < len(temp_sentence_umista):
                    # final_text_umista[ix] = temp_sentence_umista[pointer]
                    # pointer += 1
            
            merged_boas = " ".join(final_text_boas)
            # merged_umista = " ".join(final_text_umista)
                
            final_texts_boas.append( merged_boas.strip() + "\n")
            # final_texts_umista.append(merged_umista.strip() + "\n")
            
            # print(f"Boas-Masked: {kwakwala_filtered_text[temp_sentence_ix][1]}")
            # print(f"Boas-Unmasked: {final_texts_boas[temp_sentence_ix]}")
            
            # print(f"Umista-Masked: {kwakwala_filtered_text[temp_sentence_ix][2]}")
            # print(f"Umista-Unmasked: {final_texts_umista[temp_sentence_ix]}")
            
        # Now, I have the Umista and the Boas orthographies with Eng/line numbers mixed back in for their lines
        # For pure English (uncorrected text), we will simply load it from the source 
        
        final_texts_english = []
        for line_ix in range(0, first_line):
            final_texts_english.append(" ".join(src_texts[line_ix]).strip() + "\n")


        final_merged_string = ""
        # delimiter = "\n\n---------------\n\n"
        # Final printing
        for i in range(len(final_texts_english)):
            final_merged_string += final_texts_english[i] 
        # final_merged_string += "\\newpage "
        final_merged_string += "\n"
        # 
        # print("ENGLISH")
        # print(final_merged_string)
        
        for i in range(len(final_texts_boas)):
            final_merged_string += final_texts_boas[i]
        final_merged_string += "\n"
        
        # for i in range(len(final_texts_umista)):
            # final_merged_string += final_texts_umista[i]
            
        # final_merged_string += "\\newpage "
        
        with open(f"{MERGED_PATH}/{NUM}.txt", "w") as fp_merge:
            fp_merge.write(final_merged_string)
        
        