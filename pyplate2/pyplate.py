import struct
from collections import OrderedDict

#debugging
from pprint import PrettyPrinter
pp = PrettyPrinter().pprint


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


def template(**kwargs):
    template = {}
    template["type"] = "template"
    template["members"] = OrderedDict()
    template["member_values"] = OrderedDict()
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
    unpack_member_sequence = []
    unpack_sequence_prepped = False
    for member in template["members"]:
        if isinstance(template["members"][member], str):
            #flag the sequence as ready to be extracted, since it is if need be.
            unpack_sequence_prepped = True
            unpack_string += template["members"][member]
            unpack_member_sequence.append(member)

        elif isinstance(template["members"][member], tuple):
            #
            #
            # COME BACK TO THIS. HOW SHOULD DEFAULT VALUES BE HANDLED? SKIPPED DURING EXTRACT?
            # OR SHOULD THEY BE EXTRACTED BY LENGTH?
            #
            #flag the sequence as ready to be extracted, since it is if need be.
            unpack_sequence_prepped = True
            if isinstance(template["members"][member][1], str):
                #self referenced value support
                member_length_value = _search_for_member_value(template, template["member_values"], template["members"][member][1])
            elif isinstance(template["members"][member][1], int) or isinstance(template["members"][member][1], float):
                #default value support
                member_length_value = template["members"][member][1]
                #add value to member values
                unpack_string += "%s%s" % (member_length_value, member[0])
                unpack_member_sequence.append(member)

        elif isinstance(template["members"][member], dict):
            #extract the templates member values now, we are about to extract
            #a child template
            if unpack_sequence_prepped:
                #get the string to the propper size to extract and unpack
                unpacked_values = struct.unpack(unpack_string, string[0:struct.calcsize(unpack_string)])
                for index, val_member in enumerate(unpack_member_sequence):
                    template["member_values"][val_member] = unpacked_values[index]
                #reset to default, we just extracted everything we could.
                unpack_sequence_prepped = False
                unpack_string = ""
                unpack_member_sequence = []
            #extract the template, we have our context now.
            template["member_values"][member] = extract_string_template(template["members"][member], string, template)

        else:
            #we cant parse this type. oops. freakout.
            raise TypeError

    #parse the string if it hasn't been parsed yet.
    if unpack_sequence_prepped:
        unpacked_values = struct.unpack(unpack_string, string[0:struct.calcsize(unpack_string)])
        for index, val_member in enumerate(unpack_member_sequence):
            template["member_values"][val_member] = unpacked_values[index]
    #everything is unpacked and stored, return it.
    return template






def extract_file_template(templat, fobj, context=None):
    pass

if __name__ == "__main__":
    my_template = template(
        test=INT,
        inner_template=template(
            test2=INT,
            test3=(INT,'test')
        )

    )
    my_value = extract_string_template(my_template, "12341234")
    pp(my_value)
