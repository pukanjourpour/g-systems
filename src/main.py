from lsystem import lsystem
from interpreter import Interpreter

import soundfile as sf
import os.path as path
import json
import time

def main(output_name, input_path, params, axiom, rules, iterations):
    word = lsystem(axiom, rules, iterations)

    print(f"String size: {len(word)}")


    # Process signal

    source_signal, samplerate = sf.read(input_path, dtype='float32')

    gran = Interpreter(source_signal, samplerate, **params)

    start = time.time()
    result_signal = gran.interpret(word)
    end = time.time()

    print(f"Took {end - start}s to compute.")     
    print(f"Original signal duration: {len(source_signal) / samplerate}s")
    print(f"Processed signal duration: {len(result_signal) / samplerate}s")


    # Write output

    sf.write(path.join("../output", f"{output_name}.wav"), result_signal, samplerate)


    # Write metadata

    info = {
        "params": params,
        "lsystem": {
            "axiom": axiom,
            "rules": rules,
            "iterations": iterations
        }
    }

    with open(path.join("../output", f"{output_name}.json"), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=4)
        
    # gran.plot()
    


if __name__ == "__main__":
    output_name = "output"
    input_path = "../media/strings.wav"

    # Interpreter params
     
    params = {
        # index is the branching depth, value is pitch shift in semitones
        "scale": [0, -12, 10, 0],         
        # "scale": [0, 3, 5, 7, 10, -5],         
        # by how many samples each "+" or "-" shifts the carrier
        "carrier_change_samples": 50,         
        # initial grain size in milliseconds 
        "init_grain_size_ms": 100,              
        # by how many milliseconds each "D" or "d" changes the grain duration
        "grain_size_change_ms": 20,             
        # minimum grain size in milliseconds
        "min_grain_size_ms": 20,
        # maximal grain size in milliseconds
        "max_grain_size_ms": 2000,              
        # fraction of the grain covered by the next one, ranges from 0 to 1
        "init_overlap_amount": 0.6,           
        # by how much each "T" or "t" changes the overlap amount 
        "overlap_amount_change": 0.01,        
        # if there are 2+ consecutive branches, how much overlap is between them 
        "branch_overlap_amount": 0.8,           
        # initial carrier position, expressed as a fraction of the input signal 
        "init_carrier_position": 0.12             
    }


    # Define L-System

    axiom = "F"

    rules = {
        "F": "F++F[DDDFFF]TTT[+++++++++++++++FF]tF---ttF",
    }

    iterations = 5
    
    main(output_name, input_path, params, axiom, rules, iterations)
    






