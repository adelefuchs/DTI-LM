import numpy as np 
import pandas as pd
import sys
np.random.seed(42)


def process_data(config):
    root_path = config['root_path']
    data_path = config['data_path'] 
    #data_name = config['data_name'].split(' ')
    DTI_dict = {}
    for i in range(10):
        data_name = []
        data_name.append('train_fold_'+str(i+1)+'.csv')
        data_name.append('test_fold_'+str(i+1)+'.csv')
        df_drug, df_proseq, DTI = helper_function(root_path,data_path,data_name)
        DTI_dict[i] = DTI
    return df_drug, df_proseq, DTI_dict
    
def helper_function(root_path,data_path,data_name):
    #root_path = config['root_path']
    #data_path = config['data_path'] 
    #data_name = config['data_name'].split(' ')
 
    train_data = pd.read_csv(root_path+data_path+data_name[0])
    test_data = pd.read_csv(root_path+data_path+data_name[1])
    
    df_drug = pd.read_csv(root_path+'comp_struc.csv')
    df_proseq = pd.read_csv(root_path+'pro_seq.csv')

    # check how many df_proseq sequences are longer than 700
    length = df_proseq['Sequence'].apply(lambda x: len(x))
    df_proseq = df_proseq[length<700]

    length = df_drug['smiles'].apply(lambda x: len(x))
    df_drug = df_drug[length<510]
    
    df_drug = df_drug.set_index(df_drug['head'].values)
    df_proseq = df_proseq.set_index(df_proseq.pro_id.values)
    
    df_drug = df_drug.drop(columns=['head','smiles'])
    df_proseq = df_proseq.drop(columns=['pro_id'])

    # rename the columns 
    #df_drug = df_drug.rename(columns={'smiles':'SMILES'})
    df_proseq = df_proseq.rename(columns={'Sequence':'SEQ'})

    # add indicator column to show train(1),val(2), test(3)
    train_data['indicator'] = 1
    test_data['indicator'] = 3
    #flip random 15% of the train data indicator to 0
    train_data['indicator'] = np.where(np.random.rand(len(train_data)) < 0.15, 2, train_data['indicator'])
    #concatenate the train and test data
    DTI = pd.concat([train_data,test_data],axis=0)
    #keep few columns from DTI
    DTI = DTI[['head', 'tail', 'label', 'indicator']]
    #DTI = DTI.drop(columns=['relation','pred'])
    DTI = DTI.rename(columns={'head':'Drug_ID','tail':'Prot_ID'})

    # remove some rows from DTI as those proteins were remove for being >700
    DTI = DTI[DTI['Prot_ID'].isin(df_proseq.index)]    
    DTI = DTI[DTI['Drug_ID'].isin(df_drug.index)]
    return df_drug, df_proseq, DTI