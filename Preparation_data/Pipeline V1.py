
# coding: utf-8

# In[34]:


# coding: utf-8

# In[2]:


import xlrd
import numpy as np
from numpy import nan
import operator
import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly
plotly.tools.set_credentials_file(username='eadrien', api_key='KnEjzGXF14YNufp5E9xs')
import plotly.graph_objs as go
import pandas as pd
import calendar


# In[3]:


pd.set_option('display.float_format', lambda x: '%.2f' % x)


# In[4]:


def remove_duplicates(values):
    output = []
    output_index = []
    seen = set()
    i = 0
    for value in values:
        # If value has not been encountered yet,
        # ... add it to both list and set.
        if value not in seen:
            output.append(value)
            output_index.append(i)
            seen.add(value)
        i += 1
    return output_index


# In[5]:


def date_format(data_frame):
    data_transpose = data_frame.transpose()
    data_transpose = data_transpose.iloc[:,1:]
    df_date = pd.DataFrame(data_transpose.iloc[0,:])
    df_time = pd.DataFrame(data_transpose.iloc[1,:])
    for i in range(1,len(df_date)):
        df_date.iloc[i][0] = df_date.iloc[i][0].replace(hour=int(str(df_time.iloc[i])[5:7]), minute=int(str(df_time.iloc[i])[8:10]), second=int(str(df_time.iloc[i])[11:13]))
    df_date_row = df_date.transpose()
    data_transpose = data_transpose.drop([0],axis=0)
    data_transpose = data_transpose.drop([1],axis=0)
    data_transpose = data_transpose.append(df_date_row, ignore_index=False)
    data_transpose = data_transpose.sort_index()
    number_columns_df = len(data_transpose.columns)
    data_transpose.columns = range(number_columns_df)
    data_transpose = data_transpose.reset_index()
    data_transpose = data_transpose.drop("index",axis=1)
    return data_transpose


# In[6]:


def remove_duplicates_in_df(df):
    list_names_columns = df.iloc[:,0]
    list_index_names_columns_not_duplicated = remove_duplicates(list_names_columns)
    df = df.loc[list_index_names_columns_not_duplicated]
    return df


# In[7]:


def no_na_preparation(df):
    df_nona = pd.DataFrame(df)
    df_nona = df_nona.transpose()
    df_nona_t = df_nona.iloc[1:,1:].dropna(axis=1,how="all")
    #fulfill empty values by copying the previous full value in the column
    df_nona_t = df_nona_t.fillna( method='backfill', axis=0)
    #fuflill empty values by copying the next full value in the column
    df_nona_t = df_nona_t.fillna( method='ffill', axis=0)
    df_nona_t = df_nona_t.astype(float)
    return df_nona_t


# In[8]:


def get_new_column_names(df, df2,df_names):
    list_noms_colonnes = []
    list_noms_colonnes_avant = df_names
    for i in range(len(df2.columns.values)):
        list_noms_colonnes.append(list_noms_colonnes_avant[df2.columns.values[i]])
    return list_noms_colonnes


# In[9]:


def format_df(df,df2,data_unités,df_names):
    list_noms_colonnes = get_new_column_names(df,df2,df_names)
    list_adress_units_files = data_unités["Adresse"]
    list_text_units_files = data_unités["Texte"]
    list_units = data_unités["Unité"]
    list_indexes = []
    for i in range(len(list_noms_colonnes )):
        bool = 0
        for j in range(len(list_adress_units_files)):
            if(bool == 1):
                break
            elif(list_noms_colonnes[i] == list_adress_units_files[j]):
                list_indexes.append(j)
                bool = 1
        if(bool == 0):
            list_indexes.append(-1)
    new_list_texte = []
    for i in range(len(list_indexes)):
        new_list_texte.append(data_unités["Texte"].iloc[list_indexes[i]])
    #ew_list_texte.append('Date')
    new_list_units = []
    for i in range(len(list_indexes)):
        new_list_units.append(data_unités["Unité"].iloc[list_indexes[i]])
    #new_list_units.append('Date')

    #ist_noms_colonnes.append('Date')
    df2.loc['Adress'] = list_noms_colonnes
    df2.loc["Texte"] = new_list_texte
    df2.loc["Unité"] = new_list_units
    number_columns_df = len(df2.columns)
    df2.columns = range(number_columns_df)
    return df2


# In[10]:


def check_columns_with_unique_values(df):
    list_indexes = []
    for i in range(len(df.columns)):
        #array = df[names_of_columns[i]].unique()
        array = pd.unique(df.iloc[:,i].values)
        if len(array) == 1 :
            list_indexes.append(i)
    return list_indexes


