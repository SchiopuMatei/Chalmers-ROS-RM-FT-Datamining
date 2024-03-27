import json
import sys
import os
from bs4 import BeautifulSoup
import ast
import csv 
import re
import configuration as c

cloned_repos = './repos_mining_data/otherData/cloned_repos.json'
clones_path = '../Repos/'
detection_result_path = './repos_mining_data/otherData/repos_detected_files.json'
filtered_heuristic = './repos_mining_data/otherData/repos_filtered_launch_file.json'
exported_gdrive = './repos_mining_data/otherData/exported_gdrive.csv'

micro_ROS_project = False

def is_xml(file_name):
        try:
                with open(file_name) as f:
                        content = f.read()
                        re.sub(r"\W", "", content)
                        return content.strip().startswith('<')
        except:
                return False        

def search_files(path, pattern) -> list:
        filellist = list()
        for root, dirs, files in os.walk(path):
                for name in files:
                        if((name.endswith(pattern))):
                                filellist.append(os.path.join(root, name))
        return filellist

def search_xml_files(path) -> list:
        filellist = list()
        for root, dirs, files in os.walk(path):
                for name in files:
                        if(is_xml(os.path.join(root, name))):
                                filellist.append(os.path.join(root, name))
        return filellist

def get_xml_launch_file_info(xml_file):
        try:
                with open(xml_file) as f:
                        content = f.read().encode('utf-8', 'ignore')
                        soup = BeautifulSoup(content, 'xml')
                        # The XML file is a ROS launch file if it contains one <launch> tag as root
                        if(not soup.find('launch')):
                                return -1
                        num_nodes = len(soup.find_all('node'))
                        num_includes = len(soup.find_all('include'))

                        num_includes_system_modes = len(soup.find_all('system_modes'))
                        system_modes_included = False
                        if (num_includes_system_modes) > 0:
                                system_modes_included = True

                        return {'path': xml_file, 'num_nodes': num_nodes, 'num_includes': num_includes, 'system_modes_included': system_modes_included, 'type': 'xml'}
        except Exception as e:
                print(xml_file)
                print (str(e))
                return -1

def get_py_launch_file_info(py_file):
        try: 
                with open(py_file) as f:
                        string_contents = f.read()
                        # the Python file is a ROS2 Launch file if it BOTH imports the "launch" package and refers to the "LaunchDescription" module
                        if((not ("from launch" in " ".join(string_contents.split()))) or (not ("import launch" in " ".join(string_contents.split()))) or (not ("LaunchDescription" in string_contents))):
                                return -1
                        num_nodes =  string_contents.count('actions.Node(')
                        num_includes = string_contents.count('include_launch_description')

                        num_includes_system_modes = 0
                        num_includes_system_modes += string_contents.count('system_modes') 
                        num_includes_system_modes += string_contents.count('modelfile')
                        num_includes_system_modes += string_contents.count('mode_manager.launch')


                        num_GetAvailableStates = string_contents.count('GetAvailableStates')
                        num_GetState = string_contents.count('GetState')
                        num_ChangeState = string_contents.count('ChangeState')

                        num_ChangeMode = string_contents.count('ChangeMode')
                        num_GetMode = string_contents.count('GetMode')
                        num_GetAvailableModes = string_contents.count('GetAvailableModes')

                        num_TransitionEvent = string_contents.count('TransitionEvent')
                        num_ModeEvent = string_contents.count('ModeEvent')

                        system_modes_included = False

                        if (num_includes_system_modes > 0 
                                | num_GetAvailableStates > 0 
                                | num_GetState > 0 
                                | num_ChangeState > 0 
                                | num_ChangeMode > 0 
                                | num_GetMode > 0 
                                | num_GetAvailableModes > 0 
                                | num_TransitionEvent > 0 
                                | num_ModeEvent > 0) : 
                                system_modes_included = True


                        if system_modes_included == True :
                                micro_ROS_project = True


                        num_LifecycleNode = string_contents.count('LifecycleNode')  
                        lifecycleNodes_included = False    
                        if num_LifecycleNode > 0  :
                                lifecycleNodes_included = True

                        num_cloudwatch_logger = string_contents.count('cloudwatch_logger')  
                        cloudwatch_logger_included = False    
                        if num_cloudwatch_logger > 0  :
                                cloudwatch_logger_included = True
                        
                        return {'path': py_file, 'num_nodes': num_nodes, 'num_includes': num_includes,
                                        'system_modes_included': system_modes_included,
                                        'num_includes_system_modes': num_includes_system_modes,
                                        'num_GetAvailableStates': num_GetAvailableStates,
                                        'num_GetState': num_GetState,
                                        'num_ChangeMode': num_ChangeMode,
                                        'num_GetMode' : num_GetMode,
                                        'num_GetAvailableModes' : num_GetAvailableModes,
                                        'num_TransitionEvent' : num_TransitionEvent,
                                        'num_ModeEvent' : num_ModeEvent,
                                        'num_ChangeState': num_ChangeState,
                                        'lifecycleNodes_included': lifecycleNodes_included,
                                        'cloudwatch_logger_included': cloudwatch_logger_included, 
                                        'type': 'py'}
        except:
                return -1
        

