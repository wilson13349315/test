import pandas as pd

#1
df = pd.DataFrame()
df.loc[df['Value']>100]

# List1
lst = [['Geek', 25], ['is', 30],
       ['for', 26], ['Geeksforgeeks', 22]]

df = pd.DataFrame.from_records(lst)
df = pd.DataFrame(lst,columns=['Tag','Num'])

dict ={'Name': 'Geek1', 'Age': 26, 'Occupation': 'Scientist'},\
    {'Name': 'Geek2', 'Age': 31, 'Occupation': 'Researcher'},\
    {'Name': 'Geek3', 'Age': 24, 'Occupation': 'Engineer'}

df = pd.DataFrame.from_dict(dict)

# Zip function
'''
1) return a iterator
2) stop at the shortest iterable
3) handle multiple iterables
'''

# parallel iteration in a for loop -> similar to enumerate
# difference: zip returns the tuples of the object with limit while enumerate return index and value
# enumerate -> Returns an iterator with index and element pairs from the original iterable
names = ['Alice', 'Bob', 'Charlie']
ages = [25, 30, 35]
cities = ['New York', 'Los Angeles', 'Chicago']

for name,age,city in zip(names,ages,cities):
    print(f'{name} is {age} and living in {city}')

#enumerate(iterable, start=0)
for idx, (name, age, city) in enumerate(zip(names, ages, cities)):
    print(f'{idx}: {name} is {age} and living in {city}')


names = ['John', 'Jane', 'Tom']
cities = ['London', 'Paris', 'Berlin']

for name, city in zip(names,cities):
    print(name,city)

for idx, name in enumerate(names):
    print(idx,name)

# use Zip to merge dfs from lists
names = ['Alice', 'Bob', 'Charlie']
ages = [25, 30, 35]
cities = ['London', 'Paris', 'Berlin']

for name,age,city in zip(names,ages,cities):
    df = pd.DataFrame(zip(names,ages,cities),columns = ['name','age','city'])

# find out element started with A and its index
items = ['Apple', 'Banana', 'Avocado', 'Mango']
for idx,item in enumerate(items):
    if item.startswith('A'):
        print(idx,item)

# zip to dict
students = ['Anna', 'Ben', 'Chris']
scores = [[85, 90], [78, 82], [92, 88]]

student_scores = dict(zip(students, scores))

students = ['Amy', 'Ben']
scores = [90, 85]

for idx,(student,score) in enumerate(zip(students,scores)):
    print(idx,student,score)

a = [1, 2, 3, 4]
b = [1, 2, 0, 4]

for idx,(x,y) in enumerate(zip(a,b)):
    if x!=y:
        print(idx,x,y)

matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
transposed = list(zip(*matrix))


#(a, b, c) → tuple：order, duplicate, indexible, immutable (but can include mutable element like list, list can be mutable)
#{a, b, c} → set：no order, no duplicate, non-indexible, mutable

# find out whether duplicate in a list
some_list = ['a', 'b', 'c', 'b', 'd', 'm', 'n', 'n']
duplicate = set(x for x in some_list if some_list.count(x)>1)

# find out intersection/difference of two sets

valid = set(['yellow', 'red', 'blue', 'green', 'black'])
input_set = set(['red', 'brown'])
print(input_set.intersection(valid))
print(input_set.difference(valid))

'''
int, float, bool, str, list, dict, set, tuple, range,
'''

a = ['Geeks', 'for', 'Geeks']

# Creating an enumerate object from the list 'a'
b = enumerate(a)

# Handle wrong data type for one column
df['Age'] = pd.to_numeric(df['Age'],errors='coerce')

# Create df with tuples
data = [('ANSH', 22, 9),
        ('SAHIL', 22, 6),
        ('JAYAN', 23, 8),
        ('AYUSHI', 21, 7),
        ('SPARSH', 20, 8) ]

df = pd.DataFrame(data,columns=['Team','Age','Score'])

# json_normalize() to hanlde json data in a list or nested list
data = [{'Geeks': 'dataframe', 'For': 'using', 'geeks': 'list'},{'Geeks':10, 'For': 20, 'geeks': 30}]

df=pd.json_normalize(data)
print(df)

# nested dict data
countries = {
    "1": {"Country": "New Country 1",
          "Capital": "New Capital 1",
          "Population": "123,456,789"},
    "2": {"Country": "New Country 2",
          "Capital": "New Capital 2",
          "Population": "987,654,321"},
    "3": {"Country": "New Country 3",
          "Capital": "New Capital 3",
          "Population": "111,222,333"}
}

df = pd.DataFrame.from_dict(countries,orient='index')

