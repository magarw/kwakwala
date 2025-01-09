def load_file(f_path):
    with open(f_path, mode='r') as fp:
        data_string = "\n".join([x.strip() for x in fp.readlines()])

    return data_string

def cer(predicted_text, transcript):
    import editdistance as ed 
    cer = ed.eval(predicted_text, transcript)/len(transcript)
    return cer 


for OUTFILE_PATH in ['../../gold-data-creation/Boas_1909_KwakiutlofVnIsldVol2/firstpass/60.txt', '../../gold-data-creation/Boas_1909_KwakiutlofVnIsldVol2/zoned/60.txt', '../../gold-data-creation/Boas_1909_KwakiutlofVnIsldVol2/corrected/60.txt']:
    REFFILE_PATH = '../../gold-data-creation/Boas_1909_KwakiutlofVnIsldVol2/gold/60.txt'

    output_string = load_file(OUTFILE_PATH) 
    correct_string = load_file(REFFILE_PATH)
    
    print("CER: ", cer(output_string, correct_string))
    
print("--")


"""
Boas_1902_Jesup_VolV_AMNH_pt1
36.txt:
CER:  0.23
CER:  0.21
CER:  0.19

37.txt: 
CER:  0.63
CER:  0.19
CER:  0.17

Average: 
CER: 0.43
CER: 0.20 (Zoned, not corrected.. so 0.25 is indeed the Structural Error above.)
CER: 0.18

Zoned Error: 0.25 --> 0.02

----
Boas_1909_KwakiutlofVnIsldVol2
59.txt:
CER:  0.16
CER:  0.18
CER:  0.14

60.txt
CER:  0.50
CER:  0.18
CER:  0.17

Average: 
CER: 0.33
CER: 0.18
CER: 0.15

Zoned Error: 0.18 --> 0.03
----

"""