from datetime import date
from dotenv import load_dotenv
import os
import pandas as pd
import glob
import random
pd.options.mode.chained_assignment = None

## Load environment variables
load_dotenv()
filedir = os.getenv('PWD')
path = rf'{filedir}\source_files\*.xlsx'
xlsx_files = glob.glob(path)

thedate = date.today()

## Load cancelled courses
cancelled_courses_file = rf'{filedir}\source_files\cancelled_courses.txt'
with open(cancelled_courses_file, 'r') as file:
    cancelled_course_list = [line.strip() for line in file.readlines()]

for filename in xlsx_files:
    term = os.path.splitext(os.path.basename(filename))[0]
    print(rf'Reading file into Pandas for {term}...')
    survey_orig = pd.read_excel(filename, sheet_name='data', header=0)
    df_capacity = pd.read_excel(filename, sheet_name='summary', header=0)
    class_cap_orig = pd.read_excel(filename, sheet_name='detail', header=0)
    # df_capacity = capacity_orig.sort_values(by='CAPACITY')

    # Exclude cancelled courses
    survey_orig = survey_orig[~survey_orig['Course Offering Id 18'].isin(cancelled_course_list)]

    # Extract students based on flags
    ursp_students = survey_orig[survey_orig['URSP'] == 1]
    honors_students_honors_courses = survey_orig[(survey_orig['Honors'] == 1) & (survey_orig['Honors Course'] == 1) & (survey_orig['URSP'] != 1)]
    honors_students_general_courses = survey_orig[(survey_orig['Honors'] == 1) & (survey_orig['Honors Course'] != 1) & (survey_orig['URSP'] != 1)]
    general_students = survey_orig[(survey_orig['Honors'] != 1) & (survey_orig['URSP'] != 1) & (survey_orig['Honors Course'] != 1)]

    for i in range(1):
        print(f'Starting Option {i}')
        print('Assigning random numbers...')
        
        # Assign random numbers
        ursp_students['RandomDigit'] = [random.randint(100000, 999999) for _ in range(len(ursp_students))]
        honors_students_honors_courses['RandomDigit'] = [random.randint(100000, 999999) for _ in range(len(honors_students_honors_courses))]
        honors_students_general_courses['RandomDigit'] = [random.randint(100000, 999999) for _ in range(len(honors_students_general_courses))]
        general_students['RandomDigit'] = [random.randint(100000, 999999) for _ in range(len(general_students))]

        # Shuffle and sort each group
        ursp_students = ursp_students.sample(frac=1).sort_values(by='RandomDigit')
        honors_students_honors_courses = honors_students_honors_courses.sample(frac=1).sort_values(by='RandomDigit')
        honors_students_general_courses = honors_students_general_courses.sample(frac=1).sort_values(by='RandomDigit')
        general_students = general_students.sample(frac=1).sort_values(by='RandomDigit')

        # Concatenate in priority order
        df_ready = pd.concat([
            ursp_students,  # URSP students go first
            honors_students_honors_courses,  # Honors students who selected Honors courses
            honors_students_general_courses,  # Other Honors students
            general_students  # General population
        ])
        df_assigned = pd.DataFrame(columns=['UFID', 'Stu Name', 'Course Offering Id 18', 'Topic', 'Class Number', 'RandomDigit'])

        print('Starting FOR Loop...')
        for _, row in df_capacity.iterrows():
            number_of_students = row['CAPACITY']
            criteria = row['Course Offering Id 18']
            iterator = 0
        
            while iterator < number_of_students:
                iterator += 1
                try:
                    first_matching_row = df_ready.loc[df_ready['Course Offering Id 18'] == criteria].iloc[0]
                    new_row = {
                        'UFID': first_matching_row['UFID'],
                        'Stu Name': first_matching_row['Full Name'],
                        'Course Offering Id 18': first_matching_row['Course Offering Id 18'],
                        'Topic': first_matching_row['Topic'],
                        'RandomDigit': first_matching_row['RandomDigit']
                    }
                except:
                    first_matching_row = {'UFID': 'DROP', 'Course Offering Id 18': criteria}
                    new_row = first_matching_row

                new_row_df = pd.DataFrame([new_row])
                df_assigned = pd.concat([df_assigned, new_row_df], ignore_index=True)
                df_ready = df_ready[df_ready['UFID'] != first_matching_row['UFID']]

        df_assigned_sorted = df_assigned.sort_values(by='Course Offering Id 18')
        df_class_cap_all = class_cap_orig.sort_values(by='Course Offering Id 18')

        repeated_CNs = []
        for _, row in df_class_cap_all.iterrows():
            repeated_CNs.extend([row['CN']] * row['C_CAPACITY'])

        df_assigned_sorted['Class Number'] = repeated_CNs
        df_assigned_sorted.drop(df_assigned_sorted[df_assigned_sorted['UFID'] == 'DROP'].index, inplace=True)

        print('Writing to Excel...')
        writer = pd.ExcelWriter(rf'{filedir}\output_files\{thedate}_{term}_Quest_Results_Version_{len(df_assigned_sorted)}_{i}.xlsx', engine='xlsxwriter')
        df_assigned_sorted.to_excel(writer, sheet_name='assigned')
        df_ready.to_excel(writer, sheet_name='unassigned')
        class_cap_orig.to_excel(writer, sheet_name='class_cap')
        writer.close()
        print(f'Completed Option {i} with {len(df_assigned_sorted)} rows')
        print('---')
    
    print(rf'Finished with {term}')