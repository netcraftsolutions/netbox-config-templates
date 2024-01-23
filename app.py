import json
from jinja2 import Environment, FileSystemLoader


with open('config-contexts/global.json') as f:
    config_context = json.load(f)

def vlan_parser(data, first_line_len=48, other_line_len=44):
    """
    Input: Unsorted list of vlan integers
    Output: Sorted string list of integers according to IOS-like vlan list rules

    1. Vlans are listed in ascending order
    2. Runs of 3 or more consecutive vlans are listed with a dash
    3. The first line of the list can be first_line_len characters long
    4. Subsequent list lines can be other_line_len characters
    """
    # Sort and remove duplicates
    sorted_list = sorted(set(data))

    parse_list = []
    idx = 0
    while idx < len(sorted_list):
        start = idx
        end = start
        while end < len(sorted_list) - 1:
            if sorted_list[end + 1] - sorted_list[end] == 1:
                end += 1
            else:
                break

        if start == end:
            # Single VLAN
            parse_list.append(str(sorted_list[idx]))
        elif start + 1 == end:
            # Run of 2 VLANs
            parse_list.append(str(sorted_list[start]))
            parse_list.append(str(sorted_list[end]))
        else:
            # Run of 3 or more VLANs
            parse_list.append(str(sorted_list[start]) + "-" + str(sorted_list[end]))
        idx = end + 1

    line_count = 0
    result = [""]
    for vlans in parse_list:
        # First line (" switchport trunk allowed vlan ")
        if line_count == 0:
            if len(result[line_count] + vlans) > first_line_len:
                result.append("")
                line_count += 1
                result[line_count] += vlans + ","
            else:
                result[line_count] += vlans + ","

        # Subsequent lines (" switchport trunk allowed vlan add ")
        else:
            if len(result[line_count] + vlans) > other_line_len:
                result.append("")
                line_count += 1
                result[line_count] += vlans + ","
            else:
                result[line_count] += vlans + ","

    # Remove trailing orphan commas
    for idx in range(0, len(result)):
        result[idx] = result[idx].rstrip(",")

    # Sometimes text wraps to next line, but there are no remaining VLANs
    if "" in result:
        result.remove("")

    return result


with open('context.json') as f:
    context = json.load(f)

environment =  Environment(loader=FileSystemLoader('./'),trim_blocks=True,lstrip_blocks=True)
environment.filters["vlan_parser"] = vlan_parser

template = environment.get_template('template2.j2')

final_config = template.render(context)

print(final_config)


