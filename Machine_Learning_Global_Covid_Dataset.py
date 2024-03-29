
"""
You may skip this section if you are working with Anaconda jupyter-notebook on your local computer
"""

# Mounting to you own Google Colab drive
from google.colab import drive
try:
  drive.mount('/gdrive')
except:
  drive.mount('/content/gdrive', force_remount=True)

# Commented out IPython magic to ensure Python compatibility.
#The jupyter-notebook and dataset should be first placed in your Google drive under the folder name "ML2021"
#The following command is meant to set the directory as the current, in which this notebook will load the datasset from.
# %cd '/gdrive/MyDrive/ML 2021/Group Assignment'

"""# Installing specific analysis packages <a name="install_packages"></a>"""

!pip install missingno
!pip install pandas-profiling
!pip install empiricaldist
!pip install factor-analyzer
!pip install pycountry_convert
!pip install pycountry

"""# Loading analysis packages <a name="load_packages"></a>"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.feature_selection import SelectFromModel
from sklearn.utils import shuffle
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, chi2, f_classif
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import VotingRegressor
from sklearn.model_selection import train_test_split
from xgboost import plot_importance, plot_tree, XGBRegressor
from lightgbm import LGBMRegressor

from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split, GridSearchCV

import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import pycountry_convert as pc
import pycountry

#import the package for timeseries analysis
from statsmodels.tsa.seasonal import seasonal_decompose

import missingno as msno
# %matplotlib inline

pd.set_option('display.max_columns', 1000)

"""<a name='load_data'></a>
# Loading data
"""

#listing directory (works only if you gdrive's directory is with content folder)
!ls '/content/gdrive/My Drive/ML 2021/Group Assignment/'

try:
  train = pd.read_csv('train.csv')
  test = pd.read_csv('test.csv')
  submission = pd.read_csv('submission.csv')
  extra = pd.read_csv('owid-covid-data.csv')
except:
  train = pd.read_csv('/content/gdrive/My Drive/ML 2021/Group Assignment/train.csv')
  test = pd.read_csv('/content/gdrive/My Drive/ML 2021/Group Assignment/test.csv')
  submission = pd.read_csv('/content/gdrive/My Drive/ML 2021/Group Assignment/submission.csv')
  extra = pd.read_csv('/content/gdrive/My Drive/ML 2021/Group Assignment/owid-covid-data.csv')

"""Making Copies of the data 

"""

train_copy = train.copy()
test_copy = test.copy()
submission_copy = submission.copy() 
extra_copy = extra.copy()

"""# Data at first sight <a name='first_sight'></a>"""

train.head(50)

train.tail(30)

"""Observation:
* There are many NaN values in County and Province_state, as only some of the countries has these features. We can resolve this by concatenating the three 'location' features together in Data Prep, or dropping County and Province_state.
* Per country there are 2 "Weight" values, one is associated with "Target"="Fatalities", one is assciated with "Target"="ConfirmedCases"
* Some 0 values in "TargetValue", current assumption is because there were no 'ConfirmedCases' or 'Fatalities' that day.
* Population remains the same for each country for every day, i.e. population column does not update.
"""

test.head()

submission.head()

extra.head()

extra.tail()

"""Observation:
* Quite a lot of the columns across the extra dataset have a large amount of NaN. We will explore this further in EDA.
* Most of the numerical columns use float dtype (even for number cases and deaths)
* As mentioned in the group journal, some data columns(features) appear in both datasets, they are: "population", "ConfirmedCases" and "Fatalities". Therfore, we should make sure we do NOT mix the two datasets with these features if we use the extra dataset. Also, the extra dataset starts at the end of Feb 2020, whereas the train set from Kaggle for the assignment begins at the end of Jan 2020.
"""

train.info()

test.info()

test.shape

extra.info()

print("Train dataset (rows, cols):",train.shape, "\nTest dataset (rows, cols):",test.shape, "\nExtra dataset (rows, cols):",extra.shape)

"""Observation

* We see that the datatypes are as follows 
dtypes: float64(1), int64(3), object(5)

* There are 9 features in the train dataset, 8 in the test dataset and 67 features in the extra dataset

* The train dataset has 969640 rows, 311670 rows in the test dataset and 138727 rows in the extra dataset

# Metadata <a name='metadata'></a>

**Metadata (version 1)** for train data
"""

data = []
for feature in train.columns:
    # Defining the role
    if feature == 'TargetValue':
        role = 'target'
    elif feature == 'Id':
        role = 'id'
    else:
        role = 'input'
         
    # Defining the level
    if feature == 'Date':
        level = 'ordinal'
    elif feature == 'Id' or train[feature].dtype == object:
        level = 'nominal'
    else:
        level = 'interval'

        
    # Initialize keep to True for all variables except for id
    keep = True
    if feature == 'Id':
        keep = False
    
    # Defining the data type 
    dtype = train[feature].dtype
    
    # Creating a Dict that contains all the metadata for the variable
    feature_dict = {
        'varname': feature,
        'role': role,
        'level': level,
        'keep': keep,
        'dtype': dtype
    }
    data.append(feature_dict)
    
meta1 = pd.DataFrame(data, columns=['varname', 'role', 'level', 'keep', 'dtype'])
meta1.set_index('varname', inplace=True)
meta1

"""**Metadata (version 2)** for train data"""

data = []
for feature in train.columns:
    # Defining the role
    if feature == 'TargetValue':
        use = 'target'
    elif feature == 'Id':
        use = 'id'
    else:
        use = 'input'
         
    # Defining the type
    if feature == 'Target':
        type = 'binary'
    elif feature == 'Id' or train[feature].dtype == object:
        type = 'categorical'
    elif train[feature].dtype == float or isinstance(train[feature].dtype, float):
        type = 'real'
    else:
        type = 'integer'
        
    # Initialize preserve to True for all variables except for id
    preserve = True
    if feature == 'Id':
        preserve = False
    
    # Defining the data type 
    dtype = train[feature].dtype
    
    category = 'none'
    # Defining the category
    if feature == 'Date':
        category = 'date'
    elif feature == 'Id':
        category = 'id'
    elif feature == 'Target':
        category = 'Target Type'    
    elif train[feature].dtype == object:
        category = 'location'

    
    
    # Creating a Dict that contains all the metadata for the variable
    feature_dictionary = {
        'varname': feature,
        'use': use,
        'type': type,
        'preserve': preserve,
        'dtype': dtype,
        'category' : category
    }
    data.append(feature_dictionary)
    
meta2 = pd.DataFrame(data, columns=['varname', 'use', 'type', 'preserve', 'dtype', 'category'])
meta2.set_index('varname', inplace=True)
meta2

"""**Metadata (version 1)** for Extra data"""

#checking what's in column "tests_units" 
bool_series = pd.notnull(extra["tests_units"])
extra[bool_series]['tests_units'].unique()

data = []
for feature in extra.columns:
    # Defining the role
    if feature == 'iso_code':
        role = 'id'
    else:
        role = 'input'
         
    # Defining the level
    if feature == 'iso_code':
        level = 'nominal'
    elif extra[feature].dtype == float:
        level = 'interval'
    else:
        level = 'ordinal'
        
    # Initialize keep to True for all variables except for id
    keep = True
    if feature == 'iso_code':
        keep = False
    
    # Defining the data type 
    dtype = extra[feature].dtype
    
    # Creating a Dict that contains all the metadata for the variable
    feature_dict = {
        'varname': feature,
        'role': role,
        'level': level,
        'keep': keep,
        'dtype': dtype
    }
    data.append(feature_dict)
    
meta1_extra = pd.DataFrame(data, columns=['varname', 'role', 'level', 'keep', 'dtype'])
meta1_extra.set_index('varname', inplace=True)
meta1_extra

"""**Metadata (version 2)** for extra data"""

data = []
for feature in extra.columns:
    # Defining the role
    if feature == 'iso_code':
        use = 'id'
    else:
        use = 'input'
         
    # Defining the type
    if extra[feature].dtype == object:
        type = 'categorical'
    elif extra[feature].dtype == float or isinstance(extra[feature].dtype, float):
        type = 'real'
    else:
        type = 'integer'
        
    # Initialize preserve to True for all variables except for id
    preserve = True
    if feature == 'iso_code':
        preserve = False
    
    # Defining the data type 
    dtype = extra[feature].dtype
    
    category = 'none'
    # Defining the category
    if feature == 'tests_units':
        category = 'info'
    elif feature == 'date':
        category = 'date'
    elif feature == 'location' or feature == 'continent':
        category = 'location'
    

    
    
    # Creating a Dict that contains all the metadata for the variable
    feature_dictionary = {
        'varname': feature,
        'use': use,
        'type': type,
        'preserve': preserve,
        'dtype': dtype,
        'category' : category
    }
    data.append(feature_dictionary)
    
