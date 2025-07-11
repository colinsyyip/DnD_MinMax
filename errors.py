def BadArgumentFromListErrorCheck(passed_value,
                                  accepted_values: list):
    if passed_value not in accepted_values:
        raise ValueError("Argument must be one of %s. Received '%s'." % 
                             (accepted_values, passed_value))
    else:
        return True
    

def NonNegativeIntegerCheck(passed_value):
    if passed_value < 0:
        raise ValueError("Argument must be a non-negative integer. Received '%s'" % passed_value)
    else: 
        return True