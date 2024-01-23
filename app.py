import json
from jinja2 import Environment, FileSystemLoader
from ansible_collections.ansible.netcommon import vlan_parser 

with open('config-contexts/global.json') as f:
    config_context = json.load(f)

environment =  Environment(loader=FileSystemLoader('./'))
template = environment.get_template('config-templates/base_switch.j2')

final_config = template.render(config_context)

print(final_config)


