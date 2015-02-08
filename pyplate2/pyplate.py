import struct
from collections import ordereddict


#used when unpacking during an extraction
BYTE, _BYTE_SIZE = "c", struct.calcsize("c") #extracted as a char because python does not have a null byte value
CHAR, _CHAR_SIZE = "c", struct.calcsize("c")
SCHAR, _SCHAR_SIZE = "b", struct.calcsize("b")
UCHAR, _UCHAR_SIZE = "B", struct.calcsize("B")
BOOL, _BOOL_SIZE = "?", struct.calcsize("?")
SHORT, _SHORT_SIZE = "h", struct.calcsize("h")
USHORT, _USHORT_SIZE = "H", struct.calcsize("H")
INT, _INT_SIZE = "i", struct.calcsize("i")
UINT, _UINT_SIZE = "I", struct.calcsize("I")
LONG, _LONG_SIZE = "l", struct.calcsize("l")
ULONG, _ULONG_SIZE = "L", struct.calcsize("L")
LLONG, _LLONG_SIZE = "q", struct.calcsize("q")
ULLONG, _ULLONG_SIZE = "Q", struct.calcsize("Q")
FLOAT, _FLOAT_SIZE = "f", struct.calcsize("f")
DOUBLE, _DOUBLE_SIZE = "d", struct.calcsize("d")


def template(name, **kwargs):
    template = {}
    template["name"] = name
    template["type"] = "template"
    template["members"] = ordereddict()
    template["member_values"]
    for member in kwargs:
        template["members"][member] = kwargs[member]
    return template

def _search_for_member_value(template, member_values, member_name):
    member_heirarchy = member_name.split(".")
    for index, member in enumerate(member_heirarchy):
        if member in tmeplate["members"]:
            # this is a nested template call. Make sure that there is another value being referenced inside
            # before committing to it, since there is no need to direct reference a template in its entirety
            # (you should only reference the template members)
            if isinstance(template["members"][member], dict) and index < len(member_heirarchy) - 1:
                return _search_for_member_value(template["members"][member], member_values[member], member_heirarchy[index:].join("."))
            else:
                #it's a tuple or string, lowest level it needs to be (chain references are allowed)
                if isinstance(template["members"][member], tuple) or isinstance(template["members"][member], str):
                    #check to see if the value has already been found
                    if member in template["member_values"]:
                        return member_values[member]

def extract_string_template(template, string, context=None):
    unpack_string = ""
    unpack_sequence_prepped = False
    for member in template["members"]:
        if isinstance(member, str):
            unpack_string += template["members"][member]
        elif isinstance(member, tuple):
            member_length_value = _search_for_member_value(template, member[1])
            unpack_string += "%s%s" % (member_length_value, member[0])
        elif isinstance(member, dict):
            #extract the templates member values now, we are about to extract
            #the child
            if unpack_sequence_prepped:
                struct.unpack(unpack_string, )
        else:
            raise TypeError





def extract_file_template(templat, fobj, context=None):
    pass

if __name__ = "__main__":
    my_temp = template(
        my_int = INT,
        my_char = CHAR,
        my_double = DOUBLE,
        my_inner_template = template(
            my_int2 = INT,
            my_dependant_value = (CHAR, 'outer_test.my_int'),
            my_other_dep_value = (CHAR, 'outer_test.inner_test.my_int2')
        )
    )
