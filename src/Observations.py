import math, copy
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from support_readwrite import readControl, readObservations, writeToFile
from support_time import mjd_to_datetime

class Observations:
    """ 
    Observations
    ------------
    Bundles info regarding a control and observations file.\n
    Methods opt for some utilities when working with the data stored.\n
    

    Attributes
    ----------
    public :    
        timeseries : pandas DataFrame
            Pandas DataFrame with tabled information regarding obs_data attribute.\n

    private :
        ctl_file : str
            Path to a control file.\n
        obs_file : str
            Path to an observations file.\n
        sp : float
            Contains the sampling period for the observation.\n
        offsets : list
            List that has the index of what is to be considered an offset value within the observations.\n
        ctl_info : dict
            Dictionary filled with info related to control file.\n
        nan_share : float
            Share (%) of NaN's in timeseries['Value'].\n
    """


    #   Constructor for Observations object
    def __init__(self, ctl_file, obs_file):

        super().__init__()
        
        #   Private
        self.__ctl_file = ctl_file
        self.__obs_file = obs_file
        self.__ctl_info = {}
        self.__sp = 0.0
        self.__offsets = []
        self.__nan_share = 0.0

        #   Public
        self.timeseries = pd.DataFrame()
        



    #   Getter for ctl_file
    def get_ctl_file(self):
        """
        Getter for the 'ctl_file' attribute.
        """
        return self.__ctl_file


    #   Setter for ctl_file
    def set_ctl_file(self, ctl_file):
        """
        Setter for the 'ctl_file' attribute.\n
        """
        self.__ctl_file = ctl_file


    #   Getter for obs_file
    def get_obs_file(self):
        """
        Getter for the 'obs_file' attribute.\n
        """
        return self.__obs_file


    #   Setter for obs_file
    def set_obs_file(self, obs_file):
        """
        Setter for the 'obs_file' attribute.\n
        """
        self.__obs_file = obs_file


    #   Getter for control dictionary
    def get_control_dict(self):
        """
        Getter for the 'ctl_info' attribute.\n
        """
        return self.__ctl_info
    

    #   Getter for sample period
    def get_sp(self):
        """
        Getter for 'sp' attribute.\n
        """
        return self.__sp


    #   Getter for offsets list
    def get_offsets(self):
        """
        Getter for 'offsets' attribute.\n
        """
        return self.__offsets

    
    #   Getter for nan_share attribute
    def get_nan_share(self):
        """
        Getter for 'nan_share' attribute.\n
        """
        return self.__nan_share

    
    #   Generic getter for column in timeseries attribute
    def __get_column(self, column):
        if column in self.timeseries.columns.to_list():
            return self.timeseries[column].values
        return []
    
    
    #   Get timeseries estimates
    def get_column(self, column):
        """
        Returns a column from timeseries' DataFrame attribute\n
        """
        return self.__get_column(column)


    #   Get timeseries estimates
    def get_values(self):
        """
        Returns this objects' timeseries column 'Value' as a list\n
        """
        return self.__get_column('Value')
    

    #   Get timeseries indexes
    def get_indexes(self):
        """
        Returns this objects' timeseries indexes as a list\n
        """
        return self.timeseries.index.values

    
    #   Get MinimizationMethod attribute from control file if specified
    def get_min_method(self):
        """
        Returns a minimization method if specified in the 'ctl_info' dictionary or depending on nan_share value.\n
        """
        if 'MinimizationMethod' in self.__ctl_info and self.__ctl_info['MinimizationMethod'] != 'Default':
            return self.__ctl_info['MinimizationMethod']
        if self.__nan_share > 0.5:
            return 'Fullcov'
        return 'AmmarGrag'


    #   Get NoiseModels attribute from control file
    def get_noisemodels(self):
        """
        Returns the 'NoiseModels' specified in 'ctl_info' dictionary\n
        """
        if 'NoiseModels' in self.__ctl_info:
            return self.__ctl_info['NoiseModels']


    #   Method to load control file into ctl_info attribute
    def load_control(self):
        """
        Using this objects' ctl_file attribute, fill 'ctl_info' dictionary.\n
        """
        self.__ctl_info = readControl(self.__ctl_file)
        
    

    #   Method to load observations file into obs_info and obs_data
    def load_observations(self):
        """
        Using this objects' obs_file attribute, fill both obs_info and obs_data dictionaries.\n
        Fills 'timeseries', 'sp', 'offsets' and 'nan_share' attribute according to these 2 dictionaries.\n
        """
        obs_info, obs_data = readObservations(self.__obs_file)
        
        try:
            self.__sp = obs_info['Sampling period']
            self.__offsets = obs_info['Offsets']
        except KeyError as e:
            print('Missing key values from observations, please verify file integrity.\n' + e)

        values = []
        indexes = []
        est_values = []

        for k,v in obs_data.items():
            
            try:
                indexes.append(float(k))
                if isinstance(v, list):
                    if len(v) == 1:
                        values.append(float(v[0]))
                    elif len(v) == 2:
                        values.append(float(v[0]))
                        est_values.append(float(v[1]))
                    else:
                        raise IndexError('Number of invalid columns')
                else:
                    values.append(float(v))
            
            except IndexError as e:
                print(e)
            except (TypeError, ValueError) as err:
                print('Type casting failed : {0}\n\
                    Please check your observations file integrity.'.format(err))
        
        #   Create a timeseries object using lists above
        self.timeseries = pd.DataFrame(values, indexes, columns=['Value'])
        
        #   If there are already estimated values, add them as column
        if est_values != []:
            self.timeseries['Estimate c++'] = est_values

        #   Calculate NaN share in ['Value']
        if len(self.timeseries['Value']) is not 0:
            self.__nan_share = self.timeseries['Value'].isnull().sum() / len(self.timeseries['Value'])


    #   From timeseries mjd indexes generate a new list that has datetime values in iso format
    def gen_tsindexes_iso(self, isoformat=True):
        """
        Generates a list whose values are datetime objects converted from their mjd values in timeseries indexes\n
        If isoformat is True, values are displayed in ISO-8601 format.\n
        """
        timemagic = lambda mjd : mjd_to_datetime(mjd, isoformat)
        return list(map(timemagic, self.timeseries.index.values))


    #   Generates an identical deep copy of this instance
    #   Removes NaNs if opted to do so
    def gen_deepclone(self, removeNans=False):
        """
        Returns a deep copy of the current object, if its parameter is set to 'True' then removes NaN data in the process\n
        """
        new_observation = copy.deepcopy(self)
        if removeNans:
            new_observation.ts_dropnans()    
        return new_observation

    
    #   Generate F Matrix off of missing data in timeseries
    def gen_F_matrix(self):
        """
        Generates the F matrix, made by the timeseries attribute rows that contain NaNs.\n
        """
        m = len(self.timeseries.index)      
        n = self.timeseries['Value'].isnull().sum()
        F = np.zeros((m,n))

        j = 0
            
        #   Loop through time-series looking for NaNs,
        for i in range(m):
            if math.isnan(self.timeseries.iloc[i,0]):
                #   On indexes that have NaN's replace the 0 with 1
                F[i,j] = 1.0                             
                j += 1                 

        return F

    
    #   Drop all lines in timeseries that have NaNs
    def ts_dropnans(self):
        """
        Modifies timeseries attribute by deleting all rows that have NaNs.\n
        """
        self.timeseries = self.timeseries.dropna()
        self.__nan_share = 0.0
    

    #   Refreshes data from dictionary
    def ts_refresh_data(self):
        """
        Calls both load_observations and load_control methods.\n
        """
        self.load_control()
        self.load_observations()
    

    #   Switch indexes on timeseries with another list
    def ts_swap_indexes(self, indexes):
        """
        Switch current indexes in timeseries attribute to the ones in 'indexes'\n
        """
        if len(self.timeseries.index) == len(indexes):
            self.timeseries.index = indexes


    #   Append values to column_name in timeseries
    def ts_append_results(self, values, column_name='Estimate'):
        """
        Appends parameter 'values' into timeseries attribute under column 'Estimate'.\n
        """
        if len(values) == len(self.timeseries.index):
            self.timeseries[column_name] = values
    

    #   Plot the columns present in timeseries
    def ts_plot(self, save=False, path='timeseries_plot.png'):
        """
        Plots a representation of timeseries attribute.\n
        The plot may be saved in 'path'.\n
        """
        for column in self.timeseries.columns.to_list():
            if column == 'Value':
                plt.plot(self.get_indexes(), self.get_values(), 'o', label='Original Data', markersize=1)
            else:
                plt.plot(self.get_indexes(), self.get_column(column), label=column)

        plt.xlabel('Day', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.legend()
        
        if save:
            plt.savefig(path)
            print("Plot saved on:\n{0}".format(path))

        plt.show()
        

    #   Bundles and exports informatin regarding timeseries attribute
    def export_series(self, path='observations.json'):
        """
        Export this object's timeseries attribute into an observations file in .json format file located in 'path'.\n
        """
        #   The bundled information to be stored
        exportdict = {
            'Sampling period' : self.__sp,
            'Offsets'         : self.__offsets,
            'Observations'    : self.timeseries.to_dict(orient='index')
        }
        
        #   Use export function with path
        if writeToFile(exportdict, path):
            print('Successfully dumped series in file path:\n{0}'.format(path))
        else:
            print('Something went wrong when dumping series in file path in:\n{0}'.format(path))

        return exportdict


    #   Bundle current Observations object into a json file
    #   TODO : Maybe always store it in the same folder and parameter is just a name?
    def export_object(self, path='object.json'):
        """
        Export this object's state into a .json format file located in 'path'.\n
        """
        #   The bundled information to be stored
        exportdict = {
            'Control file path'      : self.__ctl_file,
            'Control info'           : self.__ctl_info,
            'Observations file path' : self.__obs_file,
            'Offsets'                : self.__offsets,
            'Nan share'              : self.__nan_share,
            'Sampling period'        : self.__sp,
            'Observations'           : self.timeseries.to_dict(orient='index')
        }
        
        #   Use export function with path
        if writeToFile(exportdict, path):
            print('Successfully dumped object in file path:\n{0}'.format(path))
        else:
            print('Something went wrong when dumping object in file path in:\n{0}'.format(path))

        return exportdict
    