# In[18]:


def preparation_data(df,data_unités):
    data = date_format(df)
    data = remove_duplicates_in_df(data)
    data_model = data.copy()
    data_not_duplicated = no_na_preparation(data)
    data_final = format_df(data,data_not_duplicated ,data_unités,data.iloc[1:,0])
    data_final_just_data = data_final.iloc[:-3,:-1]
    list_indexes_to_delete = check_columns_with_unique_values(data_final_just_data)
    data_final_just_data_no_duplicated = data_final_just_data.copy()
    data_final_just_data_no_duplicated.drop(columns = data_final_just_data.columns[list_indexes_to_delete],axis=1,inplace=True)
    #list_noms_colonnes = get_new_column_names(data_final,data_final_just_data_no_duplicated,data_final.loc['Adress'])
    #list_noms_colonnes.append('Date')
    copy_data_final_just_data_no_duplicated = data_final_just_data_no_duplicated.copy()
    data_final = format_df(data_final,copy_data_final_just_data_no_duplicated, data_unités,data_final.loc['Adress'])
    list_date = data_model.iloc[0,:]
    data_final_just_data_no_duplicated['Date'] = list_date
    data_final['Date'] =list_date
    return data_final, data_final_just_data_no_duplicated


# In[41]:


def Excel_for_Power_BI(df,df_model):
    list_new_names_columns = []
    df_copy = df.copy()
    for i in range(len(df_copy.columns)):
        list_new_names_columns.append(str(df_model.loc['Adress',i])+' en '+ str(df_model.loc['Unité',i]))
    df_copy.columns = list_new_names_columns
    save_df_in_excel(filename[:-6]+'_PowerBi.xlsx', df)
    return 'Excel for Power BI generated'


def Excel_to_look(df,df_model):
    return 'test coucou'
# In[13]:


def save_df_in_excel(filename, df):
    writer = pd.ExcelWriter(filename)
    df.to_excel(writer,"Sheet") 
    writer.save()


# In[14]:


data = pd.read_excel("13-06_13-07.xlsx",header=None)
data2 = pd.read_excel("13-07_27-09.xlsx",header=None)
data_unités = pd.read_excel('UnitésV6.xlsx')


# In[19]:


data_1, data_1_just_data = preparation_data(data,data_unités)


# In[72]:


def Excel_for_Power_BI(df,df_model,filename):
    list_new_names_columns = []
    df_copy = df.copy()
    for i in df_model.columns:
        list_new_names_columns.append(str(df_model.loc['Texte',i]) + str(df_model.loc['Adress',i])+' en '+ str(df_model.loc['Unité',i]))
    list_new_names_columns[-1] = 'Date'
    temp = list_new_names_columns[0]
    list_new_names_columns[0] = 'Date'
    list_new_names_columns[-1]  = temp
    df_copy = df_copy[list_new_names_columns]
    #df_copy.columns = list_new_names_columns
    save_df_in_excel(filename+'_PowerBi.xlsx',df_copy)
    return 'Excel for Power BI generated'


# In[326]:


def Excel_to_look(df,df_model,filename):
    df_min = df_model.iloc[:-3,:-1].min()
    df_median = df_model.iloc[:-3,:-1].median()
    df_max = df_model.iloc[:-3,:-1].max()
    df_adresse = df_model.loc["Adress"][:-1]
    df_adresse = pd.DataFrame(data=df_adresse)
    #df_adresse.index = df_median.index.values
    
    min_adresse = pd.concat([df_adresse,df_min],axis=1,ignore_index=True)
    #min_median = pd.DataFrame(min_median)
    min_median = pd.concat([min_adresse,df_median],axis=1,ignore_index=True)
    #min_median = pd.DataFrame(min_median)
    min_median_df_inter = pd.concat([min_median, df_max],axis=1,ignore_index=True)
    df_unité = df_model.loc["Unité"][:-1]
    min_median_df = pd.concat([min_median_df_inter, df_unité],axis=1,ignore_index=True)
    min_median_df = pd.DataFrame(min_median_df)
    min_median_df.columns = ['adresse','min','median','max','unité']
    min_median_df.index = df_model.loc['Texte'][:-1]
    save_df_in_excel(filename+'_Observations.xlsx',min_median_df)
    return 'Excel for Observations generated'


# In[74]:


Excel_for_Power_BI(data_1_just_data,data_1,'test_13_07')


# In[327]:


Excel_to_look(data_1_just_data,data_1,'test_13_07')
