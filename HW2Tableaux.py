import re
import math
import matplotlib.pyplot as plt

feats =	{
			"+syllabic": "(i|I|e|E|a)",
			"-syllabic": "(s|S|k)",
			"+coronal": "(s|S)",
			"+anterior": "(s)",
			"-anterior": "(S)",
			"+dorsal": "(k)",
			"+high": "(i|I)",
			"-high": "(e|E|a)",
			"+back": "(a)",
			"-back": "(i|I|e|E)",
			"+tense": "(e|i)",
			"-tense": "(I|E|a)",
			"+word_boundary": "(#)",
			"-word_boundary": "(i|I|e|E|a|s|S|k)"
		}


def intersect (feat1, feat2="", feat3="", feat4=""):
	feat1 = re.sub("\(|\)", "", feat1).split("|")
	feat2 = re.sub("\(|\)", "", feat2).split("|")
	feat3 = re.sub("\(|\)", "", feat3).split("|")
	feat4 = re.sub("\(|\)", "", feat4).split("|")
	all_feats = [f for f in [feat1, feat2, feat3, feat4] if f[0]!=""]
	
	my_inter = []
	all_segs = feat1+feat2+feat3+feat4
	for seg in all_segs:
		include = True
		for f in all_feats:
			if seg in f:
				continue
			else:
				include = False
				break
		if include and (seg not in my_inter):
			my_inter.append(seg)
	
	if len(my_inter) == 0:
		return "%"
	else:
		return "("+"|".join(my_inter)+")"
	
B_conNames = []
B_conRegexes = []
F_conNames = []
F_conRegexes = []
CB_conNames = []
CB_conRegexes = []
CF_conNames = []
CF_conRegexes = []

B_file = open("Bleeding_Outputs\\grammar.txt")
F_file = open("Feeding_Outputs\\grammar.txt")
CB_file = open("Counterbleeding_Outputs\\grammar.txt")
CF_file = open("Counterfeeding_Outputs\\grammar.txt")

for line in B_file:
	if line == "":
		continue
		
	con, tier, w = line.rstrip().split("\t")
	B_conNames.append(con)
	
	con = re.sub("\*\[|\]$", "", con)
	grams = [[feats[f] for f in g.split(",")] for g in con.split("][")]
	c_regex = "".join([intersect(*g) for g in grams])
	
	B_conRegexes.append(c_regex)

for line in F_file:
	if line == "":
		continue
		
	con, tier, w = line.rstrip().split("\t")
	F_conNames.append(con)
	
	con = re.sub("\*\[|\]$", "", con)
	grams = [[feats[f] for f in g.split(",")] for g in con.split("][")]
	c_regex = "".join([intersect(*g) for g in grams])
	
	F_conRegexes.append(c_regex)	

for line in CB_file:
	if line == "":
		continue
		
	con, tier, w = line.rstrip().split("\t")
	CB_conNames.append(con)
	
	con = re.sub("\*\[|\]$", "", con)
	grams = [[feats[f] for f in g.split(",")] for g in con.split("][")]
	c_regex = "".join([intersect(*g) for g in grams])
	
	CB_conRegexes.append(c_regex)

for line in CF_file:
	if line == "":
		continue
		
	con, tier, w = line.rstrip().split("\t")
	CF_conNames.append(con)
	
	con = re.sub("\*\[|\]$", "", con)
	grams = [[feats[f] for f in g.split(",")] for g in con.split("][")]
	c_regex = "".join([intersect(*g) for g in grams])
	
	CF_conRegexes.append(c_regex)		
	
B_file.close()
F_file.close()
CB_file.close()
CF_file.close()

print("Bleeding", len(B_conRegexes))
print("Feeding", len(F_conRegexes))
print("Counterbleeding", len(CB_conRegexes))
print("Counterfeeding", len(CF_conRegexes))

dataFile = open("Opacity_TD.csv", "r") #File with training and testing data
sigma = []
my_data = {
			"Bleeding":{"train":[], "test":[]},
			"Feeding":{"train":[], "test":[]},
			"Counterbleeding":{"train":[], "test":[]},
			"Counterfeeding":{"train":[], "test":[]}
		  }

for line in dataFile.readlines():
	columns = line.rstrip().split(",")
	lang = columns[0]
	data = columns[1:]
	
	if lang == "Nonce":
		for datum in data:
			if datum == '':
				continue
			else:
				for l in my_data.keys():
					if datum not in my_data[l]["train"]:
						my_data[l]["test"].append(datum)
						sigma += list(datum)
	else:
		for datum in data:
			if datum == '':
				continue
			my_data[lang]["train"].append(datum)
			sigma += list(datum)
dataFile.close()

#Create all possible strings:
sigma = list(set(sigma))
sigma_star = []
for seg1 in sigma:
	for seg2 in sigma:
		for seg3 in sigma:
			sigma_star.append(seg1+seg2+seg3)

#Create the tableax files:
B_tabFile = open("B_tableau.txt", "w")
F_tabFile = open("F_tableau.txt", "w")
CB_tabFile = open("CB_tableau.txt", "w")
CF_tabFile = open("CF_tableau.txt", "w")
file_dict = {"Bleeding":B_tabFile, "Feeding":F_tabFile, "Counterbleeding":CB_tabFile, "Counterfeeding":CF_tabFile}
regex_dict = {"Bleeding":B_conRegexes, "Feeding":F_conRegexes, "Counterbleeding":CB_conRegexes, "Counterfeeding":CF_conRegexes}
cName_dict = {"Bleeding":B_conNames, "Feeding":F_conNames, "Counterbleeding":CB_conNames, "Counterfeeding":CF_conNames}

for lang in file_dict.keys():
	file_dict[lang].write("datum\tprob\t"+"\t".join(cName_dict[lang])+"\n")
	for datum in my_data[lang]["train"]:
		file_dict[lang].write(datum+"\t0.05\t")
		viols = []
		for c in regex_dict[lang]:
			v = str(len(re.findall(c, datum)))
			viols.append(v)
		file_dict[lang].write("\t".join(viols)+"\n")
		
	for datum in sigma_star:
		if datum in my_data[lang]["train"]:
			continue
		file_dict[lang].write(datum+"\t0.0\t")
		viols = []
		for c in regex_dict[lang]:
			v = str(len(re.findall(c, datum)))
			viols.append(v)
		file_dict[lang].write("\t".join(viols)+"\n")

B_tabFile.close()
F_tabFile.close()
CB_tabFile.close()
CF_tabFile.close()












