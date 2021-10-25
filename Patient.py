from distutils.dir_util import copy_tree

import os
import re as regex
import pydicom
# import itk
import pickle


class Patient:
    _number = 0
    _COPD = True
    _hasDirectoryList = False
    _dicomSourceFolder = ''
    _dicomDestinationFolder = ''
    _subfolders = []
    _dicoms = []

    def __repr__(self):
        return 'Patient: ' + str(self._number) + ", COPD: " + str(self._COPD) + ' Number of DICOM sets: ' + str(
            len(self._subfolders))

    def __init__(self, number, COPD=True):
        self._number = number
        self._COPD = COPD

    def isReady(self):
        return self._hasDirectoryList

    def getCOPDStatus(self):
        return self._COPD

    def addDicomFolder(self, folder):
        self._dicomSourceFolder = folder

    def addDestinationFolder(self, destinationFolder):
        category = 'COPD' if self.getCOPDStatus() else 'NCOPD'
        destinationFolder = destinationFolder + '/' + category + '/' + str(self._number)
        self._dicomDestinationFolder = destinationFolder
        return True

    def setSubFolders(self, subfolders):
        self._subfolders = subfolders
        self._hasDirectoryList = True

    def getSubFolders(self):
        return self._subfolders

    def getNumber(self):
        return str(self._number)

    def copyCompleteFolderStructureAll(self, destination):

        if not os.path.exists(destination):
            os.makedirs(destination)
        try:
            copy_tree(self._dicomSourceFolder, destination)
        except FileNotFoundError:
            print("Error with: " + self._number)

    def getDicomImages(self):
        for root, subs, files in os.walk(self._dicomDestinationFolder):
            for folder in subs:
                if folder == 'dicom':
                    continue
                listOfDicoms = []
                if regex.search('V*', folder):
                    filePath = self._dicomDestinationFolder + "/" + folder + "/dicom"
                    for file in os.listdir(filePath):
                        if regex.search(".*.dcm", file):  # need to update filePath to be destination
                            try:
                                importName = filePath + '/' + file
                                image = pydicom.dcmread(importName)
                                listOfDicoms.append(image)
                            except FileNotFoundError:
                                print('Not a valid dicom')
                    len(listOfDicoms) > 0 and self._dicoms.append(listOfDicoms)
                self._dicoms.append(listOfDicoms)

    def getSpacing(self):
        uniqueSpacing = []
        for dicomSeries in self._dicoms:
            for dicom in dicomSeries:
                dicom.PixelSpacing not in uniqueSpacing and uniqueSpacing.append(dicom.PixelSpacing)
        return uniqueSpacing

    def storePatient(self):
        filename = self._dicomDestinationFolder + '/' + str(self._number)
        with open(filename, 'wb') as pickleFile:
            pickle.dump(self, pickleFile)

    def loadPatient(self):
        filename = self._dicomDestinationFolder + '/' + str(self._number)
        with open(filename, 'rb') as pickleFile:
            pickle.load(pickleFile)