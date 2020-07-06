import os
from Converters import Converters

#   Example script test

project_root = os.getcwd()
print(project_root)

#   Directories where control and observations are placed
observations_path = os.path.join(project_root, 'hector_files\observation_files')
control_path = os.path.join(project_root, 'hector_files\control_files')
test_observations = os.path.join(project_root, 'hector_files\\test_observations')
test_control = os.path.join(project_root, 'hector_files\\test_control')

examplefolder1 = 'example1'
examplefolder2 = 'example2'
examplefolder3 = 'example3'
examplefolder4 = 'example4'
examplefolder5 = 'example5'

Converters.folder_convert_control_tojson("path/to/directory/being/searched", "an/existing/directory", "new/folder/name/or/blank")
Converters.folder_convert_mom_tojson("path/to/directory/being/searched", "an/existing/directory", "new/folder/name/or/blank")