list = [{
        "Student": [{"Exam": 90, "Grade": "a"},
                    {"Exam": 99, "Grade": "b"},
                    {"Exam": 97, "Grade": "c"},
                    ],
        "Name": "Paras Jain"
        },
        {
        "Student": [{"Exam": 89, "Grade": "a"},
                    {"Exam": 80, "Grade": "b"}
                    ],
        "Name": "Chunky Pandey"
        }
        ]

rows = []

for data in list:
    data_row = data['Student']
    time = data['Name']

    for row in data_row:
        row['Name'] = time
        rows.append(row)

df = pd.DataFrame(rows)

student = {"Exam": 90, "Grade": "a"}
# ** student will unpack into Exam=90, Grade='a' -> flattening

import pandas as pd

data = [
    {
        "Student": [{"Exam": 90, "Grade": "a"},
                    {"Exam": 99, "Grade": "b"},
                    {"Exam": 97, "Grade": "c"}],
        "Name": "Paras Jain"
    },
    {
        "Student": [{"Exam": 89, "Grade": "a"},
                    {"Exam": 80, "Grade": "b"}],
        "Name": "Chunky Pandey"
    }
]

# Flatten the nested data
rows = [
    {**student, "Name": record["Name"]}
    for record in data
    for student in record["Student"]
]

df = pd.DataFrame(rows)


'''
List comprehension: [expression for x in iterable object], squares = [x**2 for x in range(5)]
- filtering
- mapping
- flattening nested structure
- transform data into new formats
'''
squares = [x**2 for x in range(5)]
print(squares)

df = df.pivot_table(index='Name', columns=['Grade'],
                    values=['Exam']).reset_index()

df.columns = ['Name', 'Maths', 'Physics', 'Chemistry']

# Create the dataframe
df = pd.DataFrame({'Date':['10/2/2011', '11/2/2011', '12/2/2011', '13/2/2011'],
                   'Product':[' UMbreLla', '  maTtress', 'BaDmintoN ', 'Shuttle'],
                   'Updated_Price':[1250, 1450, 1550, 400],
                   'Discount':[10, 8, 15, 10]})

# Print the dataframe
print(df)

df['Product'] = df['Product'].str.strip().str.capitalize()


# *args and **kwargs usage

def test_func(*args, **kwargs):
    print(args)
    print(kwargs)

'''
*args: support most used 6 data types in pyton: numbers, list, str, set,tuple, dict -> positional arugments
**kwargs: only support two kinds of data type: 1) key=value,eg: age = 20; 2) unpacked dict: **dict
'''

s = "mm"
l = [2,3]
t = (3,2)
d = {"name":"li", "age":20}

test_func(d)

#d为字典，没加**，会当成是传给*args的元素
test_func(s,l,t)
test_func(**d)

def func(f_arg:str,*argv:str) -> str:
    print(f_arg+'is the first argument')

    for arg in argv:
        print(arg+ 'are the rest')

func('yasoob', 'python', 'eggs', 'test')

def greet_me(**kwargs):
    for key, value in kwargs.items():
        print("{0} = {1}".format(key, value))

greet_me(name="yasoob")


def test_args_kwargs(arg1, arg2, arg3):
    print("arg1:", arg1)
    print("arg2:", arg2)
    print("arg3:", arg3)

args = ("two", 3, 5) # this is a tuple -> positional, use * to unpack tuple

kwargs = {"arg3": 3, "arg2": "two", "arg1": 5} # This is a dict (Key-Value), use ** to unpack dict

# one more example - logging
def log_event(event_type:str,*args,**kwargs):
    print(event_type)

    for i, arg in enumerate(args):
        print(i,arg)

    for key,value in kwargs.items():
        print(key,value)

log_event("LOGIN", "user1", "success")

log_event("UPLOAD", filename="report.pdf", user="user2", size="2MB")

log_event("DELETE", "file.txt", user="admin", reason="expired")



# use dict to replace if else logic
def do_open(): print("Open")
def do_close(): print("Close")
def do_default(): print("Default")

actions = {
    "open": do_open,
    "closed": do_close,
}

actions.get('open')

initial_data = {'First_name': ['Ram', 'Mohan', 'Tina', 'Jeetu', 'Meera'],
        'Last_name': ['Kumar', 'Sharma', 'Ali', 'Gandhi', 'Kumari'],
        'Age': [42, 52, 36, 21, 23],
        'City': ['Mumbai', 'Noida', 'Pune', 'Delhi', 'Bihar']}

df = pd.DataFrame(initial_data, columns = ['First_name', 'Last_name',
                                                    'Age', 'City'])

new_data = { "Ram":"B.Com",
            "Mohan":"IAS",
            "Tina":"LLB",
            "Jeetu":"B.Tech",
            "Meera":"MBBS" }

df["Qualification"] = df["First_name"].map(new_data) # map -> key-value object

# Reshape the dataset: multi-index objects / stack(),unstack(), melt()
df = pd.read_csv("https://media.geeksforgeeks.org/wp-content/uploads/nba.csv")
df_stacked = df.stack()

