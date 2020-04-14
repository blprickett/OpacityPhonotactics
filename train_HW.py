import numpy as np
import re
from random import shuffle
import os

######USER SETTINGS#############################
EPOCHS = 100 #How many updates will happen 
ETA = .01 #Learning rate
PATTERN = "Opacity" #This should match your training files
REPS = 10 #Repitions
WD = "" #Working directory, if you want to change that from the current one you're in
INIT_W = 0.0 #either a float or the string "rand"
################################################	 

######FUNCTIONS#################################	  
def get_predicted_probs (weights, viols):
	'''Takes a 1d vector of weights and a 2d vector of violation profiles as
	   input. Also requires a global variable 'v' defining violation profiles
	   for every possible word.
	   
	   Calculates probabilities given the weights and violations.
	   
	   Returns a 1d vector of predicted probabilities.
	  '''
	
	#We use different violation matrices here so that the probs we output
	#match up with whatever ambiguity the model is currently dealing with,
	#but also so that the probability distribution we're defining is over 
	#all strings, including unambiguous ones.
	this_harmony = viols.dot(weights) #Uses local variable "viols"
	all_harmonies = v.dot(weights) #Always uses global variable v

	#Typical MaxEnt stuff:
	this_eharmony = np.exp(this_harmony) #e^H
	all_eharmonies = np.exp(all_harmonies)
	Z = sum(all_eharmonies)
	if Z == 0:
		this_prob = this_eharmony*0.0 #Rounding errors can make Z=0
	else:
		this_prob = this_eharmony/Z
	
	return this_prob
	
																																								 
def grad_descent_update (weights, viols, td_probs, eta=.05):
	'''Takes a 1d vector of weights, a 1d vector of a datum's violations, a 1d vector of
	   training data probabilities, and a learning rate (default=.05)
	   as input.  

	   Output is the vector of new weights.'''
		 
			  
	#Forward pass
	le_probs = get_predicted_probs (weights, viols)
	
	#Backward pass:
	TD = viols.T.dot(td_probs) #Violations present in the training data
	LE = viols.T.dot(le_probs) #Violations expected by the learner
	gradients = (TD - LE)
	updates = gradients * eta
	new_weights = weights + updates

	return new_weights
################################################			   

######PROCESS INPUT FILES########################
grammar_files = [fn for fn in os.listdir(".") if "tableau" in fn]
langs = [fn.split("_")[0] for fn in grammar_files]
lang_object = {l:{
					"data":[],
					"viols":[],
					"probs":[],
					"con_names":[]
				} for l in langs}

for gf, l in zip(grammar_files, langs):
	this_f = open(gf, "r")
	headers = this_f.readline().rstrip().split("\t")
	lang_object[l]["con_names"] = headers[2:]

	for line in this_f.readlines():
		columns = line.rstrip().split("\t")
		datum = columns[0]
		prob = float(columns[1])
		viols = [float(v) for v in columns[2:] if v != ""]
		lang_object[l]["data"].append(datum)
		lang_object[l]["viols"].append(viols)
		lang_object[l]["probs"].append(prob)
	this_f.close()

################################################  
			

######SIMULATIONS###############################
output_file = open(WD+PATTERN+"_output.csv", "w")  
output_file.write("Language,Rep,Epoch,Word,TD_Prob,LE_Prob\n")
for lang in lang_object.keys():
	p = np.array([p for p in lang_object[lang]["probs"]])
	v = np.array([V for V in lang_object[lang]["viols"]])
	ixs = [i for i in range(len(p))]
		
	for rep in range(REPS):
		if INIT_W != "rand":
			w = np.array([INIT_W for c in lang_object[lang]["con_names"]])
		else:
			w = np.array([np.random.uniform() for c in lang_object[lang]["con_names"]])

		#Record the initial state in learning:
		current_probs = get_predicted_probs(w, v)
		for datum_index in ixs:
			output_row = []
			output_row.append(lang)
			output_row.append(str(rep))
			output_row.append(str(0))
			output_row.append(lang_object[lang]["data"][datum_index])
			output_row.append(str(p[datum_index]))
			output_row.append(str(current_probs[datum_index]))
			output_file.write(",".join(output_row)+"\n")

		for epoch in range(1,EPOCHS+1): 
			shuffle(ixs)
			for ix in ixs:
				w = grad_descent_update(
											w, #Current weights
											v[ix], #Datum violations
											p[ix], #Datum TD probability
											ETA #Learning rate
										)
				
			if epoch % 10 == 0:
				#Sometimes my version of python crashes on this print statement...
				#...fixed this with a try-except:
				try:
					print ("Epoch: " + str(epoch), ", Pattern: " + str(lang), ", Rep: " + str(rep))
				except:
					print ("Epoch: " + str(epoch), ", Pattern: " + str(lang), ", Rep: " + str(rep))
					
			#Get our model's current estimation of the data:
			current_probs = get_predicted_probs(w, v)
			
			#Record the info that we care about, depending on TEST_FOR's value
			for datum_index in ixs:
				output_row = []
				output_row.append(lang)
				output_row.append(str(rep))
				output_row.append(str(epoch))
				output_row.append(lang_object[lang]["data"][datum_index])
				output_row.append(str(p[datum_index]))
				output_row.append(str(current_probs[datum_index]))
				output_file.write(",".join(output_row)+"\n")
   
################################################

#####Close files################################
output_file.close() 
