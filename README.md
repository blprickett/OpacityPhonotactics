# OpacityPhonotactics
A vanilla online MaxEnt learner, with data representing the surface forms created by bleeding, feeding, counterbleeding, and counterfeeding phonological interactions. The learner is implemented in "train_HW.py" and uses whatever constraints are given to it in the "tableau" files along with the training/testing data from "Opacity_TD.csv"

Constraints were induced training the Hayes and Wilson (2008) learner on the same training data, which can be downloaded [here](https://linguistics.ucla.edu/people/hayes/Phonotactics/) (note that their learner requires the data to be in a different format). The output files from that model for each language are given in the "Outputs" directories, and these files can be converted to the "tableau" files that my learner requires using "HW2Tableaux.py". To view the constraints that their model created and the features I gave it as input, see "Constraints and Features for Surface Phonotactic Model.pdf".

My learner creates a single file as output, which will be titled "Opacity_output.csv". To change the model's hyperparameters, see the top of the "train_HW.py" script.

### Reference
Hayes, B., & Wilson, C. (2008). A maximum entropy model of phonotactics and phonotactic learning. *Linguistic inquiry, 39(3)*, 379-440.
