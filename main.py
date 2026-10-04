from src.lsystem import lsystem
from src.interpreter import Interpreter

import soundfile as sf
import os.path as path
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

    source_signal, samplerate = sf.read(input_path, dtype='float32')

    gran = Interpreter(source_signal, samplerate, **params)

    start = time.time()
    result_signal = gran.interpret(word)
    end = time.time()

    print(f"Took {end - start}s to compute.")     
    print(f"Original signal duration: {len(source_signal) / samplerate}s")
    print(f"Processed signal duration: {len(result_signal) / samplerate}s")


    # Write output

    sf.write(path.join(output_dir, f"{output_name}.wav"), result_signal, samplerate)

        
    # gran.plot()
    


if __name__ == "__main__":
    
    with open('./config.json') as f:
        config = json.load(f)
    
    main(config)
        
    