meta2_extra = pd.DataFrame(data, columns=['varname', 'use', 'type', 'preserve', 'dtype', 'category'])
meta2_extra.set_index('varname', inplace=True)
meta2_extra

"""Looking at the metadata for train dataset"""

pd.DataFrame({'count' : meta2.groupby(['use', 'type'])['use'].size()}).reset_index()

# Look at groupby for Extra dataset:
pd.DataFrame({'count' : meta2_extra.groupby(['use', 'type'])['use'].size()}).reset_index()

train.corr()

"""No clear correlation between any of the above features we can see in the table.

Observation for Metadata:
* The meta 1 is based on seperating out different variables while the meta 2 is based on labelling of variables.
* We can see that from train dataset we have binary(1), categorical(4), integer(1), real(1) and for extra dataset we have categorical(4) and real (62).

# Exploratory Data Analysis (EDA) <a name='eda'></a>
"""

# change date column to date dtype
train['Date'] = pd.to_datetime(train['Date'])
test['Date'] = pd.to_datetime(test['Date'])

"""## Visualization"""

import plotly.express as px
fig= plt.figure(figsize=(45,30))
fig= px.pie(train, names= 'Country_Region', values= 'TargetValue', color_discrete_sequence= px.colors.sequential.RdBu)
fig.update_traces(textposition = 'inside')

fig.show()

# ADEL VALIULLIN. (2020.) COVID-19 EDA and Forecasting. (Version 1.) [Source Code]. https://www.kaggle.com/mystery/covid-19-eda-and-forecasting/data?select=time_series_covid_19_confirmed.csv.

train['Date'] = pd.to_datetime(train.Date, format='%Y-%m-%d')
train_cc = train[(train['Target'] == 'ConfirmedCases') & (pd.isnull(train['Province_State'])) & (
    pd.isnull(train['County']))]
display(train_cc.head(2))
print(train_cc.shape)

train_fat = train[(train['Target'] == 'Fatalities') & (pd.isnull(train['Province_State'])) & (
    pd.isnull(train['County']))]
display(train_fat.head(2))
print(train_fat.shape)

#Pie-chart of confirmed cases worldwide
cc = px.pie(train_cc, values='TargetValue', color_discrete_sequence=px.colors.sequential.RdBu, names='Country_Region', title='Confirmed cases of all countries')
cc.update_traces(textposition='inside')
cc.update_layout(font_size=15)
cc.show()

# pie-chart of confirmed cases worldwide
fat = px.pie(train_fat, values='TargetValue', color_discrete_sequence=px.colors.sequential.RdBu, names='Country_Region', title='Fatalities of all countries',)
fat.update_traces(textposition='inside')
fat.update_layout(font_size=16)
fat.show()

"""Observations:

Both pie charts show that the the majority of confirmed cases and deaths due to covid-19 were found in the united states.

From this we can infer that the US is most likely driving the growth of cases. However this could be due to multiple factors. Such as the population size of the country as well as when the country went into lockdown
"""

date_data = train.groupby('Date').sum()
fig = px.line(x=date_data.index, y = date_data['TargetValue'], title = 'Worldwide COVID-19 cases over the first 5 weeks', labels = dict(x='Date', y = 'Number of Cases'))
fig.show()

"""**Observation:**

* The US is a leader in global Covid cases, accounting for 51.8% of positive cases and fatalities followed by Brazil (6.64%) and then Russia (4.09%).
* The above graph shows the global trend of cases over the first 5 weeks, until mid March there are relatively few cases (with the exception of a share rise and decline in the middle of Feb. However, from the middle of March we see a sharp rise in the number of cases unbtil around early to mid April where we see the number staying between the 125k - 175k cases (mostly).
"""

train_cc_gr = train_cc.copy()
train_cc_gr = train_cc_gr.groupby(['Country_Region'], as_index=False)['TargetValue'].sum()
train_cc_gr = train_cc_gr.nlargest(12, 'TargetValue')

train_cc2 = train_cc.copy()
train_cc2 = train_cc2.loc[train_cc2['Country_Region'].isin(train_cc_gr.Country_Region)]
train_cc2['cum_target'] = train_cc2.groupby(['Country_Region'])['TargetValue'].cumsum()

train_anim_cc = train_cc2[train_cc2["Date"].dt.strftime('%m').astype(int)>=3]
cc_overtime = px.bar(train_anim_cc, y="Country_Region", x='cum_target', orientation='h', color="Country_Region", labels={'cum_target': 'Confirmed Cases'},
                    hover_name="Country_Region", animation_frame=train_anim_cc["Date"].dt.strftime('%m-%d'),
                    title='Confirmed Cases Over Time', range_x=[0, train_cc2['cum_target'].max()],
                   color_discrete_sequence=px.colors.sequential.RdBu )
cc_overtime.update_layout(font_size=16, yaxis={'categoryorder':"total ascending"})
cc_overtime.show()

train_fat_gr = train_fat.copy()
train_fat_gr = train_fat_gr.groupby(['Country_Region'], as_index=False)['TargetValue'].sum()
train_fat_gr = train_fat_gr.nlargest(12, 'TargetValue')

train_fat2 = train_fat.copy()
train_fat2 = train_fat2.loc[train_fat2['Country_Region'].isin(train_fat_gr.Country_Region)]
train_fat2['cum_target'] = train_fat2.groupby(['Country_Region'])['TargetValue'].cumsum()

train_anim_fat = train_fat2[train_fat2["Date"].dt.strftime('%m').astype(int)>=3]

fat_overtime = px.bar(train_anim_fat, y="Country_Region", x='cum_target', orientation='h', color="Country_Region", labels={'cum_target': 'Fatalities'},
            animation_frame=train_anim_fat["Date"].dt.strftime('%m-%d'),
              title='Fatalities over time',range_x=[0, train_fat2['cum_target'].max()],
            color_discrete_sequence=px.colors.sequential.RdBu)
fat_overtime.update_layout(font_size=16, yaxis={'categoryorder':"total ascending"})
fat_overtime.write_html("fat_overtime.html")
fat_overtime.show()

train_cc3 = train_cc.copy()
train_cc3['cum_target'] = train_cc3.groupby(['Country_Region'])['TargetValue'].cumsum()

map_cc = px.choropleth(train_cc3, locations="Country_Region", locationmode='country names', color=np.log(train_cc3['cum_target']),
                    labels={'color': 'Confirmed Cases (log)'}, hover_name="Country_Region",
                     animation_frame=train_cc3["Date"].dt.strftime('%m-%d'),
                    title='Spread of covid', color_continuous_scale='Reds')
map_cc.update(layout_coloraxis_showscale=True)
map_cc.update_layout(font_size=16)
map_cc.show()

train_fat3 = train_fat.copy()
train_fat3['cum_target'] = train_fat3.groupby(['Country_Region'])['TargetValue'].cumsum()

map_fat = px.choropleth(train_fat3, locations="Country_Region", locationmode='country names', color=np.log(train_fat3['cum_target']),
                    labels={'color': 'Fatalities (log)'}, hover_name="Country_Region", animation_frame=train_fat3["Date"].dt.strftime('%m-%d'),
                    title='Fatalities over time', color_continuous_scale='Reds')
# fig.update(layout_coloraxis_showscale=False)
map_fat.update_layout(font_size=16)
map_fat.show()

"""## Data Quality Issues <a name='data_quality'></a>

### Data duplications
"""

train.shape

train.drop_duplicates()
train.shape

test.shape

test.drop_duplicates()
test.shape

extra.shape

extra.drop_duplicates()
extra.shape

"""Observations:
* Comparing to **Train**, there's 1 one missing feature in the **Test**. It is the Target_Value column.
* No duplicate records were found in all **Train**, **Test** and **extra** dataset.

### Missing Values

Missing values in Train data
"""

train.isnull().sum()

test.isnull().sum()

print('NaN values =', train.isnull().sum().sum())
print("""""")

vars_with_missing = []

