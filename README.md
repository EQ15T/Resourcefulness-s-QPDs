# s-QPDs Project

## Overview
This code implement Algorithm 1 of the research work: Frigerio, M., Debray, A., Treps, N., & Walschaers, M. (2024). Resourcefulness of non-classical continuous-variable quantum gates. arXiv preprint arXiv:2410.09226.


## Usage
To use the functions provided in `s-QPDs.py`, you can import the module in your Python scripts. 
The code takes as input a circuit 'test' of the form 'S1.2,3R-0.5,2C0.0,4L3,1B-2.5,2,5', where each gate is parameterized by a letter (S,R,C,B,L), an integer (the mode on which the gate acts), and a real number (the corresponding parameter of the gate). 
The circuit has to be provided in the right form and order by the user.

The code then asks the user to input the non-classical depth of his input state, in the form: 'X,X,X,X' where X is a real number between -1 and 1. The number of X must be equal to the number of modes.

If the computation can be done according to each transfer function, then the code asks for the non-classical depth of the measurement process, that needs to be inputted the same way.

If not, the code will tell you at which gate your process becomes unsimulable in the sense of Algorithm 1. 

We remind the reader that its code is not optimal, and results can only be concluded from if the scheme is classically simulated. In the research work, this algorithm is a conceptual way of computing the actual transfer functions of each gate and concluding on the resourcefulness of that specific gate.

## Contributing
Contributions to the s-QPDs project are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.


