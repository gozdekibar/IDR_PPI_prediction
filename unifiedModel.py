from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import pickle
import pandas as pd
import csv
import sys
import click

@click.command()

@click.option('--input', type=click.Path(exists=True), required=True)
@click.option('--pairs', type=click.Path(exists=True), required=True)
@click.option('--output', type=click.Path(exists=False), required=True)


def main(input, pairs, output):


	#export feature table
	df_ProtR =pd.read_csv(input,sep="\t",header=0,index_col=0)




	#export test pairs
	with open(pairs, newline="") as f:
		reader = csv.reader(f, delimiter='\t' ,lineterminator='\n')
		test_interactions=[]
		for x in reader:
			t = ()
			t = t + (x[0],) + (x[1],)
			test_interactions.append(t)

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

	#find the known nodes
	known_nodes=[] 
	for pair in test_interactions:
		if [x for x in repo if x[1] == pair[0] or x[0] == pair[0]]:
			item=pair[0]
			known_nodes.append(item)
		elif [x for x in repo if x[1] == pair[1] or x[0] == pair[1]]:
			item=pair[1]
			known_nodes.append(item)
		else:
			continue

#if there are asymmetric pairs, sort them
	if list(dict.fromkeys(known_nodes)):
		#sort pairs based on the known node
		key_test_updated=[]
		found_test_keys=[]
		for item in list(dict.fromkeys(known_nodes)):
			repo=tuple(test_interactions)
			test_keys=[x for x in repo if x[1] == item or x[0] == item]
			found_test_keys.append(test_keys)
			for i in test_keys:
				if i[0]==item:
					keys=i
				else:
					keys=(i[1],i[0])
				key_test_updated.append(keys)
       
        #make the prediction for asymmetric model
		result_asymm=preprocessing_features_single(df_ProtR,'minus',key_test_updated)
		result_asymm=result_asymm[df_ProtR.columns]
		preds_asymm = asymmetric_model.predict(result_asymm)
		dictionary_pred_asymm = dict(zip(key_test_updated, preds_asymm))
                
    
            
		flat_list_found = [item for sublist in found_test_keys for item in sublist]
    
		symm_pairs = []
		for item in test_interactions:
			if item not in flat_list_found:
				symm_pairs.append(item)  
				
		if symm_pairs:		

			symm_pairs_2=[]
			for i in symm_pairs:
				t = ()
				t = t + (i[1],) + (i[0],) 
				symm_pairs_2.append(t)
            
            
#if there are no asymmetric pairs
	else:
		symm_pairs=test_interactions    
		symm_pairs_2=[]
		for i in test_interactions:
			t = ()
			t = t + (i[1],) + (i[0],) 
			symm_pairs_2.append(t)    
		dictionary_pred_asymm={}
        
            
   
            
##symm model
	if symm_pairs:
		result_symm=preprocessing_features_single(df_ProtR,'abs_minus',symm_pairs)
		result_symm=result_symm[df_ProtR.columns]
		preds_symm = symmetric_model.predict(result_symm)
		probs_symm = symmetric_model.predict_proba(result_symm)

		result_symm_1=preprocessing_features_single(df_ProtR,'minus',symm_pairs)
		result_symm_1=result_symm_1[df_ProtR.columns]
		preds_symm_1 = asymmetric_model.predict(result_symm_1)
		probs_symm_1 = asymmetric_model.predict_proba(result_symm_1)


		result_symm_2=preprocessing_features_single(df_ProtR,'minus',symm_pairs_2)
		result_symm_2=result_symm_2[df_ProtR.columns]
		preds_symm_2 = asymmetric_model.predict(result_symm_2)
		probs_symm_2 = asymmetric_model.predict_proba(result_symm_2)

	## get the common choice for symmetric pairs


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
		
		dictionary_pred_symm = dict(zip(symm_pairs, newpreds))
		merged_dic={**dictionary_pred_asymm, **dictionary_pred_symm}
		
	else:
		print("please use asymmetric model")       
            

	with open(output, "w", newline="") as f:
		writer = csv.writer(f, delimiter='\t' ,lineterminator='\n')
		for i in merged_dic.keys():
			writer.writerow([i[0], i[1],merged_dic[i]])

if __name__ == "__main__":
    exit(main())
