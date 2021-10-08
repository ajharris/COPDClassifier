import pydicom
import os

class Patient:
    _number = 0
    _COPD = True
    _hasDirectoryTree = False
    _dicomFolder = ''
    _subfolders = []

    def __repr__(self):
        return 'Patient: ' + str(self._number) + ", COPD: " + str(self._COPD) + ' Number of DICOM sets: ' + str(len(self._subfolders) )

    def __init__(self, number, COPD=True):
        self._number = number
        self._COPD = COPD

    def isReady(self):
        return self._hasDirectoryTree

    def addDicomFolder(self, folder):
        self._dicomFolder=folder

    def setSubFolders(self, subfolders):
        self._subfolders = subfolders
        self._hasDirectoryTree = True

    def getSubFolders(self):
        return self._subfolders

    def getNumber(self):
        return str(self._number)

    # def loadImageSets(self):