df_melt = df.melt(id_vars=['Name','Team'])

'''
Change column names and row indexes in Pandas DataFrame
df.rename()
list comprehension
'''
df = pd.DataFrame({
    "A": ['Tom', 'Nick', 'John', 'Peter'],
    "B": [15, 26, 17, 28]
})
res = df.rename(columns={"A": "Col_1", "B": "Col_2"},
                index={0: "Row_1", 1: "Row_2", 2: "Row_3", 3: "Row_4"})
print(res)

res.columns = [x + "_new" if '2' in x else x for x in res.columns]

# iterate rows in pandas when calculation is needed -> vectorized operations. np.where() for dataframe dataset
# methods: iterrows(), itertuples(),apply() a func with calculation logic, index_based (iloc, loc)

import numpy as np

data = {'Item': ['Apple', 'Banana', 'Orange'],'Quantity': [10, 20, 30],'Price': [0.5, 0.3, 0.7]}
df = pd.DataFrame(data)

for idx, row in df.iterrows():
    total_sales = row['Quantity'] * row['Price']

for row in df.itertuples():
    total_sales = row.Quantity * row.Price


# select rows based on condition: ~df.loc, isin()

# drop rows: drop(), loc(),indexing condition

df_filtered = df[df['B']>10]

# Vectorized operations
df['Result'] = np.where(df['C'] == 'X', df['A'] * df['B'], df['A'] + df['B'])

# drop
df.drop(columns=['Item'])

dict1 = {'Driver': ['Hamilton', 'Vettel', 'Raikkonen',
                    'Verstappen', 'Bottas', 'Ricciardo',
                    'Hulkenberg', 'Perez', 'Magnussen',
                    'Sainz', 'Alonso', 'Ocon', 'Leclerc',
                    'Grosjean', 'Gasly', 'Vandoorne',
                    'Ericsson', 'Stroll', 'Hartley', 'Sirotkin'],

         'Points': [408, 320, 251, 249, 247, 170, 69, 62, 56,
                    53, 50, 49, 39, 37, 29, 12, 9, 6, 4, 1],

         'Age': [33, 31, 39, 21, 29, 29, 31, 28, 26, 24, 37,
                 22, 21, 32, 22, 26, 28, 20, 29, 23]}

# creating dataframe using DataFrame constructor
df = pd.DataFrame(dict1)
print(df.head(10))

df_filtered = df.loc[df['Points']==df['Points'].max()]


# Create a new column based on condition
# list comprehension
# apply(), map(),np.where(), np.select(),.loc, lambda func



raw_Data = {
    'Voter_name': ['Geek1', 'Geek2', 'Geek3', 'Geek4', 'Geek5', 'Geek6', 'Geek7', 'Geek8'],
    'Voter_age': [15, 23, 25, 9, 67, 54, 42, np.NaN]
}

df = pd.DataFrame(raw_Data)
conditions = [
    df['Voter_age'] >= 18,
    df['Voter_age'] < 18
]
choices = ['Yes', 'No'] # fit for three different cases

# Apply logic
df['Voter'] = np.select(conditions, choices, default='Not Sure')
df['Adult'] = df['Voter_age'].apply(lambda x: x - 18 if x >= 18 else np.nan)

#
data = {
    "name": ["John", "Ted", "Dev", "Brad", "Rex", "Smith", "Samuel", "David"],
    "salary": [10000, 20000, 50000, 45500, 19800, 95000, 5000, 50000]
}

df = pd.DataFrame(data)

conditions = [
    df['salary'] < 10000,
    (df['salary'] >= 10000) & (df['salary'] < 25000),
    df['salary'] >= 25000
]

results = ['Low', 'Medium', 'High']

df['income'] = np.select(conditions, results,default='Unknown')

# Split column
df = pd.DataFrame({'Geek_ID':['Geek1_id', 'Geek2_id', 'Geek3_id',
                                         'Geek4_id', 'Geek5_id'],
                'Geek_A': [1, 1, 3, 2, 4],
                'Geek_B': [1, 2, 3, 4, 6],
                'Geek_R': np.random.randn(5)})
df['new_col'] = df['Geek_ID'].str.split('_')


df = pd.DataFrame({
    'name': ['A', 'B', 'C'],
    'score': [88, 95, 90]
})

# Get the index of the max value of a column
max_index = df['score'].idxmax()

# Get n largest value
df.sort_values(by=['score']).nlargest(2,['score'])

# Time-series pandas
import pandas as pd
import numpy as np

# range_date
rd = pd.date_range(start ='1/1/2019', end ='1/08/2019', freq ='Min')
df = pd.DataFrame(rd, columns =['date'])
df['data'] = np.random.randint(0, 100, size =(len(rd)))

