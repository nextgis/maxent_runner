import argparse
import os

#python runmx.py

#java -mx512m -jar maxent.jar environmentallayers=layers togglelayertype=ecoreg samplesfile=samples\bradypus.csv outputdirectory=outputs redoifexists autorun

#c:\python27\python runmx.py --input samples\bradypus.csv --output outputs --env layers --features linear,quadratic,product,threshold,hinge

parser = argparse.ArgumentParser()
parser.add_argument('--input',type=str,required=True)
parser.add_argument('--output',type=str,required=True)
parser.add_argument('--features',type=str)
parser.add_argument('--of',type=str)
parser.add_argument('--curves',type=str)
parser.add_argument('--jack',type=str)
parser.add_argument('--rnd',type=str)
parser.add_argument('--reg',type=str)
parser.add_argument('--max',type=str)
parser.add_argument('--rep',type=str)
parser.add_argument('--reptype',type=str)
parser.add_argument('--adds',type=str)
parser.add_argument('--maxit',type=str)
parser.add_argument('--prev',type=str)
parser.add_argument('--thr',type=str)
parser.add_argument('--bias',type=str)
parser.add_argument('--env',type=str,required=True)
parser.add_argument('--envno',type=str)
args = parser.parse_args()

def prepare_params():

    input = args.input
    output = args.output
    if not os.path.exists(output): os.mkdir(output)
    env = args.env
    if not os.path.exists(env): 
        print('Environmental variables folder does not exist. Exiting.')
        sys.exit(1)
    
    feat_str = ''
    if args.features:
        if 'linear' not in args.features: feat_str = feat_str + ' nolinear '
        if 'quadratic' not in args.features: feat_str = feat_str + ' noquadratic '
        if 'product' not in args.features: feat_str = feat_str + ' noproduct '
        if 'threshold' not in args.features: feat_str = feat_str + ' nothreshold '
        if 'hinge' not in args.features: feat_str = feat_str + ' nohinge '
        if 'auto' not in args.features: feat_str = feat_str + ' noautofeature  '
    
    return env,input,output,feat_str

def run(env,input,output,feat_str):
    params_str = 'environmentallayers=%s togglelayertype=ecoreg samplesfile=%s outputdirectory=%s' % (env,input,output)
    
    if feat_str != '':
        params_str = params_str + feat_str
        
    cmd = 'java -mx512m -jar bin\\maxent.jar ' + params_str + ' redoifexists autorun' 
    print cmd
    os.system(cmd)
    
if __name__ == '__main__':
    env,input,output,feat_str = prepare_params()
    run(env,input,output,feat_str)









