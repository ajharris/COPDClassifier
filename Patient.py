from distutils.dir_util import copy_tree

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

    def getCOPDStatus(self):
        return self._COPD

    def addDicomFolder(self, folder):
        self._dicomFolder=folder

    def setSubFolders(self, subfolders):
        self._subfolders = subfolders
        self._hasDirectoryTree = True

    def getSubFolders(self):
        return self._subfolders

    def getNumber(self):
        return str(self._number)

    def copyFolders(self, destination):
        category = 'COPD' if self.getCOPDStatus() else 'NCOPD'
        destination = destination + '/' + category + '/' + str(self._number)
        if not os.path.exists(destination):
            os.makedirs(destination)
        try:
            copy_tree(self._dicomFolder, destination)
        except:
            print("Error with: " + self._number)


