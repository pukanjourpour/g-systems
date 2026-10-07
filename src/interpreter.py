import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

import pyrubberband as pyrb

from alive_progress import alive_bar

from scipy.interpolate import CubicSpline

class Interpreter():
    
    def __init__(self, source_signal, samplerate, **options):
        
        self._signal_length = source_signal.shape[0]
        self._source_signal = self._smoothen_ends(source_signal[:, 0])
        
        self._samplerate = samplerate
        
        self._scale = options.get("scale", [0])
        self._scale_ratios = np.pow(2, np.array(self._scale)/12)
        
        self._carrier_change_samples = int(samplerate * options.get("carrier_change_ms", 1) / 1000)
        self._min_grain_size_samples = int(self._samplerate * options.get("min_grain_size_ms", 10) / 1000) 
        self._max_grain_size_samples = int(self._samplerate * options.get("max_grain_size_ms", 1000) / 1000) 
        self._init_grain_size_samples = int(self._samplerate * options.get("init_grain_size_ms", 100) / 1000)
        self._grain_size_change_samples = int(self._samplerate * options.get("grain_size_change_ms", 1) / 1000) 
        self._grain_size_change_samples = int(self._samplerate * options.get("grain_size_change_ms", 1) / 1000) 
        self._init_nooverlap_amount = np.clip(1 - options.get("init_overlap_amount", 0.5), 0, 1)
        self._branch_nooverlap_amount = np.clip(1 - options.get("branch_overlap_amount", 0.5), 0, 1)
        self._overlap_amount_change = options.get("overlap_amount_change", 0.01)
        self._init_carrier_position = options.get("init_carrier_position", 0)
        
        self._trace = {}
        
        self._signal_layers = {}
        

    def _get_grain(self, start, duration):
        start =  start % self._signal_length
        if len(self._source_signal[start:]) >= duration:
            return self._source_signal[start:start+duration]
        else:
            part = self._source_signal[start:]
            rest = self._source_signal[:(duration - len(part))]
            combined = np.concatenate([part, rest])
            return combined

    def _smoothen_ends(self, signal):
        return signal * np.hanning(len(signal))
    
    
    def _insert_grain(self, signal, grain, idx):
        signal_size = len(signal)
        grain_size = len(grain)
        
        grain *= 0.8
        
        if idx + grain_size >= signal_size:
            diff = idx + grain_size - signal_size

            signal = np.pad(signal, (0, diff))            
            
        signal[idx:idx+grain_size] += grain

        return signal
    
    def _log(self, idx, duration, depth, forwards=True):
        # depth = str(depth)
        if depth not in self._trace:
            self._trace[depth] = []
        
        self._trace[depth].append((idx / self._samplerate, duration / self._samplerate, forwards))

    def plot(self):
        fig, ax = plt.subplots()

        # ax.set_yticks([0, 1, 2, 3])
        # ax.set_yticklabels([0, 1, 2, 3])
        
        jitter_init = 0.01
        
        for depth, intervals in self._trace.items():
            
            jitter = 0
            jitter_init = abs(jitter_init)
            
            for idx, values in enumerate(intervals):
                start, duration, forwards = values
                
                y = depth + np.random.uniform(-jitter, jitter)
                # y = depth
                
                y = depth + jitter
                jitter += jitter_init
                if jitter >= 0.05 or jitter <= -0.05:
                    jitter_init = -jitter_init 
                                    
                color = "yellow" if forwards else "red" 
                
                line = ax.hlines(y, start, start + duration,
                 color=color, linewidth=3)

                line.set_path_effects([
                    pe.Stroke(linewidth=3, foreground="black"),
                    pe.Normal(),
                ])

        ax.set_xlabel("Index")
        ax.set_ylabel("Depth")
        ax.grid(axis="x")

        plt.show()

    def _get_layer(self, depth):
        if depth not in self._signal_layers:
            self._signal_layers[depth] = np.array([])
        
        return self._signal_layers[depth]

    def _stretch_grain(self, grain, multiplier):
        stretched = grain
        if not multiplier == 1: 
            x = np.arange(len(grain))
            x_fine = np.linspace(start=x[0], stop=x[-1], num=int(x.size / multiplier))
            
            cs = CubicSpline(x, grain, bc_type='natural')
            stretched = cs(x_fine)
        
        return stretched

    def _interpret(self, 
                   word, 
                   letter_index=0, 
                   depth=0, 
                   carrier_pos_sample=0, 
                   grain_size=0, 
                   grain_nooverlap_amount=0, 
                   output_idx = 0):

        output_idx_branch = output_idx    
        
        layer_signal = self._get_layer(depth)
        
        i = letter_index
        
        start_output_idx = output_idx
        
        while i < len(word):  
            self._bar()  
            c = word[i]
            
            if c == "F":
                # Play a grain forwards
                   
                grain = self._get_grain(carrier_pos_sample, grain_size)
                
                ratio = self._scale_ratios[min(depth, len(self._scale_ratios) - 1)]
                grain = self._stretch_grain(grain, ratio)
                grain = self._smoothen_ends(grain)
                
                new_grain_size = grain.size
                
                layer_signal = self._insert_grain(layer_signal, grain, output_idx)
                self._log(output_idx, grain_size, depth)
                
                output_idx += int(new_grain_size * grain_nooverlap_amount)
                
                if output_idx_branch < output_idx:
                    output_idx_branch = output_idx
            elif c == "B":
                # Play a grain backwards
                
                grain = self._get_grain(carrier_pos_sample - grain_size, grain_size)
                grain = np.flip(grain)
                
                ratio = self._scale_ratios[min(depth, len(self._scale_ratios) - 1)]
                grain = self._stretch_grain(grain, ratio)
                grain = self._smoothen_ends(grain)
                
                new_grain_size = grain.size
                
                layer_signal = self._insert_grain(layer_signal, grain, output_idx)
                self._log(output_idx, grain_size, depth, forwards=False)
                
                output_idx += int(new_grain_size * grain_nooverlap_amount)
                
                if output_idx_branch < output_idx:
                    output_idx_branch = output_idx
            elif c == "[":
                # Branch recursively
                
                end_i, branch_length = self._interpret(
                    word=word, 
                    letter_index=i+1, 
                    depth=depth+1, 
                    carrier_pos_sample=carrier_pos_sample,
                    grain_size=grain_size,
                    grain_nooverlap_amount=grain_nooverlap_amount,
                    output_idx = output_idx_branch)
                
                i = end_i
                                
                output_idx_branch += int(branch_length * self._branch_nooverlap_amount)

            elif c == "]":
                # Merge the branch
                
                self._signal_layers[depth] = layer_signal
                length = grain_size + output_idx - start_output_idx
                return i, length
            elif c == "+":
                # Move carrier forwards
                
                carrier_pos_sample += self._carrier_change_samples
            elif c == "-":
                # Move carrier backwards
                
                carrier_pos_sample -= self._carrier_change_samples
            elif c == "T":
                # Decrease overlap
                
                grain_nooverlap_amount = np.clip(grain_nooverlap_amount + self._overlap_amount_change, 0, 1)
            elif c == "t":
                # Increase overlap
                
                grain_nooverlap_amount = np.clip(grain_nooverlap_amount - self._overlap_amount_change, 0, 1)                
            elif c == "D":
                # Increase grain duration
                
                if grain_size <= self._max_grain_size_samples - self._grain_size_change_samples:
                    grain_size += self._grain_size_change_samples
            elif c == "d":
                # Decrease grain duration
                
                if grain_size >= self._min_grain_size_samples + self._grain_size_change_samples:
                    grain_size -= self._grain_size_change_samples
            i += 1
            
        self._signal_layers[depth] = layer_signal
        return len(word) - 1, len(layer_signal)
    
    def interpret(self, word):
        
        with alive_bar(len(word)) as bar:
            self._bar = bar 
            self._interpret(word, 
                            carrier_pos_sample=int(self._init_carrier_position*self._signal_length), 
                            grain_size=self._init_grain_size_samples, 
                            grain_nooverlap_amount=self._init_nooverlap_amount
                            )
        
        result = np.array([])
        
        if len(self._signal_layers) > 0:

            for depth in range(len(self._signal_layers)):
                layer = self._signal_layers[depth]
                # layer = pyrb.pitch_shift(layer, self._samplerate, self._scale[min(depth, len(self._scale) - 1)])
                
                result = self._insert_grain(result, layer, 0)
        
        
        result = 0.95 * result / np.max(result)
   
        return result       