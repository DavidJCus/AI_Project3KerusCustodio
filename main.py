from tkinter import *
from tkinter.filedialog import askopenfilename
import os
import subprocess

window = Tk()
window.title = "Enter files"
window.geometry("475x300")
window.eval('tk::PlaceWindow . center')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
claspPath = os.path.join(ROOT_DIR, 'clasp-3.3.2-win64.exe')

files = []  # Holds the content of opened files
attributeToNumber = {}  # Dictionary mapping words in atributes file to numbers for CLASP input
hcFeasibleObjects = []

#######################################################################################################
def setUpAttribute():
    attributes = files[0].split()
    # print(attributes)
    totalNumberOfAttributes = int(len(attributes) / 3)
    for a in range(1, totalNumberOfAttributes + 1):
        # assigning numbers to attributes. Either x or -x
        attributeToNumber[attributes[(a * 3 - 2)]] = a
        attributeToNumber[attributes[(a * 3 - 1)]] = -1 * a
        # print(attributes[(a*3-2)])
        # print(attributes[(a*3-1)])
    # print(attributeToNumber)
    return attributeToNumber


#######################################################################################################
def setupHardConstraints():
    # conversion replaces the words in the hard constraints file with their numeric value from attributeToNumber dict
    constraints = files[1].split()
    conversion = ' '.join(str(attributeToNumber.get(a, a)) for a in constraints)
    # print(constraints)
    # print(conversion)

    newNumbers = []  # this will store an array of the numbers we get after computing though the NOTs and ORs
    conversionSplit = conversion.split()
    num = int(len(conversionSplit))
    skip = 0
    lines = 1
    for b in range(num):
        if skip == 1:
            skip = 0
            continue
        if conversionSplit[b] == 'NOT' and b > 1 and conversionSplit[b - 1] != 'OR':
            # this adds the 0 and new line to the array of numbers.
            newNumbers.append(0)
            newNumbers.append('\n')
            lines += 1
        if conversionSplit[b] == 'NOT':
            # if there's a NOT, multiplies the next element by -1, adds it to the array, then skips computing
            # the next element
            number = -1 * int(conversionSplit[b + 1])
            newNumbers.append(number)
            skip = 1
            continue
        if conversionSplit[b] == 'OR':
            # if there's an OR, does nothing and just skips
            continue
        if conversionSplit[b] != 'NOT' or conversionSplit[b] != 'OR':
            # if there's no NOT or an OR, just adds the number to the array
            newNumbers.append(int(conversionSplit[b]))

    newNumbers.append(0)  # adds a 0 to the last line
    # print(conversionSplit)
    # print(newNumbers)

    """
    # this gets the unique attributes for the first line of CLASP CNF input
    uniqueAttributes = -1  # this method counts 0 as a unique value, so we account for that by starting at -1
    uniqueList = []
    num3 = int(len(newNumbers))
    for a in range(num3):
        if newNumbers[a] != '\n' and abs(int(newNumbers[a])) not in uniqueList:
            uniqueAttributes += 1
            uniqueList.append(abs(int(newNumbers[a])))
    """

    booleanVars = len(attributeToNumber) / 2

    # final string is going to be our input for CLASP
    finalString = "p cnf " + str(int(booleanVars)) + " " + str(lines) + "\n"
    num2 = int(len(newNumbers))
    for num in range(num2):
        if num < num2 and [num + 1] == '\n':
            finalString += str(newNumbers[num])
            continue
        if newNumbers[num] == '\n':
            finalString += str(newNumbers[num])
            continue
        finalString += str(newNumbers[num]) + " "
        if num == num2:
            finalString += str(newNumbers[num])
    #print(finalString)
    return finalString

#######################################################################################################
def claspInput():
    cmdInput = setupHardConstraints()
    # the executable for clasp should be in the same place as this program
    with open("Output.txt", "w") as text_file:
        text_file.write(str(cmdInput))
    claspIn = os.path.join(ROOT_DIR, 'clasp-3.3.2-win64.exe -n 0 Output.txt')
    # print(claspIn)
    claspExecute = subprocess.run(claspIn, stdout=subprocess.PIPE, text=True)
    # print(claspExecute.stdout)
    # print("executed")
    for line in claspExecute.stdout.splitlines():
        # print(line)
        if line.__contains__('SATISFIABLE'):
            print("Returned Satisfiable")
            # return 1
        elif line.__contains__('UNSATISFIABLE'):
            print("Returned Unsatisfiable")
            # return 0
        elif line.__contains__('UNKNOWN'):
            print("Returned Unknown")
            # return 2
        elif line.startswith('v'):
            hcFeasibleObjects.append(line)
    #print(hcFeasibleObjects)

