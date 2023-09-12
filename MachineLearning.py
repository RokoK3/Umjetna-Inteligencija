import csv
import sys
from math import log2

def calculate_entropy(data):
    labels = [row[-1] for row in data]  # uzmi labelu, zadnju stvar iz retka
    total_count = len(labels)  # ukupan broj

    label_counts = {}  
    for label in labels:  #za svaku labelu zapisi kolko koje ima
        if label not in label_counts:  
            label_counts[label] = 0 
        label_counts[label] += 1  

    entropy = 0  
    for count in label_counts.values():
        probability = count / total_count  
        entropy -= probability * log2(probability) 
    return entropy  

def IG(data, feature_index):
    total_entropy = calculate_entropy(data) #izracunaj ukupnu entropiju
    values = [row[feature_index] for row in data] #uzmi sve vrijednosti neke znacajke
    different_values = {} #tu se cuvaju sve te vrijednosti
    for value in values:
        if value not in different_values: #ako je prvi put susrecemo postavi na 1
            different_values[value] = 1
        else:
            different_values[value] += 1 #inace povecaj za 1
    total_count = len(values) #ukupan broj vrijednosti
    
    following_entropies = 0 #sljedeca entropija
    for value, value_count in different_values.items(): #za svaku vrijednost znacajke i njen broj
        data_for_specific_value = []
        for row in data:
            if row[feature_index] == value:
                data_for_specific_value.append(row) #uzmi sve retke iz D u kojima se nalazi ta vrijednost znacajke
        one_feature_entropy = calculate_entropy(data_for_specific_value) #izracunaj njenu entropiju
        following_entropies += (value_count / total_count) * one_feature_entropy #za sve vrijednosti znacajke pozbroji entropije
    
    return total_entropy - following_entropies #vrati ukupnu - za znacajku

def most_frequent_label(data):
    labels = [row[-1] for row in data]
    label_counts = {}
    for label in labels:
        if label not in label_counts:
            label_counts[label] = 0
        label_counts[label] += 1

    if len(set(label_counts.values())) == 1:
        sorted_labels = sorted(label_counts.keys()) #ak su sve iste, tj prisutna je samo 1 labela
        return sorted_labels[0]

    max_count = max(label_counts.values()) #nadi najcescu
    for label, count in label_counts.items():
        if count == max_count: #nadi tu koja je najcesca
            return label

def print_tree(tree, path="", depth=0):
    if 'label' in tree: #dosli smo do lista -> ispisi ga
        path = path.strip()
        print(path + " " + tree['label'])
    else: #inace idemo u podstablo
        for key in tree:
            new_path = path + " " + str(depth+1) + ":" + key
            print_tree(tree[key], new_path, depth+1)

def id3(D, Dparent, X, y, tree, curr_depth=0, max_depth=float('inf')):
    if D: #ak ima jos redaka
        most_frequent = most_frequent_label(D) #uzmi najcescu labelu
    else:
        most_frequent = most_frequent_label(Dparent) #inace uzmi najcescu labelu vise razine

    if not D or curr_depth >= max_depth: #ak smo obisli sve ili dosli do max dubine
        tree['label'] = most_frequent #zabiljezi labelu 
        return

    labels = [row[y] for row in D] #skupi sve labele
    if len(set(labels)) == 1: #ako imamo samo jednu
        tree['label'] = labels[0] #zapisi
        return

    if not X: #ak nema vise znacajki 
        tree['label'] = most_frequent #zabiljezi najznacjniju labelu
        return

    gains = [] 
    for feature in X: #za svaku znacajku pogledaj IG
        feature_gain = IG(D, feature)
        gains.append(feature_gain)
    max_gain = max(gains) #uzmi najveci IG

    max_gain_index = gains.index(max_gain)

    best_feature_index = X[max_gain_index] #uzmi najbolju znacajku

    unique_values = set(row[best_feature_index] for row in D) # jedinstvene vrijednosti te znacajke

    X.remove(best_feature_index)

    for value in unique_values: 
        Dv = [row for row in D if row[best_feature_index] == value]#uzmi samo retke u kojima se pojavljuju vrijednosti te znacajke
        tree[header[best_feature_index] + "=" + str(value)] = {} #stvori novi key oblika znacajka=vrijednost
        id3(Dv, D, list(X), y, tree[header[best_feature_index] + "=" + str(value)], curr_depth + 1, max_depth) #rekurzivno pozovi id3 za podstablo

def predict(tree, current_row, header, data):
    for key in tree:
        if key == 'label': #ako smo dosli do lista
            return tree[key] #predvidamo vrijednost tog lista
        if '=' in key: 
            feature, value = key.split('=') #podijeli kljuc na znacajku i vrijednost
            feature_index = header.index(feature) #nadi index te znacajke
            if str(current_row[feature_index]) == value: #ako se vrijednosti podudaraju
                return predict(tree[key], current_row, header, data) #nastavi tim podstablom dalje
    return most_frequent_label(data) #inace vrati najcescu labelu

def get_predictions(tree, data, header):
    return [predict(tree, row, header, data) for row in data]

def get_accuracy(predictions, data):
    correct_predictions = 0
    for i in range(len(data)):

        correct_label = data[i][-1] # tocna vrijednost
        predicted_label = predictions[i]
        if correct_label == predicted_label: #ak je predikcija dobra povecaj za 1
            correct_predictions += 1
    return correct_predictions / len(data) # vrati tocan broj predikcija / ukupan broj redaka

def get_confusion_matrix(predictions, data):
    label_set = set()
    for row in data:
        label_set.add(row[-1]) # u set labela dodaj sve labele
    for pred in predictions:
        label_set.add(pred) # dodaj i sve predikcije
    labels = sorted(label_set)
    
    confusion_matrix = {}
    for label1 in labels:
        confusion_matrix[label1] = {} #napravi podmapu za svaku labelu
        for label2 in labels:
            confusion_matrix[label1][label2] = 0 #dict unutar dicta npr.  'sunny': {'sunny': 0, 'stormy': 0, 'cloudy': 0}

    for i in range(len(data)):
        correct_label = data[i][-1] # zadnja stvar u retku
        predicted_label = predictions[i] # predikcija
        confusion_matrix[correct_label][predicted_label] += 1 #povecaj vrijednost za 1 

    return confusion_matrix

train_file = sys.argv[1]
test_file = sys.argv[2]
max_depth = float('inf') if len(sys.argv) == 3 else int(sys.argv[3])
with open(train_file, 'r') as file:
    reader = csv.reader(file)
    header = next(reader) # lista svih znacajki
    rows = list(reader) # lista listi svih redaka
tree = {}
id3(rows, rows, list(range(len(header) - 1)), len(header) - 1, tree, max_depth=max_depth) #posalji datu, indexe svih mogucih znacajki, index 
print("[BRANCHES]:")
print_tree(tree)

with open(test_file, 'r') as file:
    reader = csv.reader(file)
    header = next(reader) # lista svih znacajki
    rows = list(reader) # lista listi svih redaka

predictions = get_predictions(tree, rows, header)
accuracy = get_accuracy(predictions, rows)
confusion_matrix = get_confusion_matrix(predictions, rows)

print("[PREDICTIONS]:", " ".join(predictions))
print("[ACCURACY]: {:.5f}".format(accuracy))

print("[CONFUSION_MATRIX]:")
for label in sorted(confusion_matrix.keys()):# za svaki kljuc
    print(" ".join(str(confusion_matrix[label][label2]) for label2 in sorted(confusion_matrix[label].keys())))#uzmi sve iz podmape, zatim uzmi sve iz confusion matrixa i odijeli sa " "