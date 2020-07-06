import os, time
from support_print import x_printformat
from Observations import Observations
from DesignMatrix import DesignMatrix
from Covariance import Covariance
from MLE import MLE


#===============================================================================
# Subroutines
#===============================================================================


def fill_observations():
    
    project_root = os.getcwd()
    
    #   Path to Observations file and to Control file
    obs_file = os.path.join(project_root, "hector_files\\test_observations\synthethic.json")
    ctl_file = os.path.join(project_root, "hector_files\\test_control\default_pw.json")

    #   Create observations object with file paths
    o = Observations(ctl_file, obs_file)

    #   Reading control file into object
    o.load_control()

    #   Reading test observations file into object
    o.load_observations()

    #   or do both
    #o.refresh_data()

    return o


# ---------------------------------------------- #
# Test file
# ---------------------------------------------- #

project_root = os.getcwd()
object_folder = os.path.join(project_root, "hector_files\object_files")
figure_folder = os.path.join(project_root, "hector_files\\figures")

obs = fill_observations()

#   Variáveis relevantes
x = obs.get_values()
tsindexes = obs.get_indexes()
m = len(tsindexes)
sp = obs.get_sp()
offsets = obs.get_offsets()
noisemodels = obs.get_noisemodels()
F = obs.gen_F_matrix()
min_method = obs.get_min_method()

periods = [365.25, 182.625]

#   Create DesignMatrix
H = DesignMatrix.create_DesignMatrix(sp, offsets, tsindexes, periods)

#   Guess [fraction, kappa] values and create covariance model
param = [0.514662,-0.9] 
cov = Covariance(noisemodels)



# ---------------------------------------------- #
# MLE TEST 1 
# ---------------------------------------------- #
"""
#--- MLE
mle = MLE(x, F, 'Fullcov', H, cov)
print("Timing MLE fullcov...\n")

#--- run MLE
start_time = time.time()
[theta, C_theta, ln_det_C, sigma_eta, param] = mle.estimate_parameters()
end_time = time.time()

results = x_printformat(theta, C_theta, ln_det_C, sigma_eta, offsets, param, m)

#   Estimates
Ohat = H @ theta
obs.ts_append_results(Ohat, 'MLE_Fullcov')
"""

# ---------------------------------------------- #
# MLE TEST 2
# ---------------------------------------------- #

#--- MLE
mle2 = MLE(x, F, 'AmmarGrag', H, cov)
print("Timing MLE ammar...\n")

#--- run MLE
start_time2 = time.time()
[theta, C_theta, ln_det_C, sigma_eta, param] = mle2.estimate_parameters()
end_time2 = time.time()

results2 = x_printformat(theta, C_theta, ln_det_C, sigma_eta, offsets, param, m)


#   Estimations
Ohat2 = H @ theta
obs.ts_append_results(Ohat2, 'MLE_Ammar')


# ---------------------------------------------- #
# Results
# ---------------------------------------------- #

"""
#   Fullcov results
print(results)
print("--- {0:8.3f} seconds ---\n".format(end_time - start_time))
"""

#   AmmarGrag results
print(results2)
print("--- {0:8.3f} seconds ---\n".format(end_time2 - start_time2))
print(obs.timeseries.head(5))


figure_path = os.path.join(figure_folder, 'figure.png')
object_path = os.path.join(object_folder, 'state.json')

#obs.export_object(object_path)
#obs.export_series(obs.get_ctl)

obs.ts_plot()