for feature in train.columns:
    missings = train[feature].isna().sum()
    
    if missings > 0 :
        vars_with_missing.append(feature)
        missings_perc = missings / train.shape[0]
        
        print('Variable {} has {} records ({:.2%}) with missing values.'.format(feature, missings, missings_perc))
print('In total, there are {} variables with missing values'.format(len(vars_with_missing)))
# will deal with these by concatenating the location columns with Country and then dropping the others.

#!pip install missingno

# Commented out IPython magic to ensure Python compatibility.
import missingno as msno  # Visualize missing values
# %matplotlib inline
msno.matrix(train)

msno.bar(train);

msno.heatmap(train)

"""Observations 

Missing values for County and Province_State are highly correlated, meaning it is highly likely that the rows with missing county information will also have missing province_state information.

Missing values in the extra dataset
"""

print('NaN values =', extra.isnull().sum().sum())
print("""""")

vars_with_missing = []

for feature in extra.columns:
    missings = extra[feature].isna().sum()
    
    if missings > 0 :
        vars_with_missing.append(feature)
        missings_perc = missings / extra.shape[0]
        
        print('Variable {} has {} records ({:.2%}) with missing values.'.format(feature, missings, missings_perc))
print('In total, there are {} variables with missing values'.format(len(vars_with_missing)))

# Commented out IPython magic to ensure Python compatibility.
import missingno as msno  # Visualize missing values
# %matplotlib inline
msno.matrix(extra)

msno.heatmap(extra)

msno.dendrogram(extra)

df_missing_train = pd.DataFrame({'column':train.columns, 'missing(%)':((train.isna()).sum()/train.shape[0])*100})
df_missing_test = pd.DataFrame({'column':test.columns, 'missing(%)':((test.isna()).sum()/test.shape[0])*100})
df_missing_extra = pd.DataFrame({'column':extra.columns, 'missing(%)':((extra.isna()).sum()/extra.shape[0])*100})

df_missing_train_nl = df_missing_train.nlargest(7, 'missing(%)')
df_missing_test_nl = df_missing_test.nlargest(7, 'missing(%)')
df_missing_extra_nl = df_missing_extra.nlargest(64, 'missing(%)')

sns.set_palette(sns.color_palette('nipy_spectral'))

plt.figure(figsize=(16,3))
sns.barplot(data= df_missing_train_nl, x='column', y='missing(%)',palette='nipy_spectral')
plt.title('Missing values (%) in training set')
plt.show()

plt.figure(figsize=(16,3))
sns.barplot(data= df_missing_test_nl, x='column', y='missing(%)',palette='nipy_spectral')
plt.title('Missing values (%) in test set')
plt.show()

plt.figure(figsize=(16,3))
sns.barplot(data= df_missing_extra_nl, x='column', y='missing(%)',palette='nipy_spectral')
plt.xticks(rotation=90)
plt.title('Missing values (%) in extra set')
plt.show()

"""Observations: 
* Missing value proportions tend to be consistent across the **train** and **test** dataset
* Lots of features with high % of missing values in the extra dataset.
* Too many values to sensibly visualise in Extra data set. Will drop features with more than 40% initially.
"""

# dropping columns from extra dataset (missing more than 40%)
perc = 41.0 # Like N %
min_count =  int(((100-perc)/100)*extra.shape[0] + 1)
extra_dropna = extra.dropna( axis=1, 
                thresh=min_count)

#check shape
extra_dropna.shape

msno.heatmap(extra_dropna)

"""##Observations:

* The graph above shows the correlation of misssing values in columns of the extra data set. 

* All missing values in the extra dataset are positively correlated with each other

* We can infer that the data is missing completely at random.

## Univariate Exploration <a name='univariate_exploration'></a>

### Cardinality

Cardinality of train data
"""

var = meta2[(meta2.type == 'categorical') & (meta2.preserve)].index

for feature in var:
    dist_values = train[feature].value_counts().shape[0]
    print('Variable {} has {} distinct values'.format(feature, dist_values))

"""Cardinality of extra data"""

var = meta2_extra[(meta2_extra.type == 'categorical') & (meta2_extra.preserve)].index

for feature in var:
    dist_values = extra[feature].value_counts().shape[0]
    print('Variable {} has {} distinct values'.format(feature, dist_values))

"""### Real (Interval) features

Real type data in extra data
"""

variable = meta2_extra[(meta2_extra.type == 'real') & (meta2_extra.preserve)].index
extra[variable].describe()

data = []
for feature in extra_dropna.columns:
    # Defining the role
    if feature == 'iso_code':
        use = 'id'
    else:
        use = 'input'
         
    # Defining the type
    if extra_dropna[feature].dtype == object:
        type = 'categorical'
    elif extra_dropna[feature].dtype == float or isinstance(extra_dropna[feature].dtype, float):
        type = 'real'
    else:
        type = 'integer'
        
    # Initialize preserve to True for all variables except for id
    preserve = True
    if feature == 'iso_code':
        preserve = False
    
    # Defining the data type 
    dtype = extra_dropna[feature].dtype
    
    category = 'none'
    # Defining the category
    if feature == 'tests_units':
        category = 'info'
    elif feature == 'date':
        category = 'date'
    elif feature == 'location' or feature == 'continent':
        category = 'location'
    

    
    
    # Creating a Dict that contains all the metadata for the variable
    feature_dictionary = {
        'varname': feature,
        'use': use,
        'type': type,
        'preserve': preserve,
        'dtype': dtype,
        'category' : category
    }
    data.append(feature_dictionary)
    
meta2_extra_dropna = pd.DataFrame(data, columns=['varname', 'use', 'type', 'preserve', 'dtype', 'category'])
meta2_extra_dropna.set_index('varname', inplace=True)
meta2_extra_dropna

extra_dropna.info()

fig = make_subplots(rows=1, cols=4)
# Use x instead of y argument for horizontal plot
fig.add_trace(go.Box(y=extra['reproduction_rate'], name='reproduction rate'),row=1,col=1)
fig.add_trace(go.Box(y=extra['population_density'], name='population density'),row=1,col=2) # can it show beloew 10k and the 2 outliers?
fig.add_trace(go.Box(y=extra['median_age'], name='median age'),row=1,col=3)
fig.add_trace(go.Box(y=extra['human_development_index'], name='human development index'),row=1,col=4)
fig.show()

"""### Observations

The figure above shows that there are outliers in the features: population densisty and reproduction rate.

These columns would need to be scaled before they are put through a ML model

## Bivariate Exploration <a name='bivariate_exploration'></a>

### Real (Interval) features
"""

def corr_heatmap(sample, masking=False):
    sns.set_style('whitegrid')
    # Create color map ranging between two colors
    cmap = sns.diverging_palette(50, 10, as_cmap=True)
    fig, ax = plt.subplots(figsize=(10,10))
    
    if masking==False:
        correlations = sample.corr()
        sns.heatmap(correlations, cmap=cmap, vmax=1.0, center=0, fmt='.2f', 
                    square=True, linewidths=.5, annot=True, cbar_kws={"shrink": .75})
    else:
        correlations = np.triu(sample.corr())
        sns.heatmap(sample.corr(), cmap=cmap, vmax=1.0, center=0, fmt='.2f',
                square=True, linewidths=.5, annot=True, cbar_kws={"shrink": .75}, 
                    mask=correlations)
    plt.show();

# much easier to read compared to the graph without dropped features
sample = extra_dropna.sample(1000)
var = meta2_extra_dropna[(meta2_extra_dropna.type == 'real') & (meta2_extra_dropna.preserve)].index
sample = sample[var]
corr_heatmap(sample, masking=True)

"""Observations:

No clear observations can be made from this graph as there are too many features 
"""

corr_heatmap(train, masking=True)

"""Observation: 
* No obvious correlations between any of the features in the train dataset.

* very weak correaltion between targetvalue and population

 
"""

# car categories - needs changing to COVID columns
sample = extra_dropna.sample(1000)
var = ['iso_code', 'total_cases', 
       'new_cases_smoothed_per_million', 'new_deaths_smoothed_per_million', 
       'total_deaths_per_million', 'population_density',
       'aged_65_older', 'stringency_index']
sample = sample[var]

sns.pairplot(sample)

#sns.pairplot(sample,  hue='target', 
#            palette = 'Set1', diag_kind='kde')
plt.show()

