
import fasttext 
import random 

# create combined training data for relevant languages 
languages = ["english", "kwakwala"]
labels = {
    "english": "eng_Latn",
     "kwakwala": "kwk_Latn"
}
experiment_number = 2

label_added_train = []
label_added_val = []
for lang in languages:
    with open(f"../../data/langid/train/{lang}_train.txt", "r") as in_file:
        label_added_train += [f"__label__{labels[lang]}\t{x}" for x in in_file.readlines()]
    with open(f"../../data/langid/val/{lang}_val.txt", "r") as in_file:
        label_added_val += [f"__label__{labels[lang]}\t{x}" for x in in_file.readlines()]
        
# output a combined version for fasttext 
with open(f"../../data/langid/experiment/exp{experiment_number}.train","w") as out_file:
    random.shuffle(label_added_train)
    out_file.writelines(label_added_train)
with open(f"../../data/langid/experiment/exp{experiment_number}.val","w") as out_file:
    random.shuffle(label_added_val)
    out_file.writelines(label_added_val)
    
# train fastText model 
model = fasttext.train_supervised(input=f"../../data/langid/experiment/exp{experiment_number}.train")
model.save_model(f"../../data/langid/models/exp{experiment_number}.bin")
print(model.test(f"../../data/langid/experiment/exp{experiment_number}.val"))

# Read 0M words
# Number of words:  11585
# Number of labels: 2
# Progress: 100.1% words/sec/thread:  102646 
# lr: -0.000137 avg.loss:  0.244812  
# Progress: 100.0% words/sec/thread:  102519 
# lr:  0.000000 avg.loss:  0.244812 ETA:   0h 0m 0s
# (1254, 0.9984051036682615, 0.9984051036682615)