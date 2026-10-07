from src.lsystem import lsystem
from src.interpreter import Interpreter

import soundfile as sf
from os import path, makedirs
import json
import time

def main(config):
    output_name = config["output_file_name"] 
    output_dir = config["output_dir_path"]
    input_path = config["input_file_path"]
    params = config["params"]
    axiom = config["lsystem"]["axiom"]
    rules = config["lsystem"]["rules"]
    iterations = config["lsystem"]["iterations"]
    
    
    word = lsystem(axiom, rules, iterations)

    print(f"String size: {len(word)}")


    # Process signal

    source_signal, samplerate = sf.read(input_path, dtype='float32', always_2d=True)

    gran = Interpreter(source_signal, samplerate, **params)

    start = time.time()
    result_signal = gran.interpret(word)
    end = time.time()

    print(f"Took {end - start}s to compute.")     
    print(f"Original signal duration: {len(source_signal) / samplerate}s")
    print(f"Processed signal duration: {len(result_signal) / samplerate}s")


    # Write output
    
    directory = path.join(output_dir, output_name)
    
    if not path.exists(directory):
        makedirs(directory)

    sf.write(path.join(directory, f"{output_name}.wav"), result_signal, samplerate)

    with open(path.join(directory, f"{output_name}.json"), 'w') as f:
        json.dump(config, f)
    
    # gran.plot()
    

if __name__ == "__main__":
    
    with open('./config.json') as f:
        config = json.load(f)
    
    main(config)
        
    






