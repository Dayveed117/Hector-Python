import math
import pandas as pd
import numpy as np
from numpy import fft
import sys

class AmmarGrag:

    def compute_leastsquares(self, t, H, x, F):
        """
        AmmarGrag : 
            AmmarGrag minimization method
 
        Arguments
        ---------
        t (m*1 matrix) : first column of Toeplitz covariance matrix C
        H (m*n matrix) : design matrix
        y (m*1 matrix) : observations
        F (m*k matrix) : Missing data matrix
   
        Returns
        -------
        theta (n*1 matrix)    : estimated parameters
        C_theta  (n*n matrix) : covariance matrix of estimated parameters
        ln_det_C (float)      : log(det(C))
        sigma_eta (float)     : driving noise
        """

        #--- Get size of matrix H
        (m,n) = H.shape

        #--- Get size of matrix F which number of columns = count missing data
        (m,k) = F.shape

        #--- Durbin-Levinson to compute l1 and l2
        r = np.zeros(m-1)
        delta = t[0]
        ln_det_C = math.log(delta)
        for i in range(0,m-1):
            if i==0:
                gamma = -t[i+1]/delta
            else:
                gamma = -(t[i+1] + np.dot(t[1:i+1],r[0:i]))/delta
                r[1:i+1] = r[0:i] + gamma*r[i-1::-1]

            r[0] = gamma
            delta = t[0] + np.dot(t[1:i+2],r[i::-1])
            ln_det_C += math.log(delta)
    
        #--- create l1 & l2 using r
        l1 = np.zeros(2*m)
        l2 = np.zeros(2*m)

        l1[0]   = 1.0
        l1[1:m] = r[m-2::-1]
        l2[1:m] = r[0:m-1]

        #-- Scale l1 & l2
        l1 *= 1.0/math.sqrt(delta)
        l2 *= 1.0/math.sqrt(delta)

        #--- Perform FFT on l1 and l2
        Fl1 = fft.fft(l1)
        Fl2 = fft.fft(l2) 

        #--- Currently there might be NaN's in H and x. Make those zero
        xm = np.zeros(m)
        Hm = np.zeros((m,n))
        for i in range(0,m):
            if math.isnan(x[i])==True:
                xm[i]   = 0.0
                Hm[i,:] = 0.0
            else:
                xm[i]   = x[i]
                Hm[i,:] = H[i,:]

        #--- Create auxiliary matrices and vectors
        z   = np.zeros(m)
        Fx  = fft.fft(np.concatenate((xm,z)))
        y1  = (fft.ifft(Fl1 * Fx).real)[0:m]
        y2  = (fft.ifft(Fl2 * Fx).real)[0:m]

        #--- Design matrix
        A1 = np.zeros((n,m))
        A2 = np.zeros((n,m))
        for i in range(0,n):
            FH = fft.fft(np.concatenate((Hm[:,i].T,z)))
            A1[i,:] = (fft.ifft(Fl1 * FH).real)[0:m]
            A2[i,:] = (fft.ifft(Fl2 * FH).real)[0:m]

        #--- Only when there are missing data
        if k>0:

            #--- matrix F
            G1 = np.zeros((k,m))
            G2 = np.zeros((k,m))
            for i in range(0,k):
                FF = fft.fft(np.concatenate((F[:,i].T,z)))
                G1[i,:] = (fft.ifft(Fl1 * FF).real)[0:m]
                G2[i,:] = (fft.ifft(Fl2 * FF).real)[0:m]

            #--- Compute matrix M
            M = np.linalg.cholesky(G1 @ G1.T - G2 @ G2.T)

            #--- Update ln_det_C
            for i in range(0,k):
                ln_det_C += 2.0*math.log(M[i,i])

            #--- Compute QA and Qy
            Minv = np.linalg.inv(M)
            QA = Minv @ (G1 @ A1.T - G2 @ A2.T)
            Qy = Minv @ (G1 @ y1.T - G2 @ y2.T)

            #--- Least-squares
            C_theta = np.linalg.inv(A1 @ A1.T - A2 @ A2.T - QA.T @ QA)
            theta = C_theta @ (A1 @ y1.T - A2 @ y2.T - QA.T @ Qy) 
            
            #--- Compute sigma_eta
            t1 = y1 - A1.T @ theta
            t2 = y2 - A2.T @ theta

            #--- Compute Qt
            Qt = Minv @ (G1 @ t1.T - G2 @ t2.T)

            sigma_eta = math.sqrt((np.dot(t1,t1) - np.dot(t2,t2) \
						      - np.dot(Qt,Qt))/(m-k))
        else:
            #--- Least-squares with no missing data
            C_theta = np.linalg.inv(A1 @ A1.T - A2 @ A2.T)
            theta = C_theta @ (A1 @ y1.T - A2 @ y2.T) 

            #--- Compute sigma_eta
            t1 = y1 - A1.T @ theta
            t2 = y2 - A2.T @ theta
            sigma_eta = math.sqrt((np.dot(t1,t1) - np.dot(t2,t2))/m)


        return [theta,C_theta,ln_det_C,sigma_eta]