"""Observation.

* We have visualized the features in the Real(Interval) variables using Pairplot.
* By seeing at the cluster of graphs we can say that the some columns are corelated For eg: New cases smoothed per million which is on X axis and the New deaths smoothed per million which is on y axis have a positive corelation.



"""

sns.jointplot(x='new_cases', y='extreme_poverty', data=extra, 
              kind="hist")

"""Observation.

* We have visualise the correlation between extreme poverty and new cases features in the real (Interval) variables using joint-plot.

* The graphs showsthat in countries less burdened by poverty, they have more cases of COVID-19

"""

sns.scatterplot(x='extreme_poverty',y='new_cases',data=extra)

"""this graph shows that with increase in poverty there is less number of cases but there is a possibility that in some countries due to lack of medical amenities and high cost of health care ,cases are not reported."""

sample_nc = extra.sample(1000)
var_nc = ['new_cases', 'new_deaths', 'people_vaccinated']
sample_nc = sample_nc[var_nc]

sns.lmplot(x='new_cases', y='people_vaccinated', data=sample_nc, palette='Set1', scatter_kws={'alpha':0.3})


sns.lmplot(x='new_deaths', y='people_vaccinated', data=sample_nc, palette='Set1', scatter_kws={'alpha':0.3})


plt.show()

"""Observation.

* Here, the first Implot shows the people who are vaccinated vs the new cases  so as the new cases are going up, the mre people are getting vaccinated. 
* Both graphs show a positive correlation between deaths, cases and Vaccinations

* However, the gradient is lower in the second graph, it shows the relationship between the people who are vaccinated vs the new deaths are which means the there is increase in the new deaths but more people are getting vaccinated.

 
"""

sample_nc = extra.sample(2000)
var_nc = ['new_cases', 'new_deaths', 'people_vaccinated']
sample_nc = sample_nc[var_nc]

sns.jointplot(x='new_cases', y='people_vaccinated', data=sample_nc, kind="hist")

sns.jointplot(x='new_deaths', y='people_vaccinated', data=sample_nc, kind="hist")

plt.show()

"""Observation:

No observation can be made as it is quite difficult to infer from a small graph

### Integer (Ordinal) features
"""

# Removed if type(cat) == str: line as it prevented the chart from being produced 
cats = extra['tests_units'].unique()
tests_units_cat_list = []
tests_units_sum_list = []

for cat in cats:
    tests_units_cat_list.append(cat)
    tests_units_sum_list.append(extra[extra['tests_units'] == cat].shape[0])

#NaN handling
tests_units_cat_list.append('NaN')
tests_units_sum_list.append(extra['tests_units'].isna().sum())

fig = plt.figure(figsize=(12,5))
ax = fig.add_axes([0,0,1,1])
sns.barplot(tests_units_cat_list,tests_units_sum_list,palette='nipy_spectral')
plt.xticks(rotation=45)
ax.set_ylabel('Count')
ax.set_xlabel('Label')
plt.title('Ordinal features - Tests_units')
plt.show()

"""Observations:

This graph showing the ordinal feature test_units, shows that the majority of the records are missing (around 60500)

## Other EDAs 
other EDAs that are not in lab work
"""

x = train[train['Target'] == 'ConfirmedCases']['Date']
y = train[train['Target'] == 'ConfirmedCases']['TargetValue']


plt.figure(figsize=(25,3))
plt.scatter(x, y, cmap=train['Country_Region'])
plt.xticks(rotation=90)
plt.title('Confirmed cases over time')
plt.show()

"""* In Febuary the rate of confirmed cases were lower than 20k.
* After mid March the caonfirmed cases started to rise over 30k.

"""

grouped_data= train.groupby('Country_Region').sum()

top_10_pop_countries= grouped_data.nlargest(10,'Population')['TargetValue']

top_10_pop_countries

train['Date']= pd.to_datetime(train['Date'])
test['Date']= pd.to_datetime(test['Date'])

date_grouped_data= train.groupby('Date').sum()

fig = px.line(x= date_grouped_data.index, y= date_grouped_data['TargetValue'], title= 'growth of covid cases over time', labels= dict( x='Date', y='Number of covid cases'))
fig.show()

# BHAVYA KHURANA. (2021.) COVID-19 Global Forcasting. (Version 1.) [Source Code]. https://www.kaggle.com/bhavyakhurana/covid-19-global-forcasting#DATA-PROCESSING

"""* There was a spike on Feb 12 with 802 cases.
* There was a exponential growth on march 12 after that the rises in cases where seen.
* The maximum amount of cases where seen on June 5 which was 205.329k.

###Time Series - Seasonality
"""

df_dict = {'test':test,
           'train':train
          }

for key, value in df_dict.items():
    #print('--------'+key+'---------')
    value.columns = value.columns.str.lower()
    #print(value.head())
    #print(value.info())

'''
Function to provide alpha 2 codes for each country
'''
def findCountry(country_name):
    '''
    try-except as some alpha codes need manual input
    '''
    try:
        return pycountry.countries.get(name=country_name).alpha_2
    except:
        return ("not found")
train['country_alpha_2'] = train.country_region.apply(findCountry)

#Countries that need manual alpha 2 input
train.country_region[train.country_alpha_2=='not found'].value_counts()

train[train['country_region']=='US'].head()

#Dictionary containing missing countries' alpha 2
alpha_2_dict = {
    'Korea':'KR',
    'Korea, South':'KR',
    'Congo (Brazzaville)':'CG',
    'Laos':'LA',
    'Moldova':'MD',
    'Brunei':'BN',
    'Bolivia':'BO',
    'Russia':'RU',
    'Vietnam':'VN',
    'Venezuela':'VE',
    'Cote d\'Ivoire':'CI',
    'Taiwan':'TW',
    'West Bank and Gaza':'PS',
    'Iran':'IR',
    'Tanzania':'TZ',
    'Syria':'SY',
    'Congo (Kinshasa)':'CD',
    'US':'US',
    'Kosovo':'RS',
    'Burma':'MM',
    'MS Zaandam':'NL',
    'Taiwan*':'TW',
    'Holy See':'IT',
    'Diamond Princess':'JP'

}

#Apply the dictionary to dataframe, mapping to alpha 2 column
train.loc[train.country_alpha_2=='not found', 'country_alpha_2']=train.country_region.map(alpha_2_dict)

#Check if above worked
train.country_alpha_2.value_counts()

#Set continent from alhpa 2
def alpha2_to_continent(alpha2):
    #country_alpha2 = pc.country_name_to_country_alpha2(country_name)
    try:
        country_continent_code = pc.country_alpha2_to_continent_code(alpha2)
        country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
        return country_continent_name
    except:
        return ('error')

#Apply the alpha2_to_continent function
train['continent'] = train['country_alpha_2'].apply(alpha2_to_continent)

#Check if above worked
train.continent.value_counts()

#Show what alpha 2 codes need manual input
train.country_region[train.continent=='error'].value_counts()

#Show what alpha 2 codes need manual input
train.country_alpha_2[train.continent=='error'].value_counts()

#Replace 'error' with Africa as missing value is only from Western Sahara
#If any others missing this will be ineffective
train.loc[train.continent=='error', 'continent']='Africa'

#Check if error value has been removed
train.continent.value_counts()

#Convert date column to datetime dtype
train.date = pd.to_datetime(train.date)

#create a copy of the dataframe
seasonal_analysis = train.copy()

#Dataframe containing useful columns for timeseries
seasonal_analysis_short = seasonal_analysis[['date', 'continent', 'target', 'targetvalue']]

seasonal_analysis_short.head()

#Split dataframe into confirmedcases and fatalities
confirmed_cases = seasonal_analysis_short[seasonal_analysis_short['target']=='ConfirmedCases']
fatal_cases = seasonal_analysis_short[seasonal_analysis_short['target']=='Fatalities']

#remove target column and set the index to date column
confirmed_cases = confirmed_cases.drop(['target'], axis=1)
confirmed_cases = confirmed_cases.set_index('date')

fatal_cases = fatal_cases.drop(['target'], axis=1)
fatal_cases = fatal_cases.set_index('date')

'''
List containing both dataframes
'''
case_types = {
    'Confirmed Cases':confirmed_cases,
    'Fatal Cases':fatal_cases
    }

