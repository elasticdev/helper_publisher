from ed_helper_publisher.utilities import convert_str2json

def convert_ed_output_to_values(output):

    record_on = None
    values = []

    for line in output.split("\n"):
        if "_ed_begin_output" in line:
            record_on = True
            continue
        if "_ed_end_output" in line:
            record_on = None
            continue
        if not record_on: continue
        values.append(line)

    print "Try to convert an object"

    obj_return = "\n".join(values)
    print ''
    print ''
    print values
    print ''
    print ''
    obj_return = convert_str2json(obj_return)
    #try:
    #    obj_return = convert_str2json(obj_return)
    #except:
    #    print 'WARN: Cannot convert to json'

    return obj_return
