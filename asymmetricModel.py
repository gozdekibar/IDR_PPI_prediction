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

	if not list(dict.fromkeys(known_nodes)):
		return("please use unified model")

		
		
	#sort pairs based on the known node
	key_test_updated=[]
	for item in list(dict.fromkeys(known_nodes)):
		repo=tuple(test_interactions)
		test_keys=[x for x in repo if x[1] == item or x[0] == item]
		for i in test_keys:
			if i[0]==item:
				keys=i
			else:
				keys=(i[1],i[0])
			key_test_updated.append(keys)   

	#make the prediction
	result=preprocessing_features_single(df_ProtR,'minus',key_test_updated)
	result=result[df_ProtR.columns]
	preds = asymmetric_model.predict(result)

	dictionary_pred = dict(zip(key_test_updated, preds))
	


	with open(output, "w", newline="") as f:
		writer = csv.writer(f, delimiter='\t' ,lineterminator='\n')
		for i in dictionary_pred.keys():
			writer.writerow([i[0], i[1],dictionary_pred[i]])

if __name__ == "__main__":
    exit(main())
