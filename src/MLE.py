import numpy as np
import sys
import math
from scipy.optimize import minimize
from Fullcov import Fullcov
from AmmarGrag import AmmarGrag

class MLE:

    def __init__(self, x, F, min_method, H, t):
        """ initialise class
        """

        #--- Copy observations and design matrix into class 
        self.x   = x
        self.H   = H
        self.F   = F
        self.cov = t

        (m,k) = self.F.shape
        self.m = m 
        self.N = self.m - k

        #--- FullCov or AmmarGrag
        if min_method == 'Fullcov':
            self.method = Fullcov()
        elif min_method == 'AmmarGrag':
            self.method = AmmarGrag()
        else:
            print('Unrecognizable minimization method.')
            sys.exit(0)



    def log_likelihood(self,param):
        """ Compute log likelihood value
        """

        #--- First, make sure noise parameters are inside range
        penalty = self.cov.compute_penalty(param)

        #--- Compute new covariance matrix
        t = self.cov.create_t(self.m,param)

        #--- least-squares
        [theta,C_theta,ln_det_C,sigma_eta] = \
		     self.method.compute_leastsquares(t,self.H,self.x,self.F)

        #--- Compute log-likelihood
        logL = -0.5 * (self.N*math.log(2*math.pi) + ln_det_C + \
				   2.0*(self.N)*math.log(sigma_eta) + self.N)

        return -logL + penalty



    def estimate_parameters(self):
        """ Using Nelder-Mead, estimate least-squares + noise parameters
        """


        #--- Create intial guess
        param0 = [0.1]*self.cov.Nparam

        #--- search for maximum (-minimum) log-likelihood value
        param = minimize(self.log_likelihood, param0, method='nelder-mead', options={'xatol':1.0e-4})

        #--- Now that noise parameters have been established, compute final
        #    values for the trajectory model
        t = self.cov.create_t(self.m, param.x)
        [theta, C_theta, ln_det_C, sigma_eta] = \
		      self.method.compute_leastsquares(t, self.H, self.x, self.F)

        return [theta, pow(sigma_eta,2.0)*C_theta, ln_det_C, sigma_eta, param.x]