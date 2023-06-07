from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import pickle
import pandas as pd
import csv
import numpy as np
import sys
import click

@click.command()

@click.option('--input', type=click.Path(exists=True), required=True)
@click.option('--target', type=click.Path(exists=True), required=True)
@click.option('--output', type=click.Path(exists=False), required=True)


def main(input,target, output):


	#export feature table
	df_ProtR_1 =pd.read_csv("./features/protR_IDRs_concenated_15.txt",sep="\t",header=0,index_col=0)
	df_ProtR_2 =pd.read_csv(input,sep="\t",header=0,index_col=0)
	
	result = pd.concat([df_ProtR_1, df_ProtR_2])
	df_ProtR_disorderome=result.drop_duplicates()

	
	repo_disorderome=list(tuple(df_ProtR_disorderome.index.values))

	with open(target,'r') as file:
		target_name = file.read()
		target_name=target_name.strip()
	

			
	try:
		repo_disorderome.remove(target_name)
	except ValueError:
		pass  # do nothing!

	#create all the possible combinations
	test_interactions=[(target_name,i) for i in repo_disorderome]

	#import pre-trained asymmetric model
	asymmetric_model = pickle.load(open('./models/rf_asymmetric_model.sav', 'rb')) 
	symmetric_model = pickle.load(open('./models/rf_symmetric_model.sav', 'rb')) 



	#read the product model pairs
	unpickled_df = pd.read_pickle("./models/product_model_df_asymmetric.pkl")
	repo=tuple(unpickled_df.index.values)

	def preprocessing_features_single(input_feature,operator,given_pairs):
		
		newdict=input_feature.to_dict(orient="index")


		
		dfs=[]
		for pairs in [given_pairs]:
		
				 
					

			if operator == 'minus' :
				features2={}
				for keys in pairs:
					test_dict1=newdict[keys[0]]
					test_dict2=newdict[keys[1]]
					#print(test_dict1)
					#print(test_dict2)
					res = {key: test_dict1[key] - test_dict2.get(key, 0) for key in test_dict2.keys()}   
					features2[keys] = res  

	  
					
			if operator == 'abs_minus' :
				features2={}
				for keys in pairs:
					test_dict1=newdict[keys[0]]
					test_dict2=newdict[keys[1]]
					#print(test_dict1)
					#print(test_dict2)
					res = {key: abs(test_dict2[key] - test_dict1.get(key, 0)) for key in test_dict2.keys()}   
					features2[keys] = res
									

				
			dfObj = pd.DataFrame(features2) 
			dfObj=dfObj.transpose()
			dfs.append(dfObj)

			
	   

			
		return(pd.concat(dfs))

	def most_frequent(List): 
		counter = 0
		num = List[0] 
      
		for i in List: 
			curr_frequency = List.count(i) 
			if(curr_frequency> counter): 
				counter = curr_frequency 
				num = i 
		return num 



	if [x for x in repo if x[1] == target_name or x[0] == target_name]:
		print("asymmetric model")
		result_asymm=preprocessing_features_single(df_ProtR_disorderome,'minus',test_interactions)
		result_symm=result_asymm[df_ProtR_disorderome.columns]
		probs_asymm = asymmetric_model.predict_proba(result_asymm)
		dictionary_pred_asymm = dict(zip(test_interactions, probs_asymm[:, 1]))
		merged_dic=sorted(dictionary_pred_asymm, key=dictionary_pred_asymm.get, reverse=True)[:50]
	else:
		print("symmetric model")
		symm_pairs=test_interactions
		symm_pairs_2=[]
		
		for i in symm_pairs:
			t = ()
			t = t + (i[1],) + (i[0],) 
			symm_pairs_2.append(t) 
			
		##symm model

		result_symm=preprocessing_features_single(df_ProtR_disorderome,'abs_minus',symm_pairs)
		result_symm=result_symm[df_ProtR_disorderome.columns]
		preds_symm = symmetric_model.predict(result_symm)
		probs_symm = symmetric_model.predict_proba(result_symm)

		result_symm_1=preprocessing_features_single(df_ProtR_disorderome,'minus',symm_pairs)
		result_symm_1=result_symm_1[df_ProtR_disorderome.columns]
		preds_symm_1 = asymmetric_model.predict(result_symm_1)
		probs_symm_1 = asymmetric_model.predict_proba(result_symm_1)


		result_symm_2=preprocessing_features_single(df_ProtR_disorderome,'minus',symm_pairs_2)
		result_symm_2=result_symm_2[df_ProtR_disorderome.columns]
		preds_symm_2 = asymmetric_model.predict(result_symm_2)
		probs_symm_2 = asymmetric_model.predict_proba(result_symm_2)
		
		


		newpreds=[]
		new_probs=[]
		for i in range(len(symm_pairs)):

			listx=[preds_symm[i],preds_symm_1[i],preds_symm_2[i]]
			listy=[probs_symm[i],probs_symm_1[i],probs_symm_2[i]]

			common_choice=most_frequent(listx)
			newpreds.append(common_choice)
			indices = [i for i, x in enumerate(listx) if x == common_choice]

			if common_choice==1:
				listt=[probs_symm[i][1],probs_symm_1[i][1],probs_symm_2[i][1]]
				indexofmax=listt.index(max(listt))
				new_probs.append(listy[indexofmax])
			else:
				listt=[probs_symm[i][0],probs_symm_1[i][0],probs_symm_2[i][0]]
				indexofmax=listt.index(max(listt))
				new_probs.append(listy[indexofmax])
				
		lr_probs = np.array(new_probs)[:, 1]        
		dictionary_pred_symm = dict(zip(symm_pairs, lr_probs))
		merged_dic=sorted(dictionary_pred_symm, key=dictionary_pred_symm.get, reverse=True)[:50]   
		
		
		

			

				
		
	with open(output, "w", newline="") as f:
		writer = csv.writer(f, delimiter='\t' ,lineterminator='\n')
		for i in merged_dic:
			writer.writerow([i[0], i[1],])
        

if __name__ == "__main__":
    exit(main())
