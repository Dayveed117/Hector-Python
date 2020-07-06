import sys, math
import numpy as np

class DesignMatrix:

    @classmethod
    def create_DesignMatrix(cls, sp, offsets, tsindexes, periods):
        """
        create_DesignMatrix :
            Creates a Design matrix according to specifications in its arguments.

        Parameters
        ----------
        sp : float
            A certain timeseries object sampling period attribute.
        offsets : list
            List that contains the indexes whose observation value is considered an offset.
        tsindexes : list
            List that contains the timeseries' indexes.
        periods : list
            List of periodic signals in unit days.

        Returns
        -------
        H : numpy [m,n]
            Design Matrix for the specified arguments.
        """
        

        #--- small number
        EPS = 1.0e-4

        #--- How many periods and offsets do we have?
        n_periods = len(periods)
        n_offsets = len(offsets)

            
        #   Number of observations
        m = len(tsindexes)
        if m == 0:
            print('Zero length of time series!? am crashing...')
            sys.exit()
            
        n = 2 + 2 * n_periods + n_offsets
        H = np.zeros((m,n))
        
        for i in range(0,m):
            
            H[i,0] = 1.0
            H[i,1] = i - 0.5 * (m-1)

            #   Calculate value with each periodic signals    
            for j in range(0, n_periods):
                H[i, 2+2*j+0] = math.cos(2*math.pi * i * sp/periods[j])
                H[i, 2+2*j+1] = math.sin(2*math.pi * i * sp/periods[j])
            
            for k in range(0, n_offsets):
                if offsets[k] < tsindexes[i] + EPS:
                    H[i, 2+2*n_periods+k] = 1.0
                    
        #   Return the design matrix
        return H