'''
Loop through both dataframes
'''
for case_type_key, case_type_value in case_types.items():
    

      '''
      Create a variable to be used in each iteration,
      Filter to the specific continent
      Drop continent column
      Resample the data to x days
      '''
      temp = case_type_value.drop('continent', axis=1)
      temp = temp.resample('1D').sum() #resample value change for trend over different periods

      '''
      Plot seasonal decomposition info
      '''
      decomposed_cases = seasonal_decompose(temp)
      plt.figure(figsize=(18, 4))
      plt.subplot(131)
      decomposed_cases.trend.plot(ax=plt.gca())
      plt.title('Global - {} - Trend'.format(case_type_key))
      plt.subplot(132)
      decomposed_cases.seasonal.plot(ax=plt.gca())
      plt.title('Global - {} - Seasonality'.format(case_type_key))
      plt.subplot(133)
      decomposed_cases.resid.plot(ax=plt.gca())
      plt.title('Global - {} - Residuals'.format(case_type_key))
      plt.tight_layout()

"""Location|Trend|Seasonality|Residual
---|---|---|---
GLOBAL - Confirmed Cases|The trend spikes at mid-March of 2020 with cases from <10,000 per day <br>to almost 150,000 per day at the start of April, where it continues around 150,000 <br>until June where it spikes again.  |Seasonality follows a weekly pattern that fluctuates between +10,000 and -7,500| 
GLOBAL - Fatal Cases|Trend follows same pattern as confirmed cases, spike in mid-March <1000 <br>to <13,000 beginning of April, however it declines in mid-April back down to around 6,000 per day|Seasonality also follows the same weekly pattern between +750 and -1,250|

"""

'''
List containing each continent
'''
continents = [
    'Africa',
    'Asia',
    'Europe',
    'North America',
    'Oceania',
    'South America'
]

'''
List containing both dataframes
'''
case_types = {
    'Confirmed Cases':confirmed_cases,
    'Fatal Cases':fatal_cases
    }
'''
Loop through each continent
'''
for continent in continents:
  '''
  Loop through both dataframes
  '''
  for case_type_key, case_type_value in case_types.items():
    
    

        '''
        Create a variable to be used in each iteration,
        Filter to the specific continent
        Drop continent column
        Resample the data to x days
        '''
        temp = case_type_value[case_type_value['continent']==continent]
        temp = temp.drop('continent', axis=1)
        temp = temp.resample('1D').sum() #resample value change for trend over different periods

        '''
        Plot seasonal decomposition info
        '''
        decomposed_cases = seasonal_decompose(temp)
        plt.figure(figsize=(18, 4))
        plt.subplot(131)
        decomposed_cases.trend.plot(ax=plt.gca())
        plt.title('{} - {} - Trend'.format(continent, case_type_key))
        plt.subplot(132)
        decomposed_cases.seasonal.plot(ax=plt.gca())
        plt.title('{} - {} - Seasonality'.format(continent, case_type_key))
        plt.subplot(133)
        decomposed_cases.resid.plot(ax=plt.gca())
        plt.title('{} - {} - Residuals'.format(continent, case_type_key))
        plt.tight_layout()

"""Location|Trend|Seasonality|Residual
---|---|---|---
Africa - Confirmed|Sub 1000 cases to mid-March, spikes to 100,000 at start of April, slowly declines to 75,000 in June||
Africa - Fatal|Similar trend to confirmed, spike is mid-April with 7,000 daily fatalities||
Asia - Confirmed|Asia is the only continent to spike cases between mid-January and mid-February up to 10,000 a day,<br> cases drops down to sub 1,000 until mid-March, where cases steadily increase to 30,000 daily in June ||
Asia - Fatal|Same trend as confirmed, however large spike in mid-April to 700 that drops to normal levels in roughly 1 week.<br> Flattens during May around 400 fatalities, then increases to 650 in June.||
Europe - Confirmed|Sub 1000 cases to mid-March, spikes to 35,000 at start of April, slowly declines to 15,000 in June||
Europe - Fatal|Same pattern up to April with 4000 fatalities, steeper decrease between April and June||
North America - Confirmed|Low cases until mid-March, steady increase to 7,000 cases per day in June||
North America - Fatal|Fatal cases increase at beginning of April, steady climb to 800 per day in June||
Oceania - Confirmed|Cases spike mid-March to 800, drop to under 50 by mid-April||
Oceania - Fatal|Fatalities climb mid-March, peak start of April with 8 daily, drops to normal level at start of May||
South America - Confirmed|Cases steadily increase from mid-March to 40,000 daily in June||
South America - Fatal|Fatal cases follows the same pattarn, peaking at 1,400 daily in June||

The trends for continent data begin at different points in time, the order of cases first appearing goes; <br>Asia, <br>Oceania, <br>Europe, <br>North America,  <br>Africa, <br> South America.<br>

Some continents have been hit harder than others, Africa is the worst off with a peak over 100,000, and South America being 2nd with a peak of 40,000. <br>Oceania had the lowest peak with 800, followed by North America with 7,000. 

Seasonality for all graphs follow a weekly pattern.
"""

temp_train = train.copy()

"""# *SIR* Graphical Visualisation_ Japan"""

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)



pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 200)

# BHIROYUKI ICHIJO. (2021.) SIR Fitting. (Version 1.) [Source Code]. https://www.kaggle.com/ichijo/sir-fitting

sir_train = pd.read_csv('train.csv')
sir_test = pd.read_csv('test.csv')
print(sir_train.head())
print(sir_test.head())
train_jp = sir_train[sir_train['Country_Region']=='Japan'].copy()
test_jp = sir_test[sir_test['Country_Region']=='Japan'].copy()
train_jp.drop(['County', 'Province_State'], axis=1,  inplace=True)
test_jp.drop(['County', 'Province_State'], axis=1,  inplace=True)
print(train_jp.info())
print(test_jp.info())

train_jp['Date'] = pd.to_datetime(train_jp.Date)
train_jp['dayofyear'] = train_jp.Date.dt.dayofyear
train_jp_c = train_jp[train_jp.Target=='ConfirmedCases']
train_jp_f = train_jp[train_jp.Target=='Fatalities']
train_jp_c.tail()

test_jp['Date'] = pd.to_datetime(test_jp.Date)
test_jp['dayofyear'] = test_jp.Date.dt.dayofyear
test_jp_c = test_jp[test_jp.Target=='ConfirmedCases']
test_jp_f = test_jp[test_jp.Target=='Fatalities']
test_jp_c.head()

# The 3/4 of population might not be infected finally.
population = train_jp.Population.iloc[0]/4
# b = 1.5 # infecters per week
# c = 0.5 # recover ratio
# d = 0.1 # death ratio
t_arr = np.array(train_jp_c.dayofyear)
y_arr = np.array(train_jp_c.TargetValue)
test_t_arr = np.array(test_jp_c.dayofyear)

# Start from the data has more than 10 infects.
start_day = list(y_arr>=10).index(True)
print(start_day)

t_arr = t_arr[start_day:]
y_arr = y_arr[start_day:]
t_arr_first = t_arr[0]
t_arr -= t_arr_first
test_t_arr -= t_arr_first

# cleansing
for i,n in enumerate(y_arr):
    if n > 0:
        if n > 1000:
            y_arr[i] = (y_arr[i-1] + y_arr[i+1]) / 2
        else:
            continue
    else:
        y_arr[i] = (y_arr[i-1] + y_arr[i+1]) / 2

from scipy import integrate, optimize


susceptible_0 = population - y_arr[0]
infected_0 = y_arr[0]

def sir(y,t,b,c,d):
    susceptible = -b * y[0] * y[1] / susceptible_0
    recovered = c * y[1]
    fatarities = d * y[1]
    infected = -(susceptible + recovered + fatarities)
    return susceptible,infected,recovered,fatarities

def inf_odeint(t,b,c,d):
    return integrate.odeint(sir,(susceptible_0,infected_0,0,0),t,args=(b,c,d))[:,1]

popt, pcov = optimize.curve_fit(inf_odeint, t_arr, y_arr)

# fitted = inf_odeint(np.append(t_arr,test_t_arr), *popt)
fitted = inf_odeint(t_arr, *popt)

import matplotlib.pyplot as plt

plt.plot(t_arr, y_arr, 'bo')
# plt.plot(np.append(t_arr,test_t_arr), fitted)
plt.plot(t_arr, fitted)

plt.title("Fit of infected model")
plt.ylabel("Population infected")
plt.xlabel("Days")
plt.show()

"""The above graph shows the fit of the SIR (susceptible, recovered, fatalities and infected) model for Japan over the dataset. In our research we realised this could be a really effective way to fit data to a model to predict health / infection trends. However, unfortunately, we ran out of time to try and apply this to our dataset further than including the graph representation above. If we were to do something like this in the future we would include SIR modelling.

# Data Preparation
"""

#Creating a savepoint
train_savepoint1 = train.copy()
test_savepoint1 = test.copy()

"""##Dropping Columns"""

# Drop the null columns, which are County and Province_State
train.dropna(axis=1, inplace = True)
test.dropna(axis=1, inplace=True)

train.info()

#Drop columns in train
train.drop(['id','country_alpha_2','continent'],axis=1, inplace=True)

#Save test data's ForecastId for later use and drop it from the test data
test_id = test['forecastid']
test.drop(['forecastid'], axis = 1, inplace=True)

"""##Label Encoding"""

#Lable encode categoriacal features, which are Country_Region and Target
from sklearn.preprocessing import LabelEncoder

le1 = LabelEncoder()
train['country_region'] = le1.fit_transform(train['country_region'])
test['country_region'] = le1.transform(test['country_region'])

le2 = LabelEncoder()
train['target'] = le2.fit_transform(train['target'])
test['target'] = le2.transform(test['target'])

"""##Adding SMAs"""

#Handling Confirmed Cases and fatalities separately
train_ConfirmedCases = train[train['target'] == 0].reset_index(drop=True)
train_Fatalities = train[train['target'] == 1].reset_index(drop=True)

train_ConfirmedCases_5 = train_ConfirmedCases.groupby(['country_region'])['targetvalue'].rolling(5).mean().reset_index()
train_ConfirmedCases_10 = train_ConfirmedCases.groupby(['country_region'])['targetvalue'].rolling(10).mean().reset_index()
train_ConfirmedCases_15 = train_ConfirmedCases.groupby(['country_region'])['targetvalue'].rolling(15).mean().reset_index()
train_ConfirmedCases_30 = train_ConfirmedCases.groupby(['country_region'])['targetvalue'].rolling(30).mean().reset_index()


train_ConfirmedCases['SMA_5'] = train_ConfirmedCases_5['targetvalue']
train_ConfirmedCases['SMA_10'] = train_ConfirmedCases_10['targetvalue']
train_ConfirmedCases['SMA_15'] = train_ConfirmedCases_15['targetvalue']
train_ConfirmedCases['SMA_30'] = train_ConfirmedCases_30['targetvalue']

train_Fatalities_5 = train_Fatalities.groupby(['country_region'])['targetvalue'].rolling(5).mean().reset_index()
train_Fatalities_10 = train_Fatalities.groupby(['country_region'])['targetvalue'].rolling(10).mean().reset_index()
train_Fatalities_15 = train_Fatalities.groupby(['country_region'])['targetvalue'].rolling(15).mean().reset_index()
train_Fatalities_30 = train_Fatalities.groupby(['country_region'])['targetvalue'].rolling(30).mean().reset_index()

train_Fatalities['SMA_5'] = train_Fatalities_5['targetvalue']
train_Fatalities['SMA_10'] = train_Fatalities_10['targetvalue']
train_Fatalities['SMA_15'] = train_Fatalities_15['targetvalue']
train_Fatalities['SMA_30'] = train_Fatalities_30['targetvalue']

#Combine 2 sets back together
train_combined = pd.concat([train_ConfirmedCases, train_Fatalities])

#Delete NaN in SMAs
train_combined = train_combined.dropna(subset = ['SMA_5']).reset_index(drop=True)
train_combined = train_combined.dropna(subset = ['SMA_10']).reset_index(drop=True)
train_combined = train_combined.dropna(subset = ['SMA_15']).reset_index(drop=True)
train_combined = train_combined.dropna(subset = ['SMA_30']).reset_index(drop=True)

#Sorting and re-indexing
train_combined = train_combined.sort_values(by=['country_region', 'date','target'])
train_combined = train_combined.reset_index(drop=True)

"""##Scaling"""

#Scaling the train data
ss = StandardScaler()
Scaled_train = train_combined.copy()
for column in train_combined.columns:
  Scaled_train[column] = ss.fit_transform(train_combined[column].values.reshape((-1,1)))

"""##Splitting Dataset for modeling"""

#Split train data in test, valid
test_size  = 0.15
valid_size = 0.15

test_split_idx  = int(train_combined.shape[0] * (1-test_size))
valid_split_idx = int(train_combined.shape[0] * (1-(valid_size+test_size)))

train_df  = train_combined.loc[:valid_split_idx].copy()
valid_df  = train_combined.loc[valid_split_idx+1:test_split_idx].copy()
test_df   = train_combined.loc[test_split_idx+1:].copy()

#Split data into X,Y
y_train = train_df['targetvalue'].copy()
X_train = train_df.drop(['targetvalue','date'], 1)

y_valid = valid_df['targetvalue'].copy()
X_valid = valid_df.drop(['targetvalue','date'], 1)

y_test  = test_df['targetvalue'].copy()
X_test  = test_df.drop(['targetvalue','date'], 1)

"""##Experimenting Shift/mean feature generation"""

temp_train['date'] = pd.to_datetime(temp_train['date'])

temp_train = temp_train.fillna('')
temp_train['location'] = temp_train['country_region'] + '-' + temp_train['province_state'] + '-' + temp_train['county']


temp_train['targetvalue'] = temp_train['targetvalue'].astype('int')
temp_train['rolling_mean'] = temp_train.groupby(['location', 'target'])['targetvalue'].shift().rolling(7).mean()
grouped_temp_train = temp_train.groupby(['location', 'target'])

grouped_temp_train.rolling_mean.plot(alpha=0.4, legend=False)
plt.title('Grouped rolling means by region and target')
plt.ylabel('Mean cases')
plt.xlabel('Date');

"""Graph isn't supposed to be pretty, just using to see if groupby has done as expected.<br>
Can see many different means have been created for each location point
"""

temp_train.dropna(inplace=True)

from sklearn.preprocessing import OrdinalEncoder
oe = OrdinalEncoder()
temp_train[['country_region', 'target', 'country_alpha_2', 'location','continent']] = (
    oe.fit_transform(temp_train[['country_region', 'target', 'country_alpha_2', 'location','continent']])
    )

temp_train[['country_region', 'target', 'country_alpha_2', 'location','continent']] = (
    temp_train[['country_region', 'target', 'country_alpha_2', 'location','continent']].astype('int')
)

#temp_train = temp_train.set_index('date')
temp_train = temp_train.drop(['date','county','province_state'], axis=1)

"""#### LinearRegression shift/mean feature generation"""

from sklearn.linear_model import LinearRegression
'''create a copy of columns to reset dataframe columns after make_features'''
column_copy = temp_train.columns.copy()


'''This function creates the columns for the dataframe'''

'''inputs set to dataframe, maximum value for shift, and what the rolling mean size should be'''
def make_features(data, max_shift, rolling_mean_size):

    '''shift feature created with max_shift as an end point.
    Column will be made for each shift feature up to max_shift'''
    for shift in range(1, max_shift + 1):
        data['shift_{}'.format(shift)] = data['targetvalue'].shift(shift)

    '''rolling mean column created with argument rolling_mean_size'''
    data['rolling_mean'] = data.groupby(['location', 'target'])['targetvalue'].shift().rolling(rolling_mean_size).mean()

max_lag_list = []
rolling_mean_list = []
rmse_list = []

'''i in range(1,10) to iterate max_lag'''
for i in range(1,10):
    
    '''j in range(1,25) to iterate rolling_mean'''
    for j in range(1,25):
        
        '''call make_features function and pass data, i, j'''
        make_features(temp_train, i, j)

        '''train_test_split for data, test_size 20% of original data,
        shuffle=False so data stays chronological, random_state set for repeatability'''
        features_train, features_valid = train_test_split(
         temp_train, test_size = 0.2, shuffle=False, random_state=1)

        '''na values dropped as lag feature will generate na values'''
        features_train = features_train.dropna()
        features_valid = features_valid.dropna()

        '''features and target variables for train, valid, and test set'''
        target_train = features_train['targetvalue']
        features_train = features_train.drop(['targetvalue'], axis=1)

        target_valid = features_valid['targetvalue']
        features_valid = features_valid.drop(['targetvalue'], axis=1)
        
        '''linear regression model'''
        model = LinearRegression()
        model.fit(features_train, target_train)
        
        '''prediction using test features'''
        predict_valid = model.predict(features_valid)
        
        '''lists at top of block appended with values'''
        max_lag_list.append(i)
        rolling_mean_list.append(j)
        rmse_list.append(mean_squared_error(target_valid, predict_valid)**0.5)
        
        '''reset columns in dataframe to remove make_features'''
        #this line is probably what the warnings are
        temp_train = temp_train[column_copy]


