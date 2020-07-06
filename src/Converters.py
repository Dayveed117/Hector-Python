import pandas as pd
import os, sys, fnmatch, math, json
from support_conv import create_folder, search_files, find_unique
from Exceptions import FileMalformationError, UnidentifiedHeaderError

class Converters:


    # =============================================================================================== #
    # CONTROL CONVERSION
    # =============================================================================================== #


    @classmethod
    def single_convert_control_tojson(cls, d_path, i_path, i_fname):
        """
        single_convert_control_tojson :
            Converts a single control file in .ctl format to .json format.

        Parameters
        ----------
        d_path : Path or str
            Path to folder in which we want to place the new converted file.
        i_path : Path or str
            Path to the file that needs to be converted
        i_fname : str
            Name of the file specified in 'i_path'
        """


        keys = []
        values = []
            
        for line in open(i_path, "r"):
            
            #   Ignore comments or blank lines
            if line.startswith('#---') or not line.strip():
                continue

            cols = line.split()

                        
            if len(cols) >= 2:
                keys.append(cols[0])

                if len(cols) == 2:
                    values.append(cols[1])
                else:
                    #   Multiple values for a line are added as list
                    values.append(cols[1:])
            
                

        #   Create a time series with index as keys and value values
        ts = pd.Series(values, keys)

        #   Find a suitable unique file name in d_path
        newfilename = find_unique(d_path, i_fname, '.ctl')
        newcontrol = os.path.join(d_path, newfilename)

        #   Export time series to json format
        ts.to_json(newcontrol, orient='index', indent=4)


    @classmethod
    def folder_convert_control_tojson(cls, old_controlfile_folder, container_path, new_folder_name=''):
        """
        folder_convert_control_tojson :
            Searches recursively inside argument for files in .ctl format and renews them into a new control in .json format.\n
            The new file is stored on a folder in this files' current directory.

        Arguments
        ---------
        old_controlfile_folder : path or string
            Path to folder which contains control files in dated .ctl format.
        container_path : path or str
            Path to an already existing folder where 'new_folder_name' will be placed
        new_folder_name : str
            Folder designation to store renewed files.
        """
        

        #   Desired control file directory to store new files
        new_control_directory = create_folder(container_path, new_folder_name)

        #   Aquire all the files and filepaths for the operation
        old_file_list = search_files(old_controlfile_folder, '.ctl')

        #   Start renewing old files
        for f_info in old_file_list:
            
            #   Some files are supposed to be hidden
            if f_info[0].startswith('._'):
                continue

            Converters.single_convert_control_tojson(new_control_directory, f_info[1], f_info[0])


    # =============================================================================================== #
    # MOM CONVERSION
    # =============================================================================================== #


    @classmethod
    def single_convert_mom_tojson(cls, d_path, i_path, i_fname):
        """
        single_convert_mom_tojson :
            Converts a single observation file in .mom format to .json format.

        Parameters
        ----------
        d_path : Path or str
            Path to an existing folder in which we want to place the new converted file.
        i_path : Path or str
            Path to the file that needs to be converted
        i_fname : str
            Name of the file specified in 'i_path'
        """


        #   States if arg can be float or not
        def ensure_float(arg):
            return isinstance(float(arg), float)

        def first(lst):
            return lst[0]
        
        #   Information that a .mom file may have
        offsets = []
        sp = 1.0
        logd = []
        expd = []
        kv_pair = []
        
        #   For error information
        line_number = 1
        mjd_ant = 0.0
        curr_mjd = 0.0
        errors = []
        padding = 0
        
        for line in open(i_path, "r"):
            
            #   Split lines per whitespacing
            cols = line.split()
            try:
                #   Detecting headers
                if cols[0].startswith("#"):
                    
                    if cols[1].startswith("sampling") and cols[2].startswith("period"):
                        if len(cols) == 4:
                            sp = float(cols[3])
                        else:
                            raise FileMalformationError('Row %d -> Sampling Period header malformation.' %line_number)

                    elif cols[1].startswith("offset"):
                        if len(cols) == 3:
                            offsets.append((float(cols[2])))
                        else:
                            raise FileMalformationError('Row %d -> Offset header malformation.' %line_number)

                    elif cols[1].startswith("log"):
                        if len(cols) == 4:
                            logd.append([(float(cols[2])), float(cols[3])])
                        else:
                            raise FileMalformationError('Row %d -> Log header malformation.' %line_number)
                    
                    elif cols[1].startswith("exp"):
                        if len(cols) == 4:
                            expd.append([(float(cols[2])), float(cols[3])])
                        else:
                            raise FileMalformationError('Row %d -> Exp header malformation.' %line_number)
                    
                    else:
                        raise UnidentifiedHeaderError('Row %d -> Not a recognizable header.' %line_number)
                
                #   Actual data values
                else:
                    
                    #   Without estimated column
                    if len(cols) == 2:
                        
                        if not ensure_float(float(cols[0])):
                            continue
                        curr_mjd = float(cols[0])

                        #   Check for inconsistencies in mjd
                        if mjd_ant != 0 and (mjd_ant + sp) != curr_mjd:
                            
                            tmp_mjd = mjd_ant
                            cycle = 1
                            
                            #   Filling gaps with Sampling Period multiples
                            while(tmp_mjd + sp <= curr_mjd):

                                tmp_mjd = mjd_ant + (cycle*sp)
                                kv_pair.append([float(tmp_mjd), math.nan])
                                padding += 1
                                cycle += 1
                            
                        if ensure_float(cols[1]):
                            kv_pair.append([float(curr_mjd), float(cols[1])])
                        else:
                            kv_pair.append([float(curr_mjd), math.nan])


                    #   With estimated column
                    elif len(cols) == 3:
                        
                        if not ensure_float(float(cols[0])):
                            continue
                        curr_mjd = float(cols[0])

                        #   Check for inconsistencies in mjd
                        if mjd_ant != 0 and (mjd_ant + sp) != curr_mjd:
                            
                            tmp_mjd = mjd_ant
                            cycle = 1
                            
                            #   Filling gaps with Sampling Period multiples
                            while(tmp_mjd + sp <= curr_mjd):

                                tmp_mjd = mjd_ant + (cycle*sp)
                                kv_pair.append([float(tmp_mjd), [math.nan, math.nan]])
                                padding += 1
                                cycle += 1

                        if ensure_float(cols[1]) and ensure_float(cols[2]):
                            kv_pair.append([float(curr_mjd), [float(cols[1]), float(cols[2])]])    
                        else:
                            kv_pair.append([float(curr_mjd), [math.nan, math.nan]])
                    else:
                        raise FileMalformationError('Row %d -> Unexpected Row arguments on data row.' %line_number)
                
                #   Refresh mjd_ant
                mjd_ant = curr_mjd
                    
            except (UnidentifiedHeaderError, FileMalformationError) as e:
                errors.append(e)
            except ValueError:
                errors.append('Row %d -> Value error, bad cast.' %line_number)
            except TypeError:
                errors.append('Row %d -> Type Error, check this row\'s arguments.' %line_number)
            except Exception:
                errors.append('Row %d -> Something unexpected occurred.' %line_number)
            
            #   Increment line number after each for cycle
            line_number += 1


        #   Finished reading file, present errors if needed
        if errors != []:

            print('{0} : Row Malformations :\n'.format(i_fname))
            for e in errors:
                print(e)

            print('{0} : These malformations need to be fixed before exporting file.'.format(i_fname))
        
        else:

            if padding != 0:
                print('{0} : Inserted {1} (mjd,npnan) pairs as padding.'.format(i_fname, padding))
            
            #   Information is ready to proceed
            kv_pair.sort(key=first)
            data_dict = dict(kv_pair)
            export_ready = {'Sampling period' : sp, 
                            'Offsets' : offsets,
                            'Log' : logd,
                            'Exp' : expd,
                            'Observations' : data_dict }
            
            #   Find a suitable unique file name in d_path
            newfilename = find_unique(d_path, i_fname, '.mom')
            newobservation = os.path.join(d_path, newfilename)

            with open(newobservation, "w") as fp:
                json.dump(export_ready, fp, indent=4)


    @classmethod
    def folder_convert_mom_tojson(cls, old_momfiles_folder, container_path, new_folder_name=''):
        """
        folder_convert_mom_tojson :
            Searches recursively inside argument for files in .mom format and renews them into a new observations file in .json format.\n
            The new file is stored on a folder in this files' current directory.

        Arguments
        ---------
        old_momfile_folder : path or str
            Path to folder which may contain observation files in dated .mom format.
        container_path : path or str
            Path to an already existing folder where 'new_folder_name' will be placed
        new_folder_name : str
            Folder designation to store renewed files.
        """


        #   Desired control file directory to store new files
        new_observations_directory = create_folder(container_path, new_folder_name)

        #   Aquire all the files and filepaths for the operation
        old_file_list = search_files(old_momfiles_folder, '.mom')

        #   Start renewing old files
        for f_info in old_file_list:

            #   Some files are supposed to be hidden
            if f_info[0].startswith('._'):
                continue

            Converters.single_convert_mom_tojson(new_observations_directory, f_info[1], f_info[0])
