import numpy

def loadStartTargetFromCalibData(filename='calibrationData.npz'):
    startTarget=0
    try:
        loaded = numpy.load(filename, allow_pickle=True)
        startTarget = loaded['startTarget']
        loaded.close()
    except Exception as e:
        print("Error loading calib data", e)
    return startTarget

if __name__ == "__main__":
    pass
