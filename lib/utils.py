def has(ending, files):
    return any(map(
        lambda x: x.endswith(ending),
        files
    ))

def hasnt(ending, files):
    return not any(map(
        lambda x: x.endswith(ending),
        files
    ))

def extract_name(somefile):
    return '.'.join(somefile.split('.')[:-1])

def get(ending, files):
    return list(filter(
        lambda x: x.endswith(ending),
        files
    ))[0]
