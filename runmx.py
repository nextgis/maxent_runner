import argparse
import os
import sys
import platform
import random
import datetime
import string
from osgeo import ogr
from osgeo import osr
import csv

#python runmx.py

#java -mx512m -jar maxent.jar environmentallayers=layers togglelayertype=ecoreg samplesfile=samples\bradypus.csv outputdirectory=outputs redoifexists autorun

#Short example:
#python runmx.py --input samples\bradypus.csv --env layers --features linear,quadratic --of logistic

#Full example:
#python runmx.py --input samples\bradypus.csv --env layers --features linear,quadratic,product,threshold,hinge --of logistic --curves --jack

parser = argparse.ArgumentParser()
parser.add_argument('--input',type=str,required=True)
#parser.add_argument('--output',type=str,required=True)
parser.add_argument('--features',type=str)
parser.add_argument('--of',type=str,choices=['cloglog','logistic','cumulative','raw'])
parser.add_argument('--curves',action="store_true")
parser.add_argument('--jack',action="store_true")
parser.add_argument('--rnd',type=int)
parser.add_argument('--reg',type=int)
parser.add_argument('--max',type=int)
parser.add_argument('--rep',type=int)
parser.add_argument('--reptype',type=str,choices=['cross','boot','subsample'])
parser.add_argument('--noadds',action="store_true")
parser.add_argument('--maxit',type=str)
parser.add_argument('--prev',type=str)
parser.add_argument('--thr',type=str)
parser.add_argument('--bias',type=str)
parser.add_argument('--env',type=str,required=True)
parser.add_argument('--envno',type=str)
parser.add_argument('-r','--reproject',action="store_true")
args = parser.parse_args()

def prepare_params():
    
    #output = args.output
    if not os.path.exists('outputs'): os.mkdir('outputs')
    hash = ''.join(random.choice(string.ascii_letters) for _ in range(6))
    date = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
    output = date #+ '_' + hash
    os.mkdir(os.path.join('outputs',output))
    output = os.path.join('outputs',output)
    
    input = args.input
    if not os.path.exists(input): 
        print('Input species data are missing. Exiting.')
        sys.exit(1)
    if args.reproject: 
        reproject_input(input,output)
        input = os.path.join(output,'input.csv')
    
    env = args.env
    if not os.path.exists(env): 
        print('Environmental variables folder does not exist. Exiting.')
        sys.exit(1)
    
    feat = ' '
    if args.features:
        if 'linear' not in args.features: feat = feat + ' nolinear '
        if 'quadratic' not in args.features: feat = feat + ' noquadratic '
        if 'product' not in args.features: feat = feat + ' noproduct '
        if 'threshold' not in args.features: feat = feat + ' nothreshold '
        if 'hinge' not in args.features: feat = feat + ' nohinge '
        if 'auto' not in args.features: feat = feat + ' noautofeature  '
    
    of = ''
    if args.of: of = ' outputformat=' + args.of
    
    curves = ''
    if args.curves: curves = ' responsecurves'
    
    jack = ''
    if args.jack: jack = ' jackknife'
    
    rnd = ''
    if args.rnd: rnd = ' randomtestpoints=' + str(args.rnd)
    
    reg = ''
    if args.reg: reg = ' betamultiplier=' + str(args.reg) + '.0'
    
    max = ''
    if args.max: max = ' maximumbackground=' + str(args.max)
    
    rep = ''
    if args.rep > 1: 
        rep = ' replicates=' + str(args.rep)
        rnd = '' #reset otherwise there is a popup that needs to be clicked
        if args.rnd: print('rnd set to null as replicates > 1')
    
    reptype = ''
    rndseed = ''
    if args.reptype == 'boot': 
        reptype = ' replicatetype=bootstrap'
        rndseed = ' randomseed'
    if args.reptype == 'subsample':
        if rnd == '':
            print('Subsample replicates require nonzero random test % (rnd). Exiting')
            sys.exit(1)
        else:
            reptype = ' replicatetype=subsample'
            rndseed = ' randomseed'
    
    noadds = ''
    if args.noadds: noadds = ' noaddsamplestobackground'
    
    return env,input,output,feat,of,curves,jack,rnd,reg,max,rep,reptype,rndseed,noadds

def reproject_input(input,output):
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)

    proj = '+proj=moll +lon_0=30 +x_0=3335846.22854 +y_0=-336410.83237 +datum=WGS84 +units=m +no_defs'
    target = osr.SpatialReference()
    target.ImportFromProj4(proj)

    transform = osr.CoordinateTransformation(source, target)
    
    with open(os.path.join(output,'input.csv'), mode='wb') as output_file:
        output_writer = csv.writer(output_file, delimiter=',')
        with open(input) as csv_file:
            csv_reader = csv.reader(csv_file)
            headers = next(csv_reader, None)
            output_writer.writerow(headers)
            for row in csv_reader:
                species = row[0]
                lon = row[1]
                lat = row[2]
        
                point = ogr.CreateGeometryFromWkt("POINT (%s %s)" % (lon,lat))
                point.Transform(transform)
                x = point.GetX()
                y = point.GetY()
                output_writer.writerow([species, x, y])
        
    
def run(env,input,output,feat,of,curves,jack,rnd,reg,max,rep,reptype,rndseed,noadds):
    params_str = 'environmentallayers=%s samplesfile=%s outputdirectory=%s' % (env,input,output)
    
    if feat != '':
        params_str = params_str + feat
    
    if of != '':
        params_str = params_str + of
    
    if curves != '':
        params_str = params_str + curves
        
    if jack != '':
        params_str = params_str + jack
    
    if rnd != '':
        params_str = params_str + rnd
    
    if reg != '':
        params_str = params_str + reg
    
    if max != '':
        params_str = params_str + max
    
    if rep != '':
        params_str = params_str + rep
    
    if reptype != '':
        params_str = params_str + reptype
        params_str = params_str + rndseed
        
    if noadds != '':
        params_str = params_str + noadds
    
    cmd = 'java -mx512m -jar ' + maxbin + ' ' + params_str + ' redoifexists autorun' 
    print cmd
    os.system(cmd)
    
if __name__ == '__main__':
    if platform.system() == 'Linux':
        os.environ["DISPLAY"]=":2"
        #need to start X process if it doesn't exist
        cmd = 'Xvfb :2 -screen 0 800x600x24&'
        #os.system(cmd)

    maxbin = os.path.join('bin','maxent.jar')

    env,input,output,feat,of,curves,jack,rnd,reg,max,rep,reptype,rndseed,noadds = prepare_params()
    run(env,input,output,feat,of,curves,jack,rnd,reg,max,rep,reptype,rndseed,noadds)
