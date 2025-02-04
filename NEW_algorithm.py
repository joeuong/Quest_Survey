## Run one for summer and one for Fall
## Need an Excel file with these sheets:
## Sheet1: Needs 'UFID', 'Course Offering SFID', and 'Topic'
## Sheet2: Needs 'Course Offering SFID' and 'CAPACITY' (Sum of all sections of the course)
## Sheet3: Needs 'Course Offering SFID' 'Topic' 'CN' 'C_CAPACITY'
## additional tasks: 
##	removed summer students who were moved to fall (checked for Summer Term Activation
##  removed students from both terms who did not have a term activation in either semester
##  Rename the CSV file
##  CSV Structure should be: 
##  Need to add Student Groups in beforehand
##  Watch out for UFO students

import pandas as pd
from datetime import date
import random
pd.options.mode.chained_assignment = None

## Getting the Date to print in the filename
thedate = date.today()

## Establishing directories and files
filename = r'C:\Users\juong42\OneDrive - University of Florida\Uong-AAC-Data_Requests\Quest\Algorithm 2024\Test Files\Summer_2024_Test.xlsx'
# filename = r'C:\Users\juong42\OneDrive - University of Florida\Uong-AAC-Data_Requests\Quest\Algorithm 2024\Test Files\Fall_2024_Test.xlsx'

## Read data into Pandas DataFrame
print('Reading file into Pandas...')
survey_orig = pd.read_excel(filename,sheet_name='Sheet1',header=0)
capacity_orig = pd.read_excel(filename,sheet_name='Sheet2',header=0)
class_cap_orig = pd.read_excel(filename,sheet_name='Sheet3',header=0)
df_capacity = capacity_orig.sort_values(by='CAPACITY')

# Exclude specific 'Course Offering SFID' from survey_orig
cancelled_course_list = ['a044X00000dt0gX','a044X00000dt0gK','a044X00000dt0gXQAQ','a044X00000dt0gKQAQ']  # Update this list as needed
survey_orig = survey_orig[~survey_orig['Course Offering SFID'].isin(cancelled_course_list)]

for i in range(10):
    print(f'Starting Option {i}')

    ## Assigning Random digits to the last column and then sorting by that column
    print('Assigning random numbers...')
    df = survey_orig
    
    random_digits = [random.randint(100000, 999999) for _ in range(len(df))]
    df['RandomDigit'] = random_digits
    
    ## This DF is ready to be used to find courses
    df_ready = df.sort_values(by='RandomDigit')
    
    ## DF empty at this time
    df_assigned = pd.DataFrame(columns=['UFID','Stu Name','Course Offering SFID','Topic','Class Number','RandomDigit'])
    
    print('Starting FOR Loop...')
    for index, row in df_capacity.iterrows():
    ## Get the capacity of each course
        number_of_students = row['CAPACITY'] 
    ## Get the number of students already in the class 
        iterator = 0

    ## Try statement because some courses do not have enough students selecting
    ## In that case, the script adds a blank placeholder and moves on 
        while iterator < number_of_students: 
            iterator += 1
    ## Get the course Salesforce ID
            criteria = row['Course Offering SFID']

    ## Find the first student who selected that course (it will be some sort of random numbers generated before)
            try:
                first_matching_row = df_ready.loc[df_ready['Course Offering SFID'] == criteria].iloc[0]
    ## Put the data into a new row and set as a DF 
                new_row = {'UFID': first_matching_row['UFID'], 'Stu Name': first_matching_row['Full Name'], 'Course Offering SFID': first_matching_row['Course Offering SFID'], 'Topic': first_matching_row['Topic'], 'RandomDigit': first_matching_row['RandomDigit']}
            except:
                new_row = {'UFID': r'DROP', 'Course Offering SFID': criteria}
            new_row_df = pd.DataFrame([new_row])
    ## Append the new row to the current DataFrame
            df_assigned = pd.concat([df_assigned, new_row_df], ignore_index=True)
    ## Drop all rows for the UFID previously used
            df_ready = df_ready[df_ready['UFID'] != first_matching_row['UFID']]
    
    ## Sort newly finished df_assigned by the course. This gets it ready to have the Class Numbers added
    df_assigned_sorted = df_assigned.sort_values(by='Course Offering SFID')
    ## Sort class_cap by the same field (placeholder rows will still be there)
    df_class_cap_all = class_cap_orig.sort_values(by='Course Offering SFID')

    ## Create an empty list to hold the repeated Class Number values
    repeated_CNs = []

    ## Iterate through each row of the dataframe and extend the list
    for _, row in df_class_cap_all.iterrows():
        repeated_CNs.extend([row['CN']] * row['C_CAPACITY'])

    ## Add the repeated Class Number DF into the main DF to print
    df_assigned_sorted['Class Number'] = repeated_CNs

    ## Remove all placeholder rows
    df_assigned_sorted.drop( df_assigned_sorted[ df_assigned_sorted['UFID'].astype(str) == str(r'DROP') ].index, inplace=True)

    print('Writing to Excel...')
    writer = pd.ExcelWriter(rf'C:\Users\juong42\OneDrive - University of Florida\Uong-AAC-Data_Requests\Quest\Algorithm 2024\2024_Run\{thedate}_Summer_Quest_Results_Version_{len(df_assigned_sorted)}_{i}.xlsx', engine='xlsxwriter')
    # writer = pd.ExcelWriter(rf'C:\Users\juong42\OneDrive - University of Florida\Uong-AAC-Data_Requests\Quest\Algorithm 2024\2024_Run\{thedate}_Fall_Quest_Results_Version_{len(df_assigned_sorted)}_{i}.xlsx', engine='xlsxwriter')
    df_assigned_sorted.to_excel(writer, sheet_name='assigned')
    df_ready.to_excel(writer, sheet_name='unassigned')
    class_cap_orig.to_excel(writer, sheet_name='class_cap')
    writer.close()
    print(f'Completed Option {i} with {len(df_assigned_sorted)} rows')

print('Finished')