#######################################################################################################
def setupPreferences():
# WE NEED A WAY TO KNOW WHICH PREFERENCE WE ARE WORKING WITH
# EACH BUTTON IS LINKED TO A CERTAIN INPUT FILE FOR THIS

    # preference replaces the words in the preference file with their numeric value from attributeToNumber dict
    preferences = files[2].split()
    #conversion = ' '.join(str(attributeToNumber.get(a, a)) for a in preferences)
    preferenceObjects = str(files[2]).splitlines()
    completePreferences = []
    penaltyAmount = []
    # each index in array holds the clasp code per line in preference file input
    # at least that is current goal
    
    for line in preferenceObjects:
        words = line.split()
        newLines= 1


        preferenceconversion = ' '.join(str(attributeToNumber.get(a, a)) for a in words)
        tempTest = preferenceconversion.split()
        # print("before")
        # print(tempTest)
        for pos in range(len(tempTest)):       
            if tempTest[pos] == 'NOT':
                # if there's a NOT, multiplies the next element by -1
                tempTest[pos + 1] = -1 * int(tempTest[pos + 1])
                tempTest[pos] = ""
                continue
            if tempTest[pos] == 'OR':
                # if there's an OR, does nothing and just skips
                tempTest[pos] = ""
                continue
            if tempTest[pos] == 'AND':
                # if there's an AND, we must start a new line in clasp
                # not sure how yet
                tempTest[pos] = '0\n'
                newLines += 1
                continue
        #print("after")
        penaltyAmount.append(tempTest[-1])
        tempTest.pop()
        #print(tempTest)
        # final string is going to be our input for CLASP
        booleanVars = len(attributeToNumber) / 2
        cnfString = "p cnf " + str(int(booleanVars)) + " " + str(newLines) + "\n"
        cnfString = cnfString + " ".join(str(chunk) for chunk in tempTest)
        cnfString = cnfString + ' 0'
        print(cnfString)
        
        

def runningPreferences():
    print("hi, will come back soon. On break.")        
        
        
"""       
def outputPenaltyLogic():
# fish AND wine     10
# wine OR cake      6
# beer AND beer OR beef AND NOT soup    7

def outputPossibilisticLogic():
# fish AND WINE     0.8
# wine OR cake      0.5
# beer AND beer OR beef AND NOT soup    0.6

def outputQualitativeLogic():        
# fish BT beef IF
# wine BT beer IF fish
# cake BT ice-cream IF soup
        
"""

#######################################################################################################
# FRONT END #
#######################################################################################################
def chooseFile():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    # print("You chose: " + filename)
    with open(filename) as f:
        lines = f.read().replace(',', '')
    # print(lines)
    files.append(str(lines))


def done():
    # print("You pressed done, here are the results")
    # print("First file: " + str(files[0]) + " Second File: " + str(files[1]) + " Third File: " + str(files[2]))
    # function to do calculations should go here
    setUpAttribute()
    claspInput()
    setupPreferences()
    window.destroy()  # if pressed first, then ends whole process


# #adding needed buttons
# attributesButton = Button(window, text="Select attributes file", command=chooseFile)
# constraintButton = Button(window, text="Select the hard constraints files", command=chooseFile)
# preferencesButton = Button(window, text="Select the preferences files", command=chooseFile)

# # creating windows of buttons and adding onto canvas
# attributesButtonWindow = myCanvas.create_window(350,100, anchor="c", window=attributesButton)
# constraintButtonWindow = myCanvas.create_window(350,130, anchor="c", window=constraintButton)
# preferencesButtonWindow = myCanvas.create_window(350,160, anchor="c", window=preferencesButton)


# define image
imagePath1 = os.path.join(ROOT_DIR, 'image.png')  # loads images.png no matter where the project is located
bg1 = PhotoImage(file=imagePath1)
# imagePath2 = os.path.join(ROOT_DIR, 'greyimage.png')
# bg2 = PhotoImage(file=imagePath1)
# create canvas
myCanvas = Canvas(window, width=500, height=500)
myCanvas.pack(fill="both", expand=True)
# myCanvas2 = Canvas(window, width=250, height=500)
# myCanvas2.pack(fill="both", expand=True)

# set image in canvas
myCanvas.create_image(0, 0, image=bg1)

# add a label
myCanvas.create_text(75, 60, text="Home", font=("Bierstadt", 10), fill="white")
myCanvas.create_text(75, 100, text="Help", font=("Bierstadt", 10), fill="white")
myCanvas.create_text(75, 140, text="Exit", font=("Bierstadt", 10), fill="white")


# add a drop down 

def selected(event):
    # if clicked.get() == "Select attributes file": popup to submit then execute below code
    Submit = Button(window, text="Submit", command=chooseFile)
    doneButton = Button(window, text="Done", command=done)
    myCanvas.create_window(350, 130, anchor="center", window=Submit)
    myCanvas.create_window(350, 190, anchor="center", window=doneButton)


options = [
    "Default",
    "Select attributes file",
    "Select the hard constraints files",
    "Select the preferences files"
]
# take in selected val
clicked = StringVar()
# set default val
clicked.set(options[0])

# provide a menu
ddl = OptionMenu(
    window,
    clicked,
    *options,
    command=selected
)
# putting a window on a window
ddlWindow = myCanvas.create_window(350, 100, anchor="center", window=ddl)
"""
# this seems to be working
attributesButton = Button(window, text="Select attributes file", command=chooseFile)
attributesButton.pack()
constraintButton = Button(window, text="Select the hard constraints files", command=chooseFile)
constraintButton.pack()
preferencesButton = Button(window, text="Select the preferences files", command=chooseFile)
preferencesButton.pack()
endButton = Button(window, text="Done", command=done)
endButton.pack(pady=20)
"""
window.mainloop()
#######################################################################################################