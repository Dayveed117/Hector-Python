import os, sys, fnmatch

def create_folder(existing_folder, folder_name):
    """
    create_folder :
        Creates a folder with 'folder_name' in an already existing folder if not found in this directory.\n
        If it new folder already exists, does not overwrite.\n
        Returns its absolute path.

    Parameters
    ----------
    existing_folder : Path or str
        Path to an existing folder where 'folder_name' will be placed.
    folder_name : str
        Name of the folder to be created.

    Returns
    -------
    folder_path : Path or str
        Path to the folder specified in 'folder_name'
    """

    #   Just return the existing folder path if we dont want to create a new one
    #   Tests if folder_name is empty or not
    if not folder_name.strip():
        return existing_folder

    #   TODO : Try substitute with regular expression
    if not os.path.exists(existing_folder):
        print('Path to container folder does not exist.')
        sys.exit(0)
    elif folder_name.find(r'\\') != -1 or folder_name.find(r'/') != -1 or folder_name.find(r".") != -1:
        print('Folder has weird designation, use a standart name for a folder.')
        sys.exit(0)


    #   Desired control file directory to store new files
    folder_path = os.path.join(existing_folder, folder_name)
        
    #   Create folder if needed
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    
    return folder_path
    

#   General search in a specified folder for a specified file format
def search_files(oldfolder, ftype):
    """
    search_files :
        Searches recursively inside 'oldfolder' and finds all files that have type 'ftype'.

    Arguments
    ---------
    oldfolder : Path or str
        Path to folder which contains or may contain specified file format.
    ftype : str
        String that specifies file format.
    
    Return
    ------
    file_info : lst
        Tuple list which has the files' name as first and its absolute path as second.
    """


    #   Check if this path is viable
    if not os.path.exists(oldfolder):
        print('The targeted folder does not exist - Aborting!')
        sys.exit(0)

    file_info = []
    
    #   Search recursively in specified folder for old ctl files
    #   Stores old files names and paths
    for path, _, files in os.walk(oldfolder):
        for fname in fnmatch.filter(files, '*%s' %ftype):
            abspath = os.path.abspath(os.path.join(path, fname))
            file_info.append((fname, abspath))
    
    return file_info


#   Creates or finds unique file name in directory d_path 
def find_unique(d_path, fname, fformat):
    """
    find_unique :
        Checks if 'fname' is unique name in 'd_path' folder.\n
        Concatenates an identifier such as 'd__' where d is a digit if fname and its previous attempts exists.\n
        Returns 'fname' or '(number)__ + fname' when unique.

    Parameters
    ----------
    d_path : Path or str
        Path to a specified folder in which we try to find a unique file path.
    fname : str
        The desired file name.
    fformat : str
        File format of 'fname'.

    Returns
    -------
    newfilename : str
        The unique file name found in directory 'd_path'.
    """
    

    freset = fname.replace(fformat, '.json')
    newfilename = freset
    c = 1

    while os.path.exists(os.path.join(d_path, newfilename)):
        newfilename = "%d__"%c + freset
        c += 1
    
    return newfilename
