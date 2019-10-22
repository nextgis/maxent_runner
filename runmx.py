import argparse
import os
import sys
import platform
import random
import datetime
import string
import csv
import glob
import tempfile


from rasterize import rasterize

#python runmx.py

#java -mx512m -jar maxent.jar environmentallayers=layers togglelayertype=ecoreg samplesfile=samples\bradypus.csv outputdirectory=outputs redoifexists autorun

#Short example:
#python runmx.py --input samples\bradypus.csv --env layers --features linear,quadratic --of logistic

#Full example:
#python runmx.py --input samples\bradypus.csv --env layers --features linear,quadratic,product,threshold,hinge --of logistic --curves --jack --maxit 600

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
parser.add_argument('--maxit',type=int)
parser.add_argument('--prev',type=int)
parser.add_argument('--thr',type=str,choices=['fix1','fix5','fix10','min','perc10','equaltrain','maxtrain','equaltest','maxtest','equate'])
parser.add_argument('--bias_shp',type=str)
parser.add_argument('--bias_buffer',type=float)
parser.add_argument('--env',type=str,required=True)
parser.add_argument('--envno',type=str)
parser.add_argument('-r','--reproject',action="store_true")
arguments = parser.parse_args()


class ParamAnalyser:
    def __init__(self, args):
        self._args = args
        self.date = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")

        self._output_dir = 'outputs'
        self._input_file = ''
        self._bias_file = ''
        
        self._prepare_output()
        self._prepare_input()
        self._check_env()
        self._prepare_bias()

    def _prepare_output(self):
        if not os.path.exists(self._output_dir): 
            os.mkdir(self._output_dir)
        os.mkdir(self.output)
        
    def _prepare_input(self):
        if not os.path.exists(self._args.input): 
            print('Input species data are missing. Exiting.')
            sys.exit(1)
        if self.reproject: 
            reproject_input(self.input, self.output)
            input = os.path.join(output, 'input.csv')
        else:
            input = self._args.input
        self._input_file = input
 
    def _check_env(self):
        if not os.path.exists(self.env): 
            print('Environmental variables folder does not exist. Exiting.')
            sys.exit(1)

    def _prepare_bias(self):
        if not self.bias_shp is None:
            files = []  # list of env files
            for l in glob.glob(os.path.join(self.env,'*.asc')):
                files.append(l)
            self._bias_file = tempfile.mktemp('.asc')
            # we can use any of env file as template => use file[0]
            rasterize(self.bias_shp, files[0], self.bias_buffer, self._bias_file)

 
    @property
    def output(self):
        hash = ''.join(random.choice(string.ascii_letters) for _ in range(6))
        output = self.date #+ '_' + hash
        output = os.path.join(self._output_dir, output)

        return output
    
    @property
    def input(self):
        return self._input_file
      
    @property
    def reproject(self):
        return self._args.reproject

    @property
    def env(self):
        return self._args.env

    @property
    def envcat(self):
        envcat = ''
        for l in glob.glob(os.path.join(self.env,'*.asc')):
            if os.path.exists(l + '.cat'):
                envcat = envcat + ' -t ' + l.replace('.asc','').replace(env,'').replace('\\','')
        return envcat
 
    @property
    def feat(self):
        feat = ' '
        if self._args.features:
            if 'linear' not in self._args.features: feat = feat + ' nolinear '
            if 'quadratic' not in self._args.features: feat = feat + ' noquadratic '
            if 'product' not in self._args.features: feat = feat + ' noproduct '
            if 'threshold' not in self._args.features: feat = feat + ' nothreshold '
            if 'hinge' not in self._args.features: feat = feat + ' nohinge '
            if 'auto' not in self._args.features: feat = feat + ' noautofeature  '

        return feat
 
    @property
    def of(self):
        of = ''
        if self._args.of: 
            of = ' outputformat=' + self._args.of
        return of 

    @property
    def curves(self):
        curves = ' responsecurves'  if self._args.curves else "" 
        return curves

    @property
    def jack(self):
        jack = ' jackknife' if self._args.jack else ''
        return jack
 
    @property
    def rnd(self):
        if self._args.rnd: 
            rnd = ' randomtestpoints=' + str(self._args.rnd) 
        else:
            rnd =  ""
        return rnd

    @property
    def reg(self):
        if self._args.reg: 
            reg = ' betamultiplier=' + str(self._args.reg) + '.0' 
        else:
            reg = ""
        return reg

    @property
    def max(self):
        if self._args.max: 
            max = ' maximumbackground=' + str(self._args.max) 
        else:
            max = ""
        return max

    @property
    def rep(self):
        rep = ''
        if self._args.rep > 1: 
            rep = ' replicates=' + str(self._args.rep)
            rnd = '' #reset otherwise there is a popup that needs to be clicked
            if self._args.rnd: print('rnd set to null as replicates > 1')
        return rep

    @property
    def reptype(self):
        reptype = ''
        if self._args.reptype == 'boot': 
            reptype = ' replicatetype=bootstrap'
        if self._args.reptype == 'subsample':
            if self.rnd == '':
                print('Subsample replicates require nonzero random test % (rnd). Exiting')
                sys.exit(1)
            else:
                reptype = ' replicatetype=subsample'
        return reptype

    @property
    def rndseed(self):
        rndseed = ''
        if self._args.reptype == 'boot': 
            rndseed = ' randomseed'
        if self._args.reptype == 'subsample':
            if self.rnd == '':
                print('Subsample replicates require nonzero random test % (rnd). Exiting')
                sys.exit(1)
            else:
                rndseed = ' randomseed'
        return rndseed

    @property
    def noadds(self):
        if self._args.noadds: 
            noadds = ' noaddsamplestobackground'
        else:
            noadds = ""
        return noadds

    @property
    def maxit(self):
        if self._args.maxit: 
            maxit = ' maximumiterations=' + str(args.maxit)
        else:
            maxit = ""
        return maxit

    @property
    def prev(self):
        if self._args.prev: 
            prev = ' defaultprevalence=' + str(args.prev)
        else:
            prev = ""
        return prev

    @property
    def thr(self):
        thr = ' '
        if self._args.thr:
            if self._args.thr == 'fix1': thr = ' "applythresholdrule=fixed cumulative value 1" '
            if self._args.thr == 'fix5': thr = ' "applythresholdrule=fixed cumulative value 5" '
            if self._args.thr == 'fix10': thr = ' "applythresholdrule=fixed cumulative value 10" '
            if self._args.thr == 'min': thr = ' "applythresholdrule=minimum training presence" '
            if self._args.thr == 'perc10': thr = ' "applythresholdrule=10 percentile training presence" '
            if self._args.thr == 'equaltrain': thr = ' "applythresholdrule=equal training sensitivity and specificity" '
            if self._args.thr == 'maxtrain': thr = ' "applythresholdrule=maximum training sensitivity plus specificity" '
            #Next two are not recognized http://m-d.me/img/ss/20190207_165622.png
            if self._args.thr == 'equaltest': 
                thr = ' "applythresholdrule=????" '
                print('Error: Threshold rule equal test sensitivity and specificity not recognized')
                sys.exit(1)
            if self._args.thr == 'maxtest': 
                thr = ' "applythresholdrule=????" '
                print('Error: Threshold rule maximum test sensitivity plus specificity not recognized')
                sys.exit(1)
            if self._args.thr == 'equate': thr = ' "applythresholdrule=equate entropy of thresholded and original distributions" '

        return thr

    @property
    def envno(self):
        envno = ' '
        if self._args.envno:
            for envn in self._args.envno.split(','):
                envno = envno + ' -N ' + envn
        return envno

    @property
    def bias(self):
        bias = ""
        if self._bias_file != "":
            bias = ' biasfile="%s" ' % (self._bias_file)
        return bias
 
    @property
    def bias_shp(self):
        return self._args.bias_shp
 
    @property
    def bias_buffer(self):
        return self._args.bias_buffer
    
def reproject_input(input,output):
    from osgeo import ogr
    from osgeo import osr

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
        
    
def run(analyser, maxbin):
    params_str = 'environmentallayers=%s samplesfile=%s outputdirectory=%s' % (analyser.env, analyser.input, analyser.output)

    params = [
       analyser.feat,
       analyser.of,
       analyser.curves,
       analyser.jack,
       analyser.rnd,
       analyser.reg,
       analyser.max,
       analyser.rep,
       analyser.noadds,
       analyser.maxit,
       analyser.prev,
       analyser.thr,
       analyser.envno,
       analyser.envcat,
       analyser.bias,
    ]
    for p in params:
        if p != "":
            params_str += p
    
    if analyser.reptype != '':
        params_str = params_str + reptype
        params_str = params_str + rndseed

       
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

    analyser = ParamAnalyser(arguments)
    run(analyser, maxbin)
    
    print(analyser.date)
