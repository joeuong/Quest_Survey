from datetime import date
from dotenv import load_dotenv
import os
import pandas as pd
import glob
import random
pd.options.mode.chained_assignment = None

## todo URSP: first dibs at everything (honors or not honors)
## todo Honors: if they picked Hons course, then they get that randomly first. Else, they get put in general pop

## Prep files, variables, and lists for the lopp
thedate = date.today()
load_dotenv()
filedir = os.getenv('PWD')
path = rf'{filedir}\source_files\*.xlsx'
xlsx_files = glob.glob(path)

cancelled_courses_file = rf'{filedir}\source_files\cancelled_courses.txt'
with open(cancelled_courses_file, 'r') as file:
    cancelled_course_list = [line.strip() for line in file.readlines()]

for filename in xlsx_files:
    term = os.path.basename(filename)
    ## Read data into Pandas DataFrame
    print(rf'Reading file into Pandas for {term}...')
    survey_orig = pd.read_excel(filename,sheet_name='data',header=0)
    capacity_orig = pd.read_excel(filename,sheet_name='summary',header=0)
    class_cap_orig = pd.read_excel(filename,sheet_name='detail',header=0)
    df_capacity = capacity_orig.sort_values(by='CAPACITY')

    # Exclude specific 'Course Offering SFID' from survey_orig
    survey_orig = survey_orig[~survey_orig['Course Offering SFID 18'].isin(cancelled_course_list)]

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
        df_assigned = pd.DataFrame(columns=['UFID','Stu Name','Course Offering SFID 18','Topic','Class Number','RandomDigit'])
        
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
                criteria = row['Course Offering SFID 18']

        ## Find the first student who selected that course (it will be some sort of random numbers generated before)
                try:
                    first_matching_row = df_ready.loc[df_ready['Course Offering SFID 18'] == criteria].iloc[0]
        ## Put the data into a new row and set as a DF 
                    new_row = {'UFID': first_matching_row['UFID'], 'Stu Name': first_matching_row['Full Name'], 'Course Offering SFID 18': first_matching_row['Course Offering SFID 18'], 'Topic': first_matching_row['Topic'], 'RandomDigit': first_matching_row['RandomDigit']}
                except:
                    new_row = {'UFID': r'DROP', 'Course Offering SFID 18': criteria}
                new_row_df = pd.DataFrame([new_row])
        ## Append the new row to the current DataFrame
                df_assigned = pd.concat([df_assigned, new_row_df], ignore_index=True)
        ## Drop all rows for the UFID previously used
                df_ready = df_ready[df_ready['UFID'] != first_matching_row['UFID']]
        
        ## Sort newly finished df_assigned by the course. This gets it ready to have the Class Numbers added
        df_assigned_sorted = df_assigned.sort_values(by='Course Offering SFID 18')
        ## Sort class_cap by the same field (placeholder rows will still be there)
        df_class_cap_all = class_cap_orig.sort_values(by='Course Offering SFID 18')

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
        writer = pd.ExcelWriter(rf'{filedir}\output_files\{thedate}_{term}_Quest_Results_Version_{len(df_assigned_sorted)}_{i}.xlsx', engine='xlsxwriter')
        df_assigned_sorted.to_excel(writer, sheet_name='assigned')
        df_ready.to_excel(writer, sheet_name='unassigned')
        class_cap_orig.to_excel(writer, sheet_name='class_cap')
        writer.close()
        print(f'Completed Option {i} with {len(df_assigned_sorted)} rows')

    print(rf'Finished with {term}')