'''dataframe created from lists at top of block'''
mse_linear_reg = pd.DataFrame({'max_lag': max_lag_list, 'rolling_mean': rolling_mean_list,
                                    'rmse': rmse_list})

'''min value for rmse to be returned'''
print(mse_linear_reg[mse_linear_reg['rmse']==mse_linear_reg['rmse'].min()])
print(mse_linear_reg.nsmallest(20, 'rmse'))

"""### XGBRegressor shift/mean feature generation

Below takes ~50mins to run
"""

max_lag_list = []
rolling_mean_list = []
rmse_list = []

'''i in range(1,10) to iterate max_lag'''
for i in range(1,10):
    
    '''j in range(1,5) to iterate rolling_mean'''
    for j in range(1,5):
        
        '''call make_features function and pass data, i, j'''
        make_features(temp_train, i, j)

        '''train_test_split for data, test_size 20% of original data,
        shuffle=False so data stays chronological, random_state set for repeatability'''
        features_train, features_valid = train_test_split(
         temp_train, test_size = 0.2, shuffle=False, random_state=1)

        '''na values dropped as lag feature will generate na values'''
        features_train = features_train.dropna()
        features_valid = features_valid.dropna()

        '''features and target variables for train, valid, and test set'''
        target_train = features_train['targetvalue']
        features_train = features_train.drop(['targetvalue'], axis=1)

        target_valid = features_valid['targetvalue']
        features_valid = features_valid.drop(['targetvalue'], axis=1)
        
        '''linear regression model'''
        model = XGBRegressor(objective ='reg:linear', verbose=0)
        model.fit(features_train, target_train)
        
        '''prediction using test features'''
        predict_valid = model.predict(features_valid)
        
        '''lists at top of block appended with values'''
        max_lag_list.append(i)
        rolling_mean_list.append(j)
        rmse_list.append(mean_squared_error(target_valid, predict_valid)**0.5)
        
        '''reset columns in dataframe to remove make_features'''
        temp_train = temp_train[column_copy]


'''dataframe created from lists at top of block'''
mse_linear_reg = pd.DataFrame({'max_lag': max_lag_list, 'rolling_mean': rolling_mean_list,
                                    'rmse': rmse_list})

'''min value for rmse to be returned'''
print(mse_linear_reg[mse_linear_reg['rmse']==mse_linear_reg['rmse'].min()])
print(mse_linear_reg.nsmallest(20, 'rmse'))

"""### Validation predictions LR"""

temp_train = temp_train[column_copy]

make_features(temp_train, 5, 2)

'''train_test_split for data, test_size 20% of original data,
shuffle=False so data stays chronological, random_state set for repeatability'''
features_train, split_2nd = train_test_split(
  temp_train, test_size = 0.2, shuffle=False, random_state=1)

features_valid, features_test = train_test_split(
    split_2nd, test_size=0.5, shuffle=False, random_state=1
)

'''na values dropped as lag feature will generate na values'''
features_train = features_train.dropna()
features_valid = features_valid.dropna()
features_test = features_test.dropna()

'''features and target variables for train, valid, and test set'''
target_train = features_train['targetvalue']
features_train = features_train.drop(['targetvalue'], axis=1)

target_valid = features_valid['targetvalue']
features_valid = features_valid.drop(['targetvalue'], axis=1)

target_test = features_test['targetvalue']
features_test = features_test.drop(['targetvalue'], axis=1)

model = LinearRegression()
model.fit(features_train, target_train)
print('RMSE train:',mean_squared_error(target_train, model.predict(features_train))**0.5)
print('RMSE valid:',mean_squared_error(target_valid, model.predict(features_valid))**0.5)
print('RMSE test:',mean_squared_error(target_test, model.predict(features_test))**0.5)

"""### Validation predictions XGB"""

model = XGBRegressor(n_estimators=20000,max_depth=5,reg_lambda=0.9, random_state=1)

model.fit(features_train, target_train,
          early_stopping_rounds=300, eval_set=[(features_test, target_test)], verbose=False)
y_prediction = model.predict(features_test)

results=mean_absolute_error(target_test,y_prediction)
print(results)

temp_train = temp_train[column_copy]

make_features(temp_train, 3, 4)

'''train_test_split for data, test_size 20% of original data,
shuffle=False so data stays chronological, random_state set for repeatability'''
features_train, features_valid = train_test_split(
  temp_train, test_size = 0.2, shuffle=False, random_state=1)

'''na values dropped as lag feature will generate na values'''
features_train = features_train.dropna()
features_valid = features_valid.dropna()

'''features and target variables for train, valid, and test set'''
target_train = features_train['targetvalue']
features_train = features_train.drop(['targetvalue'], axis=1)

target_valid = features_valid['targetvalue']
features_valid = features_valid.drop(['targetvalue'], axis=1)

xgboost = XGBRegressor(objective='reg:squarederror', verbose=0)
xgboost.fit(features_train, target_train)
print('RMSE train:',mean_squared_error(target_train, xgboost.predict(features_train))**0.5)
print('RMSE valid:',mean_squared_error(target_valid, xgboost.predict(features_valid))**0.5)
print('R2 train=',metrics.r2_score(features_valid,predict_valid))

oe.transform(test[['county', 'province_state', 'country_region', 'target', 'Location']])
model.predict(test)

"""#ML Model <a name='ML'></a>

## XGBRegressor + Hyperopt
"""

!pip install hyperopt
!pip install hpsklearn

from hyperopt import fmin, hp, tpe, Trials, space_eval, STATUS_OK
from hyperopt.pyll.base import scope

xgbr = XGBRegressor()
xgbr.fit(X_train, y_train)
y_pred = xgbr.predict(X_test)

print('MAE:', mean_absolute_error(y_pred, y_test))
print('RMSE:', mean_squared_error(y_pred, y_test)**0.5)

def objective(search_space):
    model = XGBRegressor(
    **search_space,
    random_state=1)
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_valid)
    
    accuracy = mean_absolute_error(y_pred, y_valid)
    return {'loss': accuracy,
           'status':STATUS_OK}

           #these are the hyperparameters to tune, change to what your model includes
search_space = {
    'max_depth': scope.int(hp.quniform("max_depth", 1, 5, 1)),
    'gamma': hp.uniform ('gamma', 0,1),
    'reg_alpha' : hp.uniform('reg_alpha', 0,50),
    'reg_lambda' : hp.uniform('reg_lambda', 10,100),
    'colsample_bytree' : hp.uniform('colsample_bytree', 0,1),
    'min_child_weight' : hp.uniform('min_child_weight', 0, 5),
    'n_estimators': hp.randint('n_estimators', 200, 20000),
    'learning_rate': hp.uniform('learning_rate', 0, .15),
    'tree_method':'hist', #could use gpu_hist if available
    'gpu_id': 0,
    'max_bin' : scope.int(hp.quniform('max_bin', 200, 550, 1))
               }

algorithm = tpe.suggest

best_params = fmin(
fn=objective,
space=search_space,
algo=algorithm,
max_evals=200) #drop max_evals to lower runtime, 200 attempts at tuning

print(best_params)

params = {
    'colsample_bytree': 0.876757749200749,
          'gamma': 0.06511761363728052,
          'learning_rate': 0.009024597551563221,
          'max_bin': 523.0,
          'max_depth': 5.0,
          'min_child_weight': 3.925009587666903,
          'n_estimators': 435,
          'reg_alpha': 17.58510396534354,
          'reg_lambda': 41.20106007831344
         }

best_xgb = XGBRegressor(params=params, random_state=1)
best_xgb.fit(X_train, y_train)

y_pred = best_xgb.predict(X_test)

print('MAE:', mean_absolute_error(y_test, y_pred))
print('RMSE:', mean_squared_error(y_test, y_pred)**0.5)

"""MSE: 3.5773795607209973 <br>
RMSE: 54.37627441780612

### Polynomial Features
"""

