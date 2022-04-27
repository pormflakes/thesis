#IMPORT
from re import I
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *




#READ PANE DIMENSIONS
mycoord = open('C:/Users/ruben/Desktop/new/test.txt','r')
dataline = mycoord.readlines()
number_lines = len(dataline)
x_coord = []
y_coord =[]
for line in dataline:
    x = line.split (",")
    x_coord.append(float(x[0]))

mycoord.close()

GlassThickness = 12                              #GLASSTHICKNESS in mm   standaard maten:4,6,8,10,12
LoadMagnitude = 100                             #LOADMAGNITUDE  in N

########################



#PART CREATION AND LOOP 
for i in range (0,number_lines):
    PartName = 'item' + str(i+1)
    mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
    mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(0.0, 0.0), 
    point2=(x_coord[i], GlassThickness))                                               #CHANGE THIS TO CHANGE PANE DIMENSIONS
    mdb.models['Model-1'].Part(dimensionality=TWO_D_PLANAR, name=PartName, type= DEFORMABLE_BODY)
    mdb.models['Model-1'].parts[PartName].BaseShell(sketch=
    mdb.models['Model-1'].sketches['__profile__'])




#MATERIAL
mdb.models['Model-1'].Material(name='Glass')
mdb.models['Model-1'].materials['Glass'].Elastic(table=((70000, 0.23),))      #young's modulus in MPa and Poisson's ratio
mdb.models['Model-1'].materials['Glass'].Density(table=((2500.E-9, ), ))      #mass density



#DEFINE AND ASSIGN SECTION
for i in range (0,number_lines):
    PartName = 'item' + str(i+1)
    SectionName = 'section' + str(i+1)
    SetName = 'set' + str(i+1)
    mdb.models['Model-1'].HomogeneousSolidSection(material='Glass', name=
    SectionName, thickness=None)
    mdb.models['Model-1'].parts[PartName].Set(faces=
    mdb.models['Model-1'].parts[PartName].faces.getSequenceFromMask(('[#1 ]', ), 
    ), name=SetName)
    mdb.models['Model-1'].parts[PartName].SectionAssignment(offset=0.0, offsetField=
    '', offsetType=MIDDLE_SURFACE, region=
    mdb.models['Model-1'].parts[PartName].sets[SetName], sectionName=SectionName, 
    thicknessAssignment=FROM_SECTION)



#LOADINGSTEP
mdb.models['Model-1'].StaticStep(name='LoadStep', previous='Initial')


   
#ASSEMBLY
mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
for i in range(0,number_lines):
    a = str(i+1)
    InstName = 'item' + a + '-inst'
    PartName = 'item' + a
    SurfaceName = 'item' + a + '-topsurface'
    LoadName = 'load' + a
    SetNameLeft = 'BCSetLeft' + a
    SetNameRight = 'BCSetRight' + a
    Bclinks = 'bclinks' + a
    Bcrechts = 'bcrechts' + a
    mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name=InstName,
    part = mdb.models['Model-1'].parts[PartName])
    mdb.models['Model-1'].rootAssembly.instances[InstName].translate(vector=             #SPATIALLY DIVIDE INSTANCES
    (0.0, x_coord[i], 0.0))
    #SURFACE SELECTION
    mdb.models['Model-1'].rootAssembly.Surface(name=SurfaceName, side1Edges=
    mdb.models['Model-1'].rootAssembly.instances[InstName].edges.getSequenceFromMask(
    ('[#4 ]', ), ))
    #LOAD 
    mdb.models['Model-1'].Pressure(amplitude=UNSET, createStepName='LoadStep', 
    distributionType=UNIFORM, field='', magnitude=LoadMagnitude, name=LoadName, 
    region=Region(
    side1Edges=mdb.models['Model-1'].rootAssembly.instances[InstName].edges.getSequenceFromMask(
    mask=('[#4 ]', ), )))  
    #BOUNDARYCONDITION LEFT
    mdb.models['Model-1'].rootAssembly.Set(name=SetNameLeft, vertices=
    mdb.models['Model-1'].rootAssembly.instances[InstName].vertices.getSequenceFromMask(
    ('[#1 ]', ), ))
    mdb.models['Model-1'].DisplacementBC(amplitude=UNSET, createStepName='Initial', 
    distributionType=UNIFORM, fieldName='', localCsys=None, name= Bclinks
    , region=
    mdb.models['Model-1'].rootAssembly.sets[SetNameLeft], u1=SET, u2=SET, ur3=                  #ACTUAL BOUNDARY OCNDITION LEFT
    UNSET)
    #BOUNDARYCONDITION Right
    mdb.models['Model-1'].rootAssembly.Set(name=SetNameRight, vertices=
    mdb.models['Model-1'].rootAssembly.instances[InstName].vertices.getSequenceFromMask(
    ('[#2 ]', ), ))
    mdb.models['Model-1'].DisplacementBC(amplitude=UNSET, createStepName='Initial', 
    distributionType=UNIFORM, fieldName='', localCsys=None, name= Bcrechts
    , region=
    mdb.models['Model-1'].rootAssembly.sets[SetNameRight], u1=UNSET, u2=SET, ur3=               #ACTUAL BOUNDARY CONDITION RIGHT
    UNSET)
    #MESHING   
    mdb.models['Model-1'].parts[PartName].seedPart(deviationFactor=0.1, size=x_coord[i]/20)
    mdb.models['Model-1'].parts[PartName].generateMesh()
    


#FIELD OUTPUT REQUEST
mdb.models['Model-1'].FieldOutputRequest(createStepName='LoadStep', name=
    'MyFieldOutput', numIntervals=100, variables=(PRESELECT))    




#MAKE JOB AND RUN 
mdb.models['Model-1'].rootAssembly.regenerate()
mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
    explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
    memory=90, memoryUnits=PERCENTAGE, model='Model-1', modelPrint=OFF, 
    multiprocessingMode=DEFAULT, name='MyJob', nodalOutputPrecision=SINGLE, 
    numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='', type=
    ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
mdb.jobs['MyJob'].submit(consistencyChecking=OFF)

#wait until job is finished

wait = input("Press Enter to continue.")

#EVERYTHING THAT FOLLOWS IS ABOUT THE OUTPUT OF THE ANALYSIS

#PLOTTING THE OUTPUT

from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=109.160163879395, 
    height=108.900466918945)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from viewerModules import *
from driverUtils import executeOnCaeStartup



#open ODB-file created by previous script
o1 = session.openOdb(name='C:/Users/ruben/Desktop/new/MyJob.odb')
session.viewports['Viewport: 1'].setValues(displayedObject=o1)

#PLOT MISES OF EVERY POINT AS A FUNCTION OF TIME 

for i in range (0,number_lines):
    a = str(i+1)
    session.xyDataListFromField(odb=o1, outputPosition=INTEGRATION_POINT, 
        variable=(('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'), )), ), 
        elementSets=('ITEM'+a+'-INST.SET'+a, ))                                  #looping through all instances
    xQuantity = visualization.QuantityType(type=TIME)
    yQuantity = visualization.QuantityType(type=STRESS)


#send data to excel
import sys
sys.path.insert(34, 
    r'c:/SIMULIA/Abaqus/6.14-5/code/python2.7/lib/abaqus_plugins/excelUtilities')
import abq_ExcelUtilities.excelUtilities
abq_ExcelUtilities.excelUtilities.XYtoExcel(
    xyDataNames='S:Mises PI: ITEM1-INST E: 1 IP: 1', trueName='')
#: XY Data sent to Excel

#werkt dit?