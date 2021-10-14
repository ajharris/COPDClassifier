'''
CopdClassifier - Adapted 10/8/2021 by andrew.harris@ryerson.ca

@author: srezvanj

Code will look along the path given for a .xlsx file, and use that to inform the organization of the images by patient

Image folders will be copied to folders for COPD or Non-COPD patients

To run from the command line, use python main.py <path to excel file/destination folder> <path to images source folder>

'''
import concurrent.futures
import os
import sys

import pandas as pd
from Patient import Patient

dataPath = ''
dicomFolder = ''
patients = []


def getStudyData(excelPath):
    for file in os.listdir(excelPath):
        if file.endswith('.xlsx'):
            excelPath = excelPath + '/' + file
            break
    return pd.read_excel(excelPath)

def listPatients(data):
    for i in range(0, len(data)):
        number = str(data.loc[i].at["Subjectid"])
        p = Patient(number, False) if data.loc[i].at['Study_group_GLI'] < 3 else Patient(number)
        patients.append(p)

def assignPatientDataPaths():
    for folder, subfolders, filename in os.walk(dicomFolder):
        for patient in range(0, len(patients)):
            if patients[patient].getNumber() in folder and not patients[patient].isReady():
                patients[patient].addDicomFolder(folder)
                patients[patient].setSubFolders(subfolders)

def cleanUpPatientList():
    listOfnonBlankPatients = []
    for patient in patients:
        if patient.getSubFolders():
            listOfnonBlankPatients.append(patient)
    return listOfnonBlankPatients

def makeSortedFolders(path):
    # Make folders for separated patient scans to be deposited
    not os.path.exists(path + '/COPD') and os.mkdir(path + '/COPD')
    not os.path.exists(path + '/NCOPD') and os.mkdir(path + '/NCOPD')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Set the paths for the location of the Excel data sheet and the CAT scan dicom data
    if len(sys.argv) > 1:
        dataPath = sys.argv[0]
        dicomFolder = sys.argv[1]
    else:
        if __debug__:
            dataPath = r'\\fs2.physics.ryerson.ca\a28harri\Documents\SortedDicoms'
            dicomFolder = r'R:\kirby_group\CanCOLD\Dicoms'
        else:
            dataPath = input('Provide the path to study data: ')
            dicomFolder = input('Provide the path to DICOM images: ')

    # subdivide the list of patients into COPD and NON-COPD classifications
    print("Sorting records.")
    data = getStudyData(dataPath)
    listPatients(pd.DataFrame(data, columns=['Subjectid', 'Study_group_GLI']))

    # match patient numbers with the path to their data, remove patients with no current images
    print("Removing empty records.")
    assignPatientDataPaths()
    patients = cleanUpPatientList()

    # create divided folders, copy patient data to appropriate location
    print("Creating sorted folders")
    makeSortedFolders(dataPath)

    print("Copying patient folders.")
    # executor = concurrent.futures.ProcessPoolExecutor(25)
    # futures = [executor.submit(patient.copyFolders, patient) for patient in patients]
    # concurrent.futures.wait(futures)
    for patient in patients:
        patient.copyFolders(dataPath)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

