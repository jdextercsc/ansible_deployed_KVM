#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Joseph Callen <jcallen () csc.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: virt_ipaddress
short_description: foo
description:
    - foo
version_added: 2.0
author: "Joseph Callen (@jcpowermac)"
notes:
    - Tested on vSphere 5.5
requirements:
    - "python >= 2.6"
    - PyVmomi
options:
    hostname:
        description:
            - The hostname or IP address of the vSphere vCenter API server
        required: True
    username:
        description:
            - The username of the vSphere vCenter
        required: True
        aliases: ['user', 'admin']
    password:
        description:
            - The password of the vSphere vCenter
        required: True
        aliases: ['pass', 'pwd']
'''

EXAMPLES = '''
'''

try:
    import json
    import libvirt
    import libvirt_qemu
    HAS_LIBVIRT_QEMU = True
except:
    HAS_LIBVIRT_QEMU = False

def main():

    argument_spec = dict(connection=dict(required=False, default="qemu:///system", type='str'),
                         name=dict(required=True, type='str'),
                         device=dict(required=True, type='str'),
                         ipv4=dict(default=True, choices=BOOLEANS, type='bool'),
                         ipv6=dict(default=False, choices=BOOLEANS, type='bool'),
                         timeout=dict(required=False, default=30, type='int'))

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    if not HAS_LIBVIRT_QEMU:
        module.fail_json(msg='libvirt_qemu is required for this module')

    try:
        connect = libvirt.open(module.params['connection'])
        domain = connect.lookupByName(module.params['name'])
        network_interface_string \
            = libvirt_qemu.qemuAgentCommand(domain,
                                            '{"execute":"guest-network-get-interfaces"}',
                                            module.params['timeout'],
                                            0)
        network_obj = json.loads(network_interface_string)
        kwargs = {}
        for device in network_obj['return']:
            if device['name'] == module.params['device']:
                for ip in device['ip-addresses']:
                    if ip['ip-address-type'] == 'ipv4' and module.params['ipv4']:
                        kwargs.update(ansible_virt_ipv4=ip['ip-address'])
                    if ip['ip-address-type'] == 'ipv6' and module.params['ipv6']:
                        kwargs.update(ansible_virt_ipv6=ip['ip-address'])
        module.exit_json(**kwargs)
    except Exception as e:
        module.fail_json(msg=str(e))


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()