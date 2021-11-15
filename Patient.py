from distutils.dir_util import copy_tree

import os
import re as regex
import pydicom
import itk
import pickle


class Patient:
    _number = 0
    _COPD = True
    _hasDirectoryList = False
    _dicomSourceFolder = ''
    _dicomDestinationFolder = ''
    _nrrdGroupFolder = ''
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
        if not os.path.exists(self._dicomDestinationFolder):
            os.makedirs(self._dicomDestinationFolder)
        return True

    def setSubFolders(self, subfolders):
        self._subfolders = subfolders
        self._hasDirectoryList = True

    def getSubFolders(self):
        return self._subfolders

    def getNumber(self):
        return str(self._number)

    def copyCompleteFolderStructureAll(self):
        if not os.path.exists(self._dicomDestinationFolder):
            os.makedirs(self._dicomDestinationFolder)
        try:
            copy_tree(self._dicomSourceFolder, self._dicomDestinationFolder)
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
        for dicom in self._dicoms:
            itk.spacing(dicom) not in uniqueSpacing and uniqueSpacing.append(itk.spacing(dicom))
        return uniqueSpacing

    def storePatient(self):
        filename = self._dicomDestinationFolder + '/' + str(self._number)
        with open(filename, 'wb') as pickleFile:
            pickle.dump(self, pickleFile)

    def loadPatient(self):
        filename = self._dicomDestinationFolder + '/' + str(self._number)
        with open(filename, 'rb') as pickleFile:
            pickle.load(pickleFile)

    def loadSingleDicomFromSource(self, setNumber = 0):
        dirName = self._dicomSourceFolder + '/' + self._subfolders[setNumber] + '/dicom'
        PixelType = itk.ctype("signed short")
        Dimension = 3

        ImageType = itk.Image[PixelType, Dimension]

        namesGenerator = itk.GDCMSeriesFileNames.New()
        namesGenerator.SetUseSeriesDetails(True)
        namesGenerator.AddSeriesRestriction("0008|0021") #not sure what this does.
        namesGenerator.SetGlobalWarningDisplay(False)
        namesGenerator.SetDirectory(dirName)

        seriesUID = namesGenerator.GetSeriesUIDs()

        try:
            image = itk.imread(self._dicomDestinationFolder + '/' + seriesUID[0] + '.nrrd')
        except:
            for uid in seriesUID:
                seriesIdentifier = uid
                fileNames = namesGenerator.GetFileNames(seriesIdentifier)

                reader = itk.ImageSeriesReader[ImageType].New()
                dicomIO = itk.GDCMImageIO.New()
                reader.SetImageIO(dicomIO)
                reader.SetFileNames(fileNames)
                reader.ForceOrthogonalDirectionOff()

                outFileName = os.path.join(self._dicomDestinationFolder, seriesIdentifier + ".nrrd")

                writer = itk.ImageFileWriter[ImageType].New()
                writer.SetFileName(outFileName)
                writer.UseCompressionOn()
                writer.SetInput(reader.GetOutput())
                writer.Update()
            image = itk.imread(self._dicomDestinationFolder + '/' + seriesUID[0] + '.nrrd')

        self._dicoms.append(image)

    def writeNrrdToSortedFolder(self, path):
        if self.getCOPDStatus() is True:
            itk.imwrite(self._dicoms[0], path + '/COPD/' + str(self._number) + '.nrrd')
        else:
            itk.imwrite(self._dicoms[0], path + '/NCOPD/' + str(self._number) + '.nrrd')