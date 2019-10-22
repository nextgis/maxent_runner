# maxent_runner
Maxent wrapper

# Preparation

    Xvfb :2 -screen 0 800x600x24&
    export DISPLAY=:1


# Examples

Simple run:

    python runmx.py --input samples/bradypus.csv --env layers --features linear,quadratic

Advanced run:

    python runmx.py --input samples/bradypus.csv --env layers --features linear,quadratic --replicates  --jack --curves

    python runmx.py --input samples/bradypus.csv --env layers --features linear,quadratic --of logistic --bias_shp samples/vizits.shp --bias_buffer 2