from sklearn.preprocessing import PolynomialFeatures

poly = PolynomialFeatures(2)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

best_xgb = XGBRegressor(params=params, random_state=1)
best_xgb.fit(X_train_poly, y_train)

y_pred = best_xgb.predict(X_test_poly)

print('MSE:', mean_absolute_error(y_test, y_pred))
print('RMSE:', mean_squared_error(y_test, y_pred)**0.5)

"""### Building the Multi Layer Perception regression model"""

from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error


def model_fit(regs):
    fitted_model={}
    model_result = pd.DataFrame()
    for model_name, model in regs.items():
        model.fit(X_train,y_train)
        fitted_model.update({model_name:model})
        #y_pred = model.predict(X_test)
        model_dict = {}
        model_dict['1.Algorithm'] = model_name
        model_dict['2.RMSE_Train'] = round(mean_squared_error(y_train, model.predict(X_train), squared = False),2)
        model_dict['3.RMSE_Test'] = round(mean_squared_error(y_test, model.predict(X_test), squared = False),2)
        model_dict['4.MAE_Train'] = round(mean_absolute_error(y_train, model.predict(X_train)),2)
        model_dict['5.MAE_Test'] = round(mean_absolute_error(y_test, model.predict(X_test)),2)
        model_result = model_result.append(model_dict,ignore_index=True)
    return fitted_model, model_result

regs = {"MLPRegressor_default":MLPRegressor(random_state=1, max_iter=200)}

fitted_model, model_result = model_fit(regs)

model_result.sort_values(by=['2.RMSE_Train'],ascending=True)

"""##RandomForest"""

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
pipeline_dt = Pipeline([('scaler2' , StandardScaler()),
                        ('RandomForestRegressor: ', RandomForestRegressor())])
pipeline_dt.fit(X_train , y_train)
prediction = pipeline_dt.predict(X_test)

score = pipeline_dt.score(X_test, y_test)
print('Score: ' + str(score))
# Score: 0.9674437518275933

from sklearn import metrics
from sklearn.metrics import mean_absolute_error
print('RMSE valid:',mean_squared_error(prediction,y_test)**0.5)
val_mae = mean_absolute_error(prediction,y_test)
print('MAE valid:', val_mae)

# RMSE valid: 52.58003961388158
# MAE valid: 3.648201569128793

"""##LightGBM"""

import lightgbm as lgb
!pip install lightgbm
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from lightgbm import LGBMRegressor 
from sklearn import metrics
from sklearn.model_selection import RandomizedSearchCV

# Using Randomized Search CV for model tuning

params_grid = {
    'learning_rate': [0.004, 0.005, 0.006],
    'feature_fraction': [0.2, 0.4, 0.6, 0.8],
    'bagging_fraction': [0.2, 0.4, 0.6, 0.8],
    "max_depth": [5, 10, 15, 20],
    "num_leaves": [16, 32, 64,128],
    "max_bin": [32, 64, 100]
}

lgbm_cv = RandomizedSearchCV(estimator=lgb.LGBMRegressor(), 
                             param_distributions=params_grid, 
                             cv = 5, 
                             n_iter=100,
                             verbose=1)

lgbm_cv.fit(X_train, y_train)

print("Best model parameters: ", lgbm_cv.best_params_)
# Training model with best parameters
best_params = lgbm_cv.best_params_

params = {
    'learning_rate': best_params['learning_rate'],
    'feature_fraction': best_params['feature_fraction'],
    'bagging_fraction': best_params['bagging_fraction'],
    "max_depth": best_params['max_depth'],
    "num_leaves": best_params['num_leaves'],
    "max_bin": best_params['max_bin']
}

lgbm = lgb.LGBMRegressor(**params)

lgbm.fit(X_train, y_train)

y_pred = lgbm.predict(X_test)

print("Root Mean Squared Error: ", round(mean_squared_error(y_test, y_pred)**0.5, 2))
print("Mean Absolute Error: ", round(mean_absolute_error(y_test, y_pred), 2))
print("R2: ", round(metrics.r2_score(y_test, y_pred), 2))

"""##Linear Regression Model"""

from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X_train, y_train)
print('RMSE train:',mean_squared_error(y_train, model.predict(X_train))**0.5)
print('RMSE test:',mean_squared_error(y_test, model.predict(X_test))**0.5)
print("MAE train: ", round(mean_absolute_error(y_train, model.predict(X_train)), 2))
print("MAE test: ", round(mean_absolute_error(y_test, model.predict(X_test)), 2))
# RMSE train: 69.8476941359348
# RMSE valid: 47.65099733127677

"""## Decision Tree Regressor"""

#Feature selection by ExtraTreesRegressor(model based). 
#ExtraTreesRegressor helps us find the features which are most important.
# Feature selection by ExtraTreesRegressor(model based)

from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score as acc
from sklearn import metrics

reg= ExtraTreesRegressor()
reg.fit(X_train,y_train)

feat_importances = pd.Series(reg.feature_importances_, index=X_train.columns)
feat_importances.nlargest().plot(kind='barh')
plt.show()

from sklearn.tree import DecisionTreeRegressor
reg_decision_model=DecisionTreeRegressor()

# fit independent varaibles to the dependent variables
reg_decision_model.fit(X_train,y_train)

reg_decision_model.score(X_train,y_train)
#Score for train dataset is 0.9999

reg_decision_model.score(X_test,y_test)
#Score for test dataset is 0.8989

"""### Hyper Parameter Tuning for Decision Tree Regressor"""

prediction=reg_decision_model.predict(X_test)

# Hyper parameters range intialization for tuning 
parameters={"splitter":["best","random"],
            "max_depth" : [1,3,5,7,9,11,12],
           "min_samples_leaf":[1,2,3,4,5,6,7,8,9,10],
           "min_weight_fraction_leaf":[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9],
           "max_features":["auto","log2","sqrt",None],
           "max_leaf_nodes":[None,10,20,30,40,50,60,70,80,90] }

# calculating different regression metrics
from sklearn.model_selection import GridSearchCV
tuning_model=GridSearchCV(reg_decision_model,param_grid=parameters,scoring='neg_mean_squared_error',cv=3,verbose=3)

tuning_model.fit(X_train,y_train)

# best hyperparameters 
tuning_model.best_params_

# best model score
tuning_model.best_score_

"""###Training Decision Tree With Best Hyperparameters

"""

tuned_hyper_model= DecisionTreeRegressor(max_depth=5,max_features='auto',max_leaf_nodes=50,min_samples_leaf=2,min_weight_fraction_leaf=0.1,splitter='random')

# fitting model
tuned_hyper_model.fit(X_train,y_train)

tuned_pred=tuned_hyper_model.predict(X_test) # Tuned prediction

# With hyperparameter tuned 

from sklearn import metrics
print('MAE:', metrics.mean_absolute_error(y_test,tuned_pred))
print('MSE:', metrics.mean_squared_error(y_test, tuned_pred))
print('RMSE:', np.sqrt(metrics.mean_squared_error(y_test, tuned_pred)))

reg_decision_model.score(X_test,tuned_pred)

# without hyperparameter tuning 
print('MAE:', metrics.mean_absolute_error(y_test,prediction))
print('MSE:', metrics.mean_squared_error(y_test, prediction))
print('RMSE:', np.sqrt(metrics.mean_squared_error(y_test, prediction)))

"""##Gradient boost"""

gradientregressor=GradientBoostingRegressor(max_depth=2,n_estimators=50,learning_rate=1.0)

model=gradientregressor.fit(X_train,y_train)
y_pred=model.predict(X_test)

from sklearn.metrics import r2_score
r2_score(y_pred,y_test)

y_pred

from sklearn.metrics import mean_absolute_error,mean_squared_error

mae_model=mean_absolute_error(y_test,y_pred)

mse_model=mean_squared_error(y_test,y_pred)

print(f"mae_model:{mae_model} ")
print(f"mse_model: {mse_model}")

from sklearn.metrics import mean_squared_error
from math import sqrt

print('root mean square value :' ,sqrt(mean_squared_error(y_test,y_pred)))

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
# %matplotlib inline

from sklearn.ensemble import GradientBoostingClassifier

features=model.feature_importances_
features

X_train.columns

columns=X_train.columns

graph=pd.Series(features,columns)
graph

import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

figure(figsize=(10,10))
graph.sort_values().plot.barh(color='red')