def detect_yaml_files(repo):
        result = list()
        file_list = search_files(repo['local_clone_path'], '.yaml')
        for yaml_file in file_list:
                file_info = get_yaml_info(yaml_file)
                if(file_info != -1):
                        result.append(file_info)
        return result

def get_yaml_info(yaml_file):
        try: 
                with open(yaml_file) as f:
                        string_contents = f.read()
                        
                        num_modes_declarations =  string_contents.count('modes:')
                        if (num_modes_declarations > 0):
                                micro_ROS_project = True
                                return {'path': yaml_file, 'num_modes_declarations': num_modes_declarations, 'type': 'yaml'}

                        return -1
        except:
                return -1
        

def detect_cpp_files(repo):
        result = list()
        file_list = search_files(repo['local_clone_path'], '.cpp')
        for cpp_file in file_list:
                file_info = get_cpp_info(cpp_file)
                if(file_info != -1):
                        result.append(file_info)
        return result

def get_cpp_info(cpp_file):
        try: 
                with open(cpp_file) as f:
                        string_contents = f.read()
                        

                        lifecycle_msg_declarations =  string_contents.count('lifecycle_msgs')                        
                        ROS_DEBUG_declarations =  string_contents.count('ROS_DEBUG')
                        ROS_INFO_declarations =  string_contents.count('ROS_INFO')
                        ROS_WARN_declarations =  string_contents.count('ROS_WARN')
                        ROS_ERROR_declarations =  string_contents.count('ROS_ERROR')
                        ROS_FATAL_declarations =  string_contents.count('ROS_FATAL')


                        return {'path': cpp_file, 'lifecycle_msg_declarations': lifecycle_msg_declarations,
                         'ROS_DEBUG_declarations': ROS_DEBUG_declarations,
                         'ROS_INFO_declarations': ROS_INFO_declarations,
                         'ROS_WARN_declarations': ROS_WARN_declarations,
                         'ROS_ERROR_declarations': ROS_ERROR_declarations,
                         'ROS_FATAL_declarations': ROS_FATAL_declarations,   'type': 'ccp'}


                        return -1
        except:
                return -1

def detect_xml_launch_files(repo):
        result = list()
        file_list = search_files(repo['local_clone_path'], '.xml')
        file_list= file_list + search_xml_files(repo['local_clone_path'])
        for xml_file in file_list:
                file_info = get_xml_launch_file_info(xml_file)
                if(file_info != -1):
                        result.append(file_info)
        return result

def detect_py_launch_files(repo):
        result = list()
        file_list = search_files(repo['local_clone_path'], '.py')
        for py_file in file_list:
                file_info = get_py_launch_file_info(py_file)
                if(file_info != -1):
                        result.append(file_info)
        return result

def start_detecting():
    with open(cloned_repos, 'r') as f:  
        repos_list = json.load(f)
        counter = 1
        detection_result = list()
        for p in repos_list:
            print("Detecting files for repo number " + str(counter) + " --- " + p['id'])
            counter += 1
            micro_ROS_project = False
            p['xml_launch_files'] = detect_xml_launch_files(p)
            p['py_launch_files'] = detect_py_launch_files(p)
            p['yaml_system_mode_files'] = detect_yaml_files(p)
            p['cpp_files'] = detect_cpp_files(p)
            if micro_ROS_project == True:
              p['micro_ROS'] = {'micro_ROS_project': True}
            else:
              p['micro_ROS'] = {'micro_ROS_project': False}
            detection_result.append(p)
    c.save(detection_result_path, detection_result)

