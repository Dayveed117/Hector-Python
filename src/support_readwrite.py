import json, os, sys

def readControl(filepath):
    """
    readControl :
        Read json file from filepath and parses its information into dictionaries.\n
        Information is expected to be from a control file. 

    Parameters
    ----------
    filepath : str
        The absolute filepath or relative from root to a control file.
    Returns
    -------
    control_dict : dict
        One dictionary with specifications regarding a control file, such as:\n
        "Definition" : Option
    """

    try:
        if(os.path.exists(filepath) and filepath.endswith('.json')):
            fp = open(filepath, "r")
            control_dict = json.load(fp)
            fp.close()
            return control_dict
        else:
            raise FileNotFoundError('Invalid file path for control file.')
        
    except (FileNotFoundError,json.JSONDecodeError) as e:
        print(e)
        sys.exit(0)
    except Exception as e:
        print('Something unexpected ocurred :\n' + e)
        sys.exit(0)


def readObservations(filepath):
    """
    readObservations :
        Read json file from filepath and parses its information into dictionaries.
        Information is expected to be from an observations' file.
            
    Parameters
    ----------
    filepath : str
        The absolute filepath or relative from root to a observations file.

    Returns
    -------
    header_dict : dict
        Dictionary with information on some parameters regarding observations values on data dict with pairs such as:\n
        'Header' : Value or 'Header' : Value

    data_dict : dict
        Dictionary filled with observation values of pairs 'Date' : Value. May also have Estimated Value next to Value.
    """

    try:
        if(os.path.exists(filepath) and filepath.endswith('.json')):
            fp = open(filepath, "r")
            header_dict = json.load(fp)
            data_dict = header_dict.pop('Observations')
            fp.close()
            return header_dict, data_dict
        else:
            raise FileNotFoundError('Invalid file path for observations file.')

    except (FileNotFoundError,json.JSONDecodeError) as e:
        print(e)
        sys.exit(0)
    except Exception as e:
        print('Something unexpected ocurred :\n' + e)
        sys.exit(0)


def writeToFile(dictionary, filepath):
    """
    writeToFile :
        Dumps 'dictionary' into a .json file format in 'filepath'.

    Parameters
    ----------
    dictionary : dict
        Dictionary an Observation instance state.
    filepath : path or str
        Path to file where 'dictionary' will be stored.

    Returns
    -------
    True or False :
        Successful or unsuccessful operation.
    """
    
    
    try:
        fp = open(filepath, "w")
        json.dump(dictionary, fp, indent=4)
        fp.close()

        return True

    except Exception as e:
        print('Something unexpected ocurred :\n' + e)
        return False
