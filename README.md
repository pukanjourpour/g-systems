# How it works
 This program uses [L-systems](https://en.wikipedia.org/wiki/L-system) to manipulate an input sound. The chosen sound manipulations are based on the theory of [granular synthesis](https://en.wikipedia.org/wiki/L-system). 
 ## Grammar 
 In this L-system grammar, each variable and terminal can be represented with a "command" to the granular interpreter engine.
 ### Variables
 - ```F``` - play a grain forwards.
 - ```B``` - play a grain backwards. 
 ### Terminals
 - ```D``` / ```d``` - increase/decrease the duration of a grain. 
 - ```+``` / ```-``` - move the input carrier forwards/backwards.
 - ```T``` / ```t``` - decrease/increase grain overlap.
 
 ### Branching

 Terminals ```[``` and ```]``` denote branches that play in parallel with the content after the ```]```.  

# How to run
1. Create a venv and activate it.
2. ```pip install -r requirements.txt```
3. ```python main.py```

# config.json
```config.json``` controls allows tweaking the variables of the system.

- ```input_file_path``` full or root-relative path to the input audio file.
- ```output_dir_path``` output directory path.
- ```output_file_name``` output file name.

### Interpreter params
Found under ```params``` field.
 
- ```scale```
a list of integers, where index is the branching depth, value is pitch shift in semitones.
- ```carrier_change_ms``` 
controls by how many milliseconds each "+" or "-" shifts the carrier.
- ```init_grain_size_ms```
initial grain size in milliseconds.
- ```grain_size_change_ms```
controls by how many milliseconds each "D" or "d" changes the grain duration.
- ```min_grain_size_ms```
minimum grain size in milliseconds.
- ```max_grain_size_ms```
maximum grain size in milliseconds.
- ```init_overlap_amount```
fraction of the grain covered by the next one, ranges from 0 to 1.
- ```overlap_amount_change```
controls by how much each "T" or "t" changes the overlap amount.
- ```branch_overlap_amount```
if there are 2+ consecutive branches, how much overlap is between them.
- ```init_carrier_position```
initial carrier position, expressed as a fraction of the input signal.

### L-system definition
Found under ```lsystem``` field.

- ```axiom```
initial "sentence".
- ```rules```
an object containing key-value pairs, each encoding a rule. Key is the LHS, value is the RHS.
- ```iterations```
integer specifying how many iterations to run.