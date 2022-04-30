"""
##############################################################################
#######               PROJECT NAME : CO2 EMISSIONS WITH GUI            #######
##############################################################################
                                Synopsis:
GUI program, which read co2 csv file, validates it and allow user choose fossil fuel and country to plot charts.
"""

## import necessary libraries
from tkinter import *
from tkinter import ttk
import pandas as pd
import numpy as np
from pandas_schema import Column, Schema
from pandas_schema.validation import CustomElementValidation
from matplotlib import pyplot as plt


### read csv file and filter columns of interest
data = pd.read_csv('fossil-fuel-co2-emissions-by-nation_csv.csv', usecols=['Country', 'Total', 'Solid Fuel', 'Liquid Fuel', 'Gas Fuel',
       'Cement', 'Gas Flaring', 'Year'])

### Custom number check function
def int_check(num):
            try:
                int(num)
            except ValueError:
                return False
            return True

### Prepare validation for Schema
int_validation = [CustomElementValidation(lambda i: int_check(i),'is not integer value')]
null_validation = [CustomElementValidation(lambda a: a is not np.nan, 'cannot be empty')]

### Schema for pandas_schema validation
schema = Schema([
Column('Country', null_validation),
Column('Total',null_validation+int_validation),
Column('Solid Fuel',null_validation+int_validation),
Column('Liquid Fuel',null_validation+int_validation),
Column('Gas Fuel',null_validation+int_validation),
Column('Cement',null_validation+int_validation),
Column('Gas Flaring',null_validation+int_validation),
Column('Year',null_validation+int_validation)
])

### Validation with pandas_schema based on specified schema above
errors = schema.validate(data)


if not errors:
#### If no errors assing default values
    error_perc = 0
    error_count = 0
else:
#### Isolate validated data from invalid
    errors_index_rows = [e.row for e in errors]
    error_df = pd.DataFrame({'Errors':errors})
    error_count = error_df.shape[0]
    error_perc = round((error_count/data.shape[0]) * 100, 2)
    data = data.drop(index=errors_index_rows)

#### Specify two dataframes, first dataframe as sum of all values
data_total = data[['Country', 'Total', 'Solid Fuel', 'Liquid Fuel', 'Gas Fuel',
       'Cement', 'Gas Flaring']].groupby('Country').sum()

### Second dataframe grouped by specific countries     
data_groups = data.groupby('Country')

### Plot function
def plot():
### Retrieve variables
    country = choice1.get()
    pollutant = choice2.get()

    ### Define style of plot
    plt.style.use('fivethirtyeight')

    if country == 'Top 10':
        if pollutant == 'All':
            data_total.sort_values('Total', ascending=False)[:10].plot(kind='barh', figsize=(35,15)).invert_yaxis()
            ## Define title
            plt.title('Top 10 Carbon Polluters')
        else:
            plt.figure(figsize=(35,15))
            d = data_total.sort_values(f'{pollutant}', ascending=False)[:10]
            plt.barh(d.index, d[f'{pollutant}'])        
            plt.gca().invert_yaxis()   
            ## Define title
            plt.title(f'Top 10 Carbon Polluters with {pollutant}')   
        ### Scale plot on x axis
        plt.xscale('log')
        ### Rotate and align ticks on y axis
        plt.yticks(rotation=40, ha='right')
        #### x axis label
        plt.xlabel('Million metric tons of carbon')  
    else:
        if pollutant != 'All':
            plt.figure(figsize=(35,15))
            d = data_groups.get_group(f'{country}')
            plt.plot(d['Year'], d[f'{pollutant}'])
            plt.title(f"{country}'s carbon emission with {pollutant}")
            plt.ylabel(f'Million metric tons of carbon')
        else:
            ### Prepare grouped dataframe, drop 'Country' column, and set 'Year' as index
            d = data_groups.get_group(f'{country}').drop('Country', axis=1).set_index('Year')
            ### Plot
            d.plot(figsize=(35,15))
            ## Define title
            plt.title(f"{country}'s carbon emissions")
            ### Scale plot on y axis
            plt.yscale('log')
            plt.ylabel('Million metric tons of carbon')
    ### Print legend on plot
    plt.legend()
    ### Fit plots within your figure cleanly
    plt.tight_layout()
    ### Plot bar chart
    plt.show()     


### Tkinter class
app = Tk()
### App title
app.wm_title('Plots')


### Dropdown variables
optionList=list(data.groupby('Country').groups.keys())
optionList.insert(0, 'Top 10')
optionList2 = list(data.columns)
optionList2.remove('Year')
optionList2.remove('Country')
optionList2.insert(0, 'All')


### Define starting variables
choice1 = StringVar()
choice1.set(optionList[0])
choice2 = StringVar()
choice2.set(optionList2[0])



### Setting labels
l1 = ttk.Label(app, text='Country')
l1.grid(row=0, column=0)
l2 = ttk.Label(app, text='Pollutant')
l2.grid(row=0, column=3, columnspan=3)
l3 = ttk.Label(app,text=f'{error_perc}% errors found \n {error_count} rows affected')
l3.grid(row=4, column=5)


### Setting Dropdowns
drop1 = ttk.Combobox(app, textvariable=choice1)
drop1.grid(row=1, column=0)
drop1['values']=optionList
drop2 = ttk.Combobox(app, textvariable=choice2)
drop2.grid(row=1, column=3, columnspan=3)
drop2['values']=optionList2


### Setting Button
b1 = ttk.Button(app, text='Plot!', command=plot)
b1.grid(row=3, column=2)

app.mainloop()