def apply_filtering_heuristics():
        with open(detection_result_path, 'r') as f:
                repos = json.load(f)
                with_launch_file = 0
                final_filtered = 0
                collected_xml_launch_files = list()
                collected_py_launch_files = list()
                filtered_repos = list()
                for p in repos:
                        # Check 1: the repo must contain at least one Launch file
                        if((len(p['xml_launch_files']) > 0) or (len(p['py_launch_files']) > 0)):
                                with_launch_file += 1
                                total_nodes = 0
                                total_includes = 0
                                total_ros_includes = 0
                                total_lifecycleNodes_included = 0
                                total_cloudwatch_logger_included = 0 

                                num_includes_system_modes = 0
                                total_lifecycle_msg_declarations = 0
                                total_ROS_DEBUG_declarations = 0
                                total_ROS_INFO_declarations = 0
                                total_ROS_WARN_declarations = 0
                                total_ROS_ERROR_declarations = 0
                                total_ROS_FATAL_declarations = 0

                                for el in p['xml_launch_files']:
                                        total_nodes += el['num_nodes']
                                        total_includes += el ['num_includes']
                                for el in p['py_launch_files']:
                                        total_nodes += el['num_nodes']
                                        total_includes += el ['num_includes']
                                        # print(el ['system_modes_included'])
                                        num_includes_system_modes += el ['num_includes_system_modes']

                                        if el ['lifecycleNodes_included']:
                                                total_lifecycleNodes_included += 1

                                        if el ['cloudwatch_logger_included']:
                                                total_cloudwatch_logger_included += 1

                                for el in p['cpp_files']:
                                        total_lifecycle_msg_declarations += el['lifecycle_msg_declarations']
                                        total_ROS_DEBUG_declarations += el ['ROS_DEBUG_declarations']
                                        total_ROS_INFO_declarations += el ['ROS_INFO_declarations']
                                        total_ROS_WARN_declarations += el ['ROS_WARN_declarations']
                                        total_ROS_ERROR_declarations += el ['ROS_ERROR_declarations']
                                        total_ROS_FATAL_declarations += el ['ROS_FATAL_declarations']

                                # print(p['micro_ROS'])
                                # for el in p['micro_ROS']:
                                #         print(el)
                                #         # if (el ['micro_ROS_project'] != False):
                                #         #         total_ros_includes += 1

                                        
                                        # 'num_GetAvailableStates': num_GetAvailableStates,
                                        # 'num_GetState': num_GetState,
                                        # 'num_ChangeMode': num_ChangeMode,
                                        # 'num_GetMode' : num_GetMode,
                                        # 'num_GetAvailableModes' : num_GetAvailableModes,
                                        # 'num_TransitionEvent' : num_TransitionEvent,
                                        # 'num_ModeEvent' : num_ModeEvent,
                                        # 'num_ChangeState':num_ChangeState, 


                                collected_xml_launch_files.append(len(p['xml_launch_files']))
                                collected_py_launch_files.append(len(p['py_launch_files']))

                                if total_lifecycleNodes_included != 0:
                                        print(p['id'] + " - total_lifecycleNodes_included :" + str(total_lifecycleNodes_included))
                                if total_cloudwatch_logger_included != 0:
                                        print(p['id'] + " - total_cloudwatch_logger_included :" + str(total_cloudwatch_logger_included))
                                if total_lifecycle_msg_declarations != 0:
                                        print("\033[92m"+ p['id'] + " - total_lifecycle_msg_declarations :" + str(total_lifecycle_msg_declarations) + "\033[0m")
                                if total_ROS_DEBUG_declarations != 0:
                                        print("\033[91m" + p['id'] + " - total_ROS_DEBUG_declarations :" + str(total_ROS_DEBUG_declarations) + "\033[0m")
                                if total_ROS_INFO_declarations != 0:
                                        print("\033[93m" + p['id'] + " - total_ROS_INFO_declarations :" + str(total_ROS_INFO_declarations) + "\033[0m")
                                if total_ROS_WARN_declarations != 0:
                                        print("\033[94m" + p['id'] + " - total_ROS_WARN_declarations :" + str(total_ROS_WARN_declarations) + "\033[0m")
                                if total_ROS_ERROR_declarations != 0:
                                        print("\033[95m" + p['id'] + " - total_ROS_ERROR_declarations :" + str(total_ROS_ERROR_declarations) + "\033[0m")
                                if total_ROS_FATAL_declarations != 0:
                                        print("\033[96m" + p['id'] + " - total_ROS_FATAL_declarations :" + str(total_ROS_FATAL_declarations) + "\033[0m")

                                if(total_nodes >= 2 or total_includes >= 1):
                                        final_filtered += 1
                                filtered_repos.append(p)
                c.save(filtered_heuristic, filtered_repos)
                print("Total number XML launch file: " + str(sum(collected_xml_launch_files)))
                print("Details: " + str(collected_xml_launch_files))
                print("Total number Python launch file: " + str(sum(collected_py_launch_files)))
                print("Details: " + str(collected_py_launch_files))
                print("Repos with either an XML or Python launch file: " + str(with_launch_file))
                print("Repos with either more than 2 nodes or 1 include statement: " + str(final_filtered))
                print("Repos with Micro-ROS include statement: " + str(num_includes_system_modes))

def prepare_export_gdrive():
        csv.register_dialect('tab_separated_csv', delimiter = '\t', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        exported_contents = list()
        with open(filtered_heuristic, 'r') as f:
              repos = json.load(f)
              for p in repos:
                      exported_contents.append([p['id'], p['description'], p['web_url'], p['default_branch'], len(p['xml_launch_files']), len(p['py_launch_files'])])
        with open(exported_gdrive, 'w+') as f:
                writer = csv.writer(f, dialect='tab_separated_csv')
                for row in exported_contents:
                        writer.writerow(row)
        
# start_detecting()
apply_filtering_heuristics()
prepare_export_gdrive()
