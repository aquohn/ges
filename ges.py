#!/usr/bin/env python3

import re # reeeeeeee

# ['year', 'university', 'school', 'degree', 'employment_rate_overall', 'employment_rate_ft_perm', 'basic_monthly_mean', 'basic_monthly_median', 'gross_monthly_mean', 'gross_monthly_median', 'gross_mthly_25_percentile', 'gross_mthly_75_percentile']

# manual cleaning: remove MBBS, LLB, remove typo by NUS where there's no space
# between (Pharmacy) and (Hons), and typo by NTU where there's no space around
# the / in Physics / Applied Physics, and replaced Mathematical Science with
# Mathematical Sciences

datafile = open("graduate-employment-survey-ntu-nus-sit-smu-sutd.csv", 'r')
cleanfile = open("ges.csv", 'w')

degree_dict = {}
headers = []
re_bachelor = re.compile("Bachelor of .*(\(.*\)|in .*)$")

for line in datafile:
    line = line.strip()

    # create honours field
    if len(headers) == 0:
        headers = line.split(',')
        headers.append("honours")
        cleanfile.write(','.join(headers) + "\n")
        continue

    # clean fields with extraneous commas and special characters we don't want
    cleanline = ""
    esc = False # flag for whether or not the next comma we encounter is escaped
    for c in line:
        if c in "*#^+":
            continue
        elif c == '"':
            if esc:
                esc = False
            else:
                esc = True
        elif esc:
            if c == ',':
                cleanline += ' '
            else:
                cleanline += c
        else:
            cleanline += c

    # split into fields and create lowercase version for easy comparison
    data = list(map(str.strip, cleanline.split(',')))
    faculty = data[2].lower()
    degree = data[3].lower()

    # exclude majors with no reported data
    if data[4] == "na":
        continue

    # clean faculty
    if "comp" in faculty or "info" in faculty or "comp" in degree or "info" in degree:
        data[2] = "Computing"
    elif "music" in faculty or "music" in degree or "fine" in degree:
        data[2] = "Music and Art"
    elif "design" in faculty:
        data[2] = "Design and Environment"
    elif "social" in faculty or "arts" in faculty or "econ" in faculty or "humani" in faculty or "arts" in degree: # be careful about other B.A. degrees like archi
        data[2] = "Arts and Social Sciences"
    elif "engin" in faculty or "engin" in degree:
        data[2] = "Engineering"
    elif "business" in faculty or "account" in faculty or "business" in degree or "account" in degree or "manag" in degree:
        data[2] = "Business Accounting and Management"
    elif "law" in faculty:
        data[2] = "Law"
    elif "medicine" in faculty or "nursing" in faculty or "nursing" in degree or "medicine" in degree or "therap" in degree or "health" in degree or "diag" in degree:
        data[2] = "Medicine Health and Nursing"
    elif "dentist" in faculty or "dentist" in degree:
        data[2] = "Dentistry"
    elif "education" in faculty or "education" in degree:
        data[2] = "Education"
    elif "science" in faculty or "science" in degree: # get social sciences and computer science out of the way first
        data[2] = "Science"
    else:
        data[2] = "Misc"

    # deduce honours
    if "hons" in degree or "honours" in degree:
        data.append("Honours")
    elif data[1] == "Singapore Management University": # only SMU uses the cum laude system without the standard honours system
        if "cum laude" in degree:
            data.append("Cum Laude")
        else:
            data.append("No Cum Laude")
    else:
        data.append("No Honours")
    data[3] = re.sub(r"( \([^()]*Hon[^()]*\)| with Honours| Cum Laude and above)", "", data[3])

    # clean degree
    data[3] = re.sub(r" \([^()]*4-year[^()]*\)", "", data[3]) # delete the "4-year programme" annotations
    bach_match = re_bachelor.match(data[3]) # find the "Bachelor of XXX (<degree>)" or "Bachelor of XXX in <degree>" pattern, and capture <degree>
    if bach_match:
        cleandeg = bach_match.group(1) # extract <degree> accordingly
        if cleandeg[0] == '(':
            data[3] = cleandeg[1:-1]
        else:
            data[3] = cleandeg[3:]
    # ensure that only one combination of capitalisations is used
    degree = data[3].lower()
    if degree in degree_dict:
        data[3] = degree_dict[degree]
    else:
        degree_dict[degree] = data[3]

    # write out
    cleanfile.write(','.join(data) + "\n")

datafile.close()
cleanfile.close()
