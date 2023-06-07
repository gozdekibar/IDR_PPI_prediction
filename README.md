
# IDR_PPI_prediction

Prediction of protein-protein interactions using sequences of intrinsically disordered regions

## Models

![Screenshot_2022-12-09_15-20-47](https://user-images.githubusercontent.com/39767530/206725968-bd1459f8-35c3-4309-a60a-a285c1bc539b.png)

We provide:

#### 1. Asymmetric model

This prediction model is designed to analyze protein pairs that share a common protein within our model as described in the paper. If your protein pairs do not have a common protein in our model, the model will not produce a valid output

#### 2. Unified model

Depending on the pair type, this model will utilize either a symmetric or asymmetric model. If you're uncertain about which model to employ for testing the interactions, you can use this model. 

#### 3. IDR-Based Protein Target Prediction Model
This model is designed to identify potential interaction partners for a given protein. Unlike other prediction models that require pairs of proteins as input, this model only requires the user to input a single protein of interest. The model analyzes the intrinsically disordered regions (IDRs) of the provided protein and uses this information to generate a list of potential interaction partners.


## Installation

1. Dependency

- R
- R libraries: protR

- python 3.9
- python libraries: sklearn, matplotlib, pickle, pandas, csv, sys, click

You can create the enviroment using enviroment.yml file 



2. Clone this repository and cd into it.

        git clone https://github.com/gozdekibar/IDR_PPI_prediction.git
        cd ./IDR_PPI_prediction

 ## Example Usage - Asymmetric Model

Here is the example of the prediction of the interactions of retinoblastoma protein as shown in the paper using asymmetric model

### Step 1: Preprocessing

Before running the code, you will need to generate the input features matrix from IDR sequences of the input proteins by running the following  R code. 

- Input: IDR sequences as a fasta file. IDR sequences should be longer than 15 amino acids. (example input: test_input_RB_IDRs.fa in sequences folder)

Run:

    Rscript ./R/extractFeatures_protR.R ./sequences/test_input_RB_IDRs.fa ./features/output_RB1_protR.txt

This command will take the input fasta file located at ./sequences/test_input_RB_IDRs.fa and preprocess it for use with our model. The preprocessed data will be output to a file located at ./features/output_RB1_protR.txt.


### Step 2: Running the Asymmetric Model


Once the input feature matrix  has been generated, you can run the asymmetric model using the following command:

- --input : features calculated from the preprocessing step

- --pairs : Candidate pairs in tab separated format. Protein names should be Uniprot IDs.

- --output : output file path for the predictions

Run:

    python3 asymmetricModel.py --input ./features/output_RB1_protR.txt --pairs ./exampleDataRB1/RB_test_interactions.txt --output ./exampleDataRB1/RB1_predictions_out.txt

This command will use the asymmetric model to test the interactions for the provided protein pairs. The predicted interactions will be output to a file located at exampleDataRB1/RB1_predictions_out.txt



 ## Example Usage - Unified Model
 
This command will use our unified model to test the interactions

- --input : features calculated from the preprocessing step

- --pairs : Candidate pairs in tab separated format. Protein names should be Uniprot IDs.

- --output : output file path for the predictions 
 
 Run:

    python3 unifiedModel.py --input ./features/output_RB1_protR.txt --pairs ./exampleDataRB1/RB_test_interactions_unified.txt --output ./exampleDataRB1/RB1_predictions_unified_out.txt



 ## Example Usage - Target Prediction Model
 
This command will use our target prediction model to test the interaction partners for the input protein. 
 
- --input : features calculated from the preprocessing step including the input protein

- --target: Uniprot IDs of the input protein

- --output : output file path for the predictions
 
 Run:
    
    python3 targetModel.py --input ./features/output_RB1_protR.txt --target ./exampleDataRB1/target_file.txt --output ./exampleDataRB1/RB1_predictions_target_out.txt
