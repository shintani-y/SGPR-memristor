# SGPR-memristor
Code for "Accelerating Machine Learning-Based Memristor Compact Modeling Using Sparse Gaussian Process"

Modeling memristors using sparse Gaussian process regression.

## Preparation
- Install `Anaconda 4.10.1`
- Build a virtual environment with the following command:
    ```sh
    $ conda env create -f=./env_conda.yml
    ```
- Activate the virtual environment using the following command:
    ```sh
    $ conda activate py36_sgpr
    ```


## Execution Steps
1. Run `$ make train` to generate the model.
2. Run `$ make hspice` to convert the generated model into Verilog and execute it.

## Additional Information
The execution results of Hspice in step 2 are outputted in the `img/` directory.

## Explanation of Each File
```
data/ : The place to save csv data
HSPICE_*/ : The place to save Hspice files
img/ : The place to save figures outputted by matplotlib
save_sgpr/ : The place to save model data executed by Pyro
temp/ : Verilog-A templates files
utils/ : Utilities for the program
verilog/ : The place where Verilog-A files are located
params.py : The program that converts model data saved in save_sgpr/ into necessary data for Verilog-A
read_plot_mosfet.py : The program that reads data executed by hspice and outputs figures
sgpr_train_current.py : The program to generate a current prediction model with Pyro
sgpr_train_state.py : The program to generate a state prediction model with Pyro
sgpr_train.py : The program that runs sgpr_train_current.py and sgpr_train_state.py
```