import numpy as np
import sys
import math

class Covariance:


    def __init__(self,noisemodels):
        """ initialise class

        Arguments
        ---------
        noisemodels (array string) : list of noise model names
        """

        self.noisemodels = noisemodels[:]
        self.Nmodels = len(self.noisemodels)
        self.Nparam = self.Nmodels-1  # weight parameters
        
        #--- Do we need to estimate additional noise parameters?
        for noisemodel in self.noisemodels:
            if noisemodel=='Powerlaw':
                self.Nparam += 1
            elif noisemodel=='White':
                self.Nparam += 0
           


    def get_Nparam(self):
        """ Return the number of parameters to estimate numerically
        
        Returns
        -------
        self.Nparam (int) : total number of parameters 
        """

        return self.Nparam


        
    def compute_fraction(self,i,param):
        """ Compute fraction of noise model i

        Arguments
        ---------
        i (int) : index of noise model
        param (array float) : parameters describing weight of noise models
        
        Returns
        -------
        fraction (float) : fraction of noise model
        """

        #--- Constant
        hpi = 2.0*math.atan(1.0)

        #--- compute fraction
        if self.Nmodels==1:
            return 1.0
        else:
            fraction = 1.0
            for j in range(0,i):
                fraction *= math.sin(hpi*param[j]);
            if i<self.Nmodels-1:
                fraction *= math.cos(hpi*param[i]);

        #--- Some range checks
        if fraction>1.0:
            fraction = 1.0

        return pow(fraction,2.0)
   


    def compute_penalty(self,param):
        """ penalty for each fraction outside the [0:1] range

        Arguments
        ---------
        param (list float) : fractions of each noise model (Nmodels-1)

        Returns
        -------
        penalty value (float)
        """

        #--- Constant
        LARGE = 1.0e8
 
        #--- first fractions
        penalty = 0.0
        for i in range(0,len(self.noisemodels)-1):
            if param[i]<0.0:
                penalty += (0.0-param[i])*LARGE
                param[i] = 0.0
            elif param[i]>1.0:
                penalty += (param[i]-1.0)*LARGE
                param[i] = 1.0

        #--- Extra penalties for noise model parameters
        k = len(self.noisemodels)-1
        for noisemodel in self.noisemodels:
            method = getattr(self,'penalty_{0:s}'.format(noisemodel))
            penalty += method(k,param)

        return penalty



    def create_t(self,m,param):
        """

        Arguments
        ---------
        m (int) : length of time series
        param (array float) : array of parameters to estimate

        Returns
        -------
        t (array float) : first row of covariance matrix
        """

        #--- Create empty autocovariance array
        t = np.zeros(m)

        #--- Add autocovariance of each noise model
        k = self.Nmodels-1
        for i in range(0,self.Nmodels):
            fraction = self.compute_fraction(i,param)
            method = getattr(self,'create_{0:s}_t'.format(self.noisemodels[i]))
            t += fraction*method(m,k,param)

        return t



    def create_Powerlaw_t(self,m,k,param):
        """ Create first row of covariance matrix of power-law noise
    
        Arguments
        ---------
        m (int) : length of time series
        k (int) : index of param
        param (array float) : spectral index
        
        Returns
        -------
        t (row (m,1)   ) : first row Toeplitz covariance matrix 
        """

        #--- Constant
        EPS = 1.0e-6

        #--- Parse param
        kappa = param[k]
        k += 1   # increase k for next model

        #--- Create first row vector of Covariance matrix
        t = np.zeros(m)

        t[0] = math.gamma(1.0+kappa)/pow(math.gamma(1+0.5*kappa),2.0) 
        for i in range(1,m):
            t[i] = (i - 0.5*kappa - 1.0)/(i + 0.5*kappa) * t[i-1]

        return t 



    def create_White_t(self,m,k,param):
        """ Create first row of covariance matrix of white noise
    
        Arguments
        ---------
        m (int) : length of time series
        k (int) : index of param
        param (array float) : --- nothing ---
        
        Returns
        -------
        t (row (m,1)   ) : first row Toeplitz covariance matrix 
        """

        #--- Create first row vector of Covariance matrix
        t = np.zeros(m)
        t[0] = 1.0

        return t 


  
    def penalty_Powerlaw(self,k,param):
        """ Computes penalty for power-law noise

        Arguments
        ---------
        k (int) : index of param
        param (array float) : spectral index
        
        Returns
        -------
        penalty (float)
        """

        LARGE = 1.0e8
        penalty = 0.0 
        kappa = param[k]
        k += 1           # move one place for next model
        #--- Check range of parameters
        if kappa<-1.0:
            penalty += (-1.0 - kappa)*LARGE
            param[k-1] = -1.0 + 0.00001
        elif kappa>1.0:
            penalty += (kappa - 1.0)*LARGE
            kappa = 1.0
            param[k-1] = 1.0 - 0.00001
        return penalty


  
    def penalty_White(self,k,param):
        """ Computes penalty for power-law noise

        Arguments
        ---------
        k (int) : index of param
        param (array float) : --- nothing ---
        
        Returns
        -------
        penalty (float)
        """

        penalty = 0.0 
        return penalty
