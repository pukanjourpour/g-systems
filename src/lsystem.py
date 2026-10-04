def lsystem(axiom, rules, iterations):
    result = axiom
    
    for _ in range(iterations):
        new = ""
        
        for c in result:
            new += rules.get(c, c)
                
        result = new
    
    return result