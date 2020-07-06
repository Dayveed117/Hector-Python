import os, sys
import pandas as pd

#   Series of prompts to make a control file in json format on testfiles directory

def info():
    print('\nDataFile,') 
    print('DataDirectory,       related to mom files, should it be set manually?')
    print('OutputFile,\n') 
    print('DataFile            -> name of file with observations')
    print('Data Directory      -> directory where file with observations is stored')
    print('OutputFile          -> name of file with observations and estimated model in .mom format')
    print('Interpolate         -> yes | no')
    print('PhysicalUnit        -> the physical unit of the observations')
    print('ScaleFactor         -> a number to scale the observations (optional, default 1.0)')
    print('NoiseModels         -> chosen from any of the following set : White, FlickerGGM, RandomWalkGGM, Powerlaw, PowerlawApprox, ARFIMA, ARMA, GGM')
    print('SeasonalSignal      -> yes | no')
    print('HalfSeasonalSignal  -> yes | no')
    print('EstimateOffsets     -> yes | no')
    print('ScaleFactor2        ->  ?')
    print('PhysicalUnit2       ->  ?')
    print('MinimizationMethod  -> AmmarGrag | Fullcov')



def menuprompt():
    
    while True:
        try:
            op = int(input('Option : ').strip())
            if op >= 0 and op <= 3:
                return op
        except ValueError:
            print('Invalid input')    

def q1():
    
    possibleanswers = ["yes", "no"]

    while True:
        p = input('Interpolate : (yes | no) - ').strip()
        if p in possibleanswers:
            return p
        print('Invalid input')

def q2():
    
    possibleanswers = ["m", "mm", "nm"]

    while True:
        p = input('PhysicalUnit : (m | mm | nm) - ').strip()
        p = p.strip()
        if p in possibleanswers:
            return p
        else:
            print('Invalid input')

def q3():
    
    while True:
        try:
            op = float(input('ScaleFactor : ').strip())
            return op
        except ValueError as identifier:
            print('Invalid input')

def q4():

    possibleanswers = ['White', 'FlickerGGM', 'RandomWalkGGM', 'Powerlaw', 'PowerlawApprox', 'ARFIMA', 'ARMA', 'GGM']

    print('Noisemodels : Powerlaw becomes default model if user does not choose any')
    print(possibleanswers)
    print('You may choose more than 1, type EXIT to proceed\n')

    answers = []

    while True:
        p = input('-> ').strip()
        if p == 'EXIT':
            break
        if p in possibleanswers and p not in answers:
            answers.append(p)
            if len(answers) != 0:
                print(answers)
        else:
            print('Invalid input')

    #   Default option is Powerlaw
    if len(answers) == 0:
        answers.append("Powerlaw")

    return answers

def q5():
    
    possibleanswers = ["yes", "no"]

    while True:
        p = input('SeasonSignals : (yes | no) - ').strip()
        p = p.strip()
        if p in possibleanswers:
            return p
        print('Invalid input')

def q6():
    
    possibleanswers = ["yes", "no"]

    while True:
        p = input('HalfSeasonSignals : (yes | no) - ').strip()
        if p in possibleanswers:
            return p
        print('Invalid input')

def q7():
    
    possibleanswers = ["yes", "no"]

    while True:
        p = input('EstimateOffsets : (yes | no) - ').strip()
        if p in possibleanswers:
            return p
        print('Invalid input')

def q8():
    while True:
        try:
            op = float(input('Second ScaleFactor : ').strip())
            return op
        except ValueError as identifier:
            print('Invalid input')

def q9():
    
    possibleanswers = ["m", "mm", "nm"]

    while True:
        p = input('Second PhysicalUnit : (m | mm | nm) - ').strip()
        p = p.strip()
        if p in possibleanswers:
            return p
        else:
            print('Invalid input')

def q10():
    
    possibleanswers = ["AmmarGrag", "Fullcov", 'Default']

    while True:
        p = input('Minimization Method : (Fullcov | AmmarGrag | Default) - ').strip()
        if p in possibleanswers:
            return p
        print('Invalid input')


def questionaire():
    
    answers = []

    answers.append(q1())
    answers.append(q2())
    answers.append(q3())
    answers.append(q4())
    answers.append(q5())
    answers.append(q6())
    answers.append(q7())
    answers.append(q8())
    answers.append(q9())
    answers.append(q10())

    return answers



def export_to_json(values, d_path):
    
    newfile = ''

    while True:
        p = input('Create a new configuration? (yes | no)\n').strip()
        if p == 'yes':
            newfile = input('Save file as?\n').strip()

            #   Making sure file ends with .json
            if not newfile.endswith('.json'):
                newfile = newfile + '.json'
            
            #   Making sure we dont overwrite a file on purpose
            if os.path.exists(os.path.join(d_path, newfile)):
                p = input('File already exists, overwrite? (yes | no)\n').strip()
                if p == 'yes':
                    break
                elif p == 'no':
                    continue
            else:
                break

        elif p == 'no':
            newfile = 'ctl.json'
            break
        else:
            print('Invalid input')

    #   Keys vector
    keys = ['Interpolate', 'PhysicalUnit', 'ScaleFactor',
            'NoiseModels', 'SeasonSignal', 'HalfSeasonSignals',
            'EstimateOffsets', 'ScaleFactor2', 'PhysicalUnit2', 'MinimizationMethod']

    #   Creating time series with keys and values
    ts = pd.Series(values, keys)

    #   Concatenating newfile name with folder and finally exporting
    outfile = os.path.join(d_path, newfile)
    ts.to_json(outfile, orient='index', indent=4)
    print('File saved successfully in the following location :\n' + outfile)


#   Script to make a control file

def main():
    
    answers = []
    project_root = os.getcwd()
    control_path = os.path.join(project_root, 'hector_files\control_files')

    while True:

        print("\nControl file maker : \n\n\
        0 - Exit \n\
        1 - Info \n\
        2 - Start and/or Override current configuration\n\
        3 - Export to JSON\n")

        op = menuprompt()

        if op == 0:
            print('Glad i could help!')
            break

        elif op == 1:
            info()

        elif op == 2:
            answers = questionaire()
            
        elif op == 3:
            if len(answers) > 0:
                export_to_json(answers, control_path)
            else:
                print('Please run a configuration before exporting!')


if __name__ == "__main__":
    main()