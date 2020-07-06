import math, sys

def x_printformat(theta, C_theta, ln_det_C, sigma_eta, offsets, cov_params, m):
    """
    x_printformat :
        Pretty format for an array returned from a leastsquares solution.

    Parameters
    ----------
    theta : list
        Solution array from a leastsquares solution.
        Array of estimated parameters
    C_theta : list
        Covariance of estimated parameters
        Diagonal of the matrix that has the variance of the estimated parameters on a leastsquares equation.
    offsets : list
        Index list of offsets shown on an observations file.
    ln_det_C : float
        log(det(C))
    sigma_eta : float
        Driving noise
    cov_params : list(float)
        Fraction and Kappa minimized
    m : int
        Total number of observations
        
    Returns
    -------
    prettyformat(strlist) : str
        Concatenation of all modified strings in the process, justified with padding if needed.
    """

    # =============================================================================================== #
    # HELPER FUNCTION
    # =============================================================================================== #

    def prettyformat(strlist):
        """
        prettyformat :
            Searches for ':' in string and padds string according to the biggest substring until ':' is recognized.
        
        Parameters
        ---------
        strlist : list
            List of string to be parsed.
        
        Returns
        -------
        tot : str
            All strings for 'strlist' parsed and concatenated.
        """


        left = []
        right = []

        #   Separate strings by left and right according to the ':' in it
        for elem in strlist:
            s = elem.split(':')
            left.append(s[0])
            right.append(s[1])
        
        #   Store the biggest string in left for reference when applying padding
        biggest = max(left, key=len)
        tot = ''

        for i, elem in enumerate(left):

            #   Calculate the padding needed for each string on the left
            pad_ammount = len(biggest) - len(elem)
            left[i] = elem.ljust(len(elem)+pad_ammount)

            #   Add an extra space if the leading char is a digit
            if right[i][1].isdigit():
                right[i] = right[i].rjust(len(right[i])+1)

            tot += left[i] + ' : ' + right[i]

        return tot


    # =============================================================================================== #
    # ACTUAL FUNCTION
    # =============================================================================================== #


    params = ['Nominal bias', 'Seasonal trend', 'Cosine yearly', 'Sine yearly', 'Cosine hyearly', 'Sine hyearly']
    strlist = []

    #   New variable for diagonal in C_theta
    new_c_theta = []
    for x in range(len(theta)):
        new_c_theta.append(math.sqrt(C_theta[x,x]))
    
    #   Format depends on number of offsets, since theta has at leasnt length of 6 (params)
    if len(offsets) == 0:
        #   Data without offsets
        for i, val in enumerate(theta):
            #   Multiply bias by seasonal value
            if i == 1:
                strlist.append('{0} : {1:.3f} +/- {2:.3f} mm\n'.format(params[i], val*365.25, new_c_theta[i]*365.25))    
            else:
                strlist.append('{0} : {1:.3f} +/- {2:.3f} mm\n'.format(params[i], val, new_c_theta[i]))    
    
    else:
        #   Format theta that arent offsets
        v_params = theta[:-len(offsets)]
        for i, val in enumerate(v_params):
            #   Multiply bias by seasonal value
            if i == 1:
                strlist.append('{0} : {1:.3f} +/- {2:.3f} mm\n'.format(params[i], val*365.25, new_c_theta[i]*365.25))    
            else:
                strlist.append('{0} : {1:.3f} +/- {2:.3f} mm\n'.format(params[i], val, new_c_theta[i]))

        #   Format the offsets
        v_offset = theta[-len(offsets):]
        for i, off in enumerate(offsets):
            strlist.append('Offset at {0} : {1:.3f} +/- {2:.3f} mm\n'.format(off, v_offset[i], new_c_theta[-len(offsets)+i]))

    #   Additional values outside theta
    strlist.append('Series length : {0}\n'.format(m))
    strlist.append('ln_det_C : {0:f}\n'.format(ln_det_C))
    strlist.append('sigma_eta : {0:f}\n'.format(sigma_eta))
    strlist.append('fraction : {0:f}\n'.format(cov_params[0]))
    strlist.append('kappa : {0:f}\n'.format(cov_params[1]))
        
    return prettyformat(strlist)
