import json
import sys
import logging
import os
import csv
import subprocess
from git import Repo

organization_project_separator = "_____"

months = 12

repos_to_clone = './repos_to_clone.csv'
cloned_repos_csv = './cloned_repos.csv'
clones_path = './cloned_repos/'
people_csv = './people_' + str(months) + '_months.csv'

# def get_clone_path(repo, is_absolute):
#     if(is_absolute):
#         return os.path.abspath(clones_path + repo['ID'].replace("/", organization_project_separator))
#     else:
#         return clones_path + repo['ID'].replace("/", organization_project_separator)

# def clone_repo(repo, path_to_clone):
#     try:
#         if(not os.path.exists(path_to_clone)):
#             Repo.clone_from(url = 'https://github.com/' + repo['ID'] + '.git', to_path = path_to_clone)
#         else:
#             print("Jumped repo because its folder already exists: " + repo['id'])
#     except:
#         print("Error for: " + repo['ID'])
#         print(sys.exc_info()[0])


# def start_cloning():
#     with open(repos_to_clone, 'r') as f:  
#         repos_list = csv.DictReader(f, delimiter=',')
#         counter = 1
#         cloned_repos = list()
#         for p in repos_list:
#             print("Cloning repo number " + str(counter) + " --- " + p['ID'])
#             counter += 1
#             absolute_path_to_clone = get_clone_path(p, True)
#             local_path_to_clone = get_clone_path(p, False)
#             clone_repo(p, absolute_path_to_clone)
#             p['absolute_clone_path'] = absolute_path_to_clone
#             p['local_clone_path'] = local_path_to_clone
#             cloned_repos.append(p)

#     with open(cloned_repos_csv, 'w') as f:
#         writer = csv.writer(f)
#         writer.writerow(['ID', 'absolute_clone_path', 'local_clone_path'])
#         for row in cloned_repos:
#             writer.writerow([row['ID'], row['absolute_clone_path'], row['local_clone_path']])


def get_folders_in_directory(directory):

    directory = os.path.abspath(directory)

    all_items = os.listdir(directory)

    # extract only folders, non-recursive
    folders = [item for item in all_items if os.path.isdir(os.path.join(directory, item))]

    # get absolute paths
    folder_paths = [os.path.abspath(os.path.join(directory, folder)) for folder in folders]

    return folder_paths


def collect_absolute_paths():
    folder_paths = get_folders_in_directory("/home/schiopu/Desktop/Chalmers-ROS-RM-FT-Datamining/dataset/Repos")

    with open(cloned_repos_csv, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['absolute_clone_path'])

        for path in folder_paths:
            writer.writerow([path])

# --------------------------------------------------------------

def collect_emails():
    with open(cloned_repos_csv, 'r') as f: 
        repos_list = csv.DictReader(f, delimiter=',')
        counter = 1
        people = list()
        seen = list()

        for p in repos_list:
            print("Collecting emails for repo number " + str(counter) + " --- " + p['absolute_clone_path'])
            counter += 1
            contributors = subprocess.check_output('cd ' + p['absolute_clone_path'] + ';git log --since="' + str(months) + ' month ago" --pretty="%aN---%ae" | sort -u | uniq;', shell=True, universal_newlines=True)
            if(len(contributors) > 0):
                splitted = contributors.split('\n')
                cleaned = list()
                for el in splitted:
                    if((not 'noreply' in el) and (el != '') and (not el in seen) ):
                        cleaned.append({'name': el.split("---")[0], 'email': el.split("---")[1], 'repo': p['absolute_clone_path']})
                        seen.append(el)
                people = people + cleaned
            # cleaned = [ el for el in contributors.split('\n') if 'noreply' in not in el]
        # for el in people:
        #         print(el)
        # print(len(people))

        # for p in repos_list:
        #     print("Collecting names for repo number " + str(counter) + " --- " + p['absolute_clone_path'])
        #     counter += 1
        #     contributors = subprocess.check_output('cd ' + p['absolute_clone_path'] + ';git log --since="' + str(months) + ' month ago" --pretty="%aN" | sort | uniq;', shell=True, universal_newlines=True)
        #     if(len(contributors) > 0):
        #         splitted = contributors.split('\n')
        #         cleaned = list()
        #         for el in splitted:
        #             if((not 'noreply' in el) and (el != '') and (not el in seennames) ):
        #                 cleaned.append({'email': el, 'repo': p['absolute_clone_path']})
        #                 seennames.append(el)
        #         names = names + cleaned


    with open(people_csv, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'email', 'repo'])
        for row in people:
            writer.writerow([row['name'], row['email'], row['repo']])


# start_cloning()
# collect_absolute_paths()
collect_emails()