# once date (time) is set as index, then we can do several resampling cals
df = df.set_index(df['date'])
df_daily = df.resample('D').mean(numeric_only=True)

def cal(year: int, customer: str) -> pd.DataFrame:
    data = {'Year': [year], 'Customer': [customer]}
    return pd.DataFrame(data)

"""
*args and **kwargs

*args -> non-keyworded variable
**kwargs ->
"""

def test_var_args(f_arg, *argv):
    print("first normal arg:", f_arg)
    for arg in argv:
        print("another arg through *argv:", arg)

test_var_args('yasoob', 'python', 'eggs', 'test')


'''
Time-series practice
'''

import pandas as pd
import numpy as np
df = pd.date_range('2022-01-01','2024-01-01',freq='h')
df = pd.DataFrame(df,columns=['date'])
df['value'] = np.random.rand(len(df))
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['week'] = df['date'].dt.day
df['weekday'] = df['date'].dt.weekday
df = df.set_index('date')

# sum
df.resample('YS').agg({'value':'sum'})

df_filtered = df.loc[(df.year==2023) & (df.month==5)]
df_new = df.loc[(df.index>='2022-01-01') & (df.index<='2022-10-01')]
df_new = df_new.resample('MS').agg({'value': 'sum'})

df_daily = df.resample('D').agg({'value':'sum'})
df_daily_shift = df_daily.shift(7)

df_reset = df.reset_index(drop=False)
df_reset['MonthEnd'] = np.where(df_reset['date'].dt.is_month_end, 1, 0)

# resample and calcuate, to create new columns.
df_monthly = df.resample('MS').agg(value_sum=('value', 'sum'), value_mean=('value', 'mean'))
df_weekly = df.resample('W').agg({'value':'mean'})

df_weekly_rolling = df_daily.rolling(7).agg({'value':'mean'})

df_quarterly = df.resample('QS').agg({'value':'sum'})
df_quarterly['YoY'] = df_quarterly['value'].diff(4)

# use diff(), pct_change() to calculate changes
# resample to monthly / quarterly / yearly first
# calculate changes by using diff()
# .agg({'col1': 'sum', 'col2': 'mean'}) — multiple aggregation by column

df_dedup = df.groupby(pd.Grouper(key='timestamp', freq='T')).first().reset_index()

# this time-series is not complete
dates = pd.to_datetime(['2024-08-01', '2024-08-03', '2024-08-06'])
data = [10, 20, 15]
df = pd.DataFrame({'value': data}, index=dates)

# fill the all time-series
df_full = df.asfreq('D')
df_full = df_full.fillna(0)

"""
Decorators
- returning function within functions
- giving function as an argument to another function
"""

def hi(name="yasoob"):
    def greet():
        return "now you are in the greet() function"

    def welcome():
        return "now you are in the welcome() function"

    if name == "yasoob":
        return greet
    else:
        return welcome

a = hi()
print(a())

def checkall(func):
    def wrapper(*args,**kwargs):
        if type(args[0])==type(0) and type(args[1])==type(0):
            return func(*args,**kwargs)
        else:
            print('Type must be number!')
            return None
    return wrapper

@checkall
def plus(a,b):
    return a+b

plus(1,2)

from functools import wraps

def logit(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        print(func.__name__ + " was called")
        return func(*args, **kwargs)
    return with_logging

@logit
def addition_func(x):
   """Do some math."""
   return x + x


print(addition_func(4))

# Decorator

import time

def timer(f):
    def wrapper(*args,**kwargs):
        start_time = time.time()
        result = f(*args,**kwargs)
        end_time = time.time()
        print(f"How much time spent {end_time-start_time}")

        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)

slow_function()

'''
Collections - module: deafultdict, ordereddict,counter,deque,namedtuple
'''
from collections import defaultdict
colours = (
    ('Yasoob', 'Yellow'),
    ('Ali', 'Blue'),
    ('Arham', 'Green'),
    ('Ali', 'Black'),
    ('Yasoob', 'Red'),
    ('Ahmed', 'Silver'),
)

favourite_colours = defaultdict(list)

for name, colour in colours:
    favourite_colours[name].append(colour)

# Counter - fast count element
from collections import Counter

test_list = ['a', 'b', 'a', 'c', 'a', 'b']
print(Counter(test_list))

"""
Class - instance, class variables

Use class variables for things all instances share (e.g. constants).

Use instance variables for unique data per object (e.g. name, radius, etc.).

self.var lets you access both — first instance → then class (fallback).
"""

class Cal():
    pi = 3.142

    def __init__(self, radius):
        self.radius = radius

    def cal_area(self):
        return self.pi * (self.radius ** 2)

a = Cal(2)
print(a.cal_area())  # Example usage

a_list = [[1, 2], [3, 4], [5, 6]]
flat = [item for sublist in a_list for item in sublist]

