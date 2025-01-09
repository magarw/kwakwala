from nltk.tokenize import word_tokenize
import fasttext
from huggingface_hub import hf_hub_download
from string import punctuation, printable
import os

if __name__ == "__main__":
    model_path = "../../data/langid/models/exp2.bin"
    model = fasttext.load_model(model_path)

    # BOOKPATH = "data/text/Boas_1902_JesupVolV_AMNH_pt1"
    # BOOKPATH =  "data/text/Boas_1902_JesupVolV_AMNH_Pt02"
    # BOOKPATH = "data/text/Boas_1902_JesupVolV_AMNH_Pt03"
    # BOOKPATH = "data/text/Boas_1906_JesupVolX_AMNH"
    # BOOKPATH = "data/text/Boas_1909_KwakiutlofVnIsldVol2"
    
    # The books below contain mixed Kwak'wala-English text, and need word-level langID
    BOOKPATH = "data/text/BOAS_1948_dictionary"
    # BOOKPATH = "data/text/Boas_1931_NotesKwaVocabIJAL"
    # BOOKPATH = "data/text/Boas_1934_GeographNamesKwakiutl_Entire"

    folder = f"../../{BOOKPATH}/src/"
    output_folder = f"../../{BOOKPATH}/filt/"
    output_folder_tempmask = f"../../{BOOKPATH}/tempmask/"
    
    files = [x for x in os.listdir(folder) if '.txt' == x[-4:]]
    
    custom_mask_tokens = ['|', '(', ')', '-', "“", "'", "\"", '[', ']', ',', '”'] # add ”
    allowed_masks_char_level = ['|', '(', ')', '.', '-', '—']
    
    for filename in files:
        print(filename)
    
        # Given a text file with n sentences (s)
        with open(folder + filename, "r") as f:
            sentences = f.readlines()
            
            mask_indices = []
            masked_data = []

            for sentence in sentences:
                
                # Tokenize the string 
                sentence = sentence.strip()
                tokens = sentence.split(" ") # tokenize based on space? or character?
                
                numerical_indices = []
                tokens_masked = tokens
                # We want to identify the spans that have numbers 
                for i in range(len(tokens)):
                    if tokens[i].isnumeric() or tokens[i] in custom_mask_tokens or (all([x.isnumeric() or x in allowed_masks_char_level for x in tokens[i]])):
                        numerical_indices.append(i)
                        tokens_masked[i] = ""

                
                # sentence-level score
                sent_level_mask = False
                # masked_sentence = " ".join([tokens[i] for i in range(len(tokens)) if i not in numerical_indices])
                # sent_level_prediction = model.predict(sentence)
                # if sent_level_prediction[0][0] == '__label__eng_Latn'  and sent_level_prediction[1][0] > 0.85:
                #     english_indices = list(range(len(tokens)))
                #     sent_level_mask = True 
                        
                # Currently, we can filter out sentences that are entirely English 
                # But, we can also do a more intelligent span-level detection
                if not sent_level_mask:
                    english_indices = []
                    # We want to identify the spans that have English text 
                    for i in range(len(tokens_masked)):
                        if i not in english_indices:
                            prediction = model.predict(tokens_masked[i])
                            printable_i = all(t in printable for t in tokens_masked[i] )
                            if tokens_masked[i] not in punctuation and printable_i and i not in numerical_indices and prediction[0][0] == '__label__eng_Latn'  and prediction[1][0] > 0.50:
                                english_indices.append(i)
                                
                                # For such an index if it works out, then, we want to do a search around it 
                                # because maybe the word before or after it would only count as English in context?                        
                                
                                # Forward Search 
                                if i < len(tokens_masked) - 1:
                                    for j in range(i +1, len(tokens_masked)):
                                        span = " ".join(tokens_masked[i:j+1])
                                        prediction = model.predict(span)
                                        printable_j = all(t in printable for t in tokens[j] )
                                        if tokens_masked[j] not in punctuation and printable_j and j not in numerical_indices and prediction[0][0] == '__label__eng_Latn'  and prediction[1][0] > 0.50:
                                            english_indices.append(j)
                                        else:
                                            break
                                            
                                # Backward Search 
                                if i > 0:
                                    for j in range(i-1, -1,-1):
                                        span = " ".join(tokens_masked[j:i+1])
                                        prediction = model.predict(span)
                                        printable_j = all(t in printable for t in tokens_masked[j] )
                                        if tokens_masked[j] not in punctuation and printable_j and j not in numerical_indices and prediction[0][0] == '__label__eng_Latn'  and prediction[1][0] > 0.50:
                                            english_indices.append(j)
                                        else:
                                            break
                        
                    # Remove the entire line if more than half of the tokens are English
                    # if len(english_indices) > (len(tokens) - len(numerical_indices))/2 :
                    #     english_indices = list(range(len(tokens))) # Removes spans that occur later in the string
                    
                sentence_mask_indices =   list(set(numerical_indices   + english_indices))
                sentence_mask_indices = sorted(sentence_mask_indices)
                mask_indices.append(sentence_mask_indices)
                
                # For visual inspection only
                hidden_tokens = ""
                for i in range(len(tokens)):
                    if i in sentence_mask_indices:
                        hidden_tokens += tokens[i] + " "
                print(hidden_tokens)
                
                # We want to create a masked sentence (with english and numbers hidden)
                masked_sentence = ""
                for i in range(len(tokens)):
                    if i not in sentence_mask_indices:
                        masked_sentence += tokens[i] + " "
                masked_sentence = masked_sentence.strip()
                masked_data.append(masked_sentence)
            
            # We want to save the indices of the masked elements so we can insert them back
            output_filename = filename.split(".txt")[0] + ".tempmask"
            with open(output_folder_tempmask + output_filename, "w") as output_mask:
                for m in mask_indices:
                    out_string = ""
                    for n in m:
                        out_string += str(n) + " "
                    output_mask.write(out_string + "\n")
             
            # We want to identify the non-English-non-numeric span and send it for correction 
            output_filename = filename.split(".txt")[0] + "_masked.txt"
            with open(output_folder + output_filename, "w") as output_mask:
                for out_string in masked_data:
                    output_mask.write(out_string + "\n")
            
            