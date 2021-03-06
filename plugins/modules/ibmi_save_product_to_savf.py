#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# Author, Chang Le <changle@cn.ibm.com>


from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
module: ibmi_save_product_to_savf
short_description: Save the the licensed program(product) to a save file
version_added: "2.8"
description:
    - the C(ibmi_save_product_to_savf) module saves the product to a save file.
options:
  product:
    description:
      - Specifies the seven-character identifier of the licensed program that is saved.
    type: str
    required: yes
  option:
    description:
      - Specifies the optional parts of the licensed program given in the Product prompt (LICPGM parameter) that are saved.
    type: str
    default: '*BASE'
  object_type:
    description:
      - Specifies the type of licensed program objects being saved.
    type: str
    default: '*ALL'
    choices: ['*ALL', '*PGM', '*LNG']
  language:
    description:
      - Specifies which national language version (NLV) is used for the save operation.
      - It's the IBM-supplied language feature codes, like German is 2924, English is 2924.
      - This parameter is ignored when object_type(*PGM) is specified.
    type: str
    default: '*PRIMARY'
  release:
    description:
      - Specifies which version, release, and modification level of the licensed program is saved.
    type: str
    default: '*ONLY'
  target_release:
    description:
      - Specifies the release level of the operating system on which you intend to restore and use the product.
    type: str
    default: '*CURRENT'
  savf_name:
    description:
      - Specify the name of the save file, if it is not existed, will create it.
    type: str
    required: yes
  savf_library:
    description:
      - Specify the name of the library where the save file is located, if it is not existed, will create it.
    type: str
    required: yes
  check_signature:
    description:
      - Specifies if the digital signatures of objects being saved with the licensed program are to be checked.
    type: str
    default: '*SIGNED'
    choices: ['*SIGNED', '*ALL', '*NONE']
  parameters:
    description:
      - The parameters that SAVLICPGM command will take. Other than options above, all other parameters need to be specified here.
      - The default values of parameters for SAVLICPGM will be taken if not specified.
      - Parameter CLEAR in SAVLICPGM command should not be specified here, 'CLEAR(*ALL)' already used.
    type: str
    default: ' '
  joblog:
    description:
      - If set to C(true), output the avaiable job log even the rc is 0(success).
    type: bool
    default: False
seealso:
- module: ibmi_uninstall_product, ibmi_install_product_from_savf
author:
- Chang Le (@changlexc)
'''

EXAMPLES = r'''
- name: Saving Program using Defaults.
  ibmi_save_product_to_savf:
    product: 5770WDS
    savf_name: MYFILE
    savf_library: MYLIB

- name: Saving Program 5733D10 option 11.
  ibmi_save_product_to_savf:
    product: 5733D10
    option: 11
    savf_name: MYFILE
    savf_library: MYLIB
'''

RETURN = r'''
stdout:
    description: The standard output.
    type: str
    sample: "+++ success SAVLICPGM LICPGM(5733D10) DEV(*SAVF) OPTION(*BASE) RSTOBJ(*ALL)"
    returned: When rc as 0(success)
stderr:
    description: The standard error.
    type: str
    sample: 'CPF9801: Object QNOTE in library L10010125P not found'
    returned: When rc as non-zero(failure)
rc:
    description: The task return code (0 means success, non-zero means failure).
    type: int
    sample: 255
    returned: always
stdout_lines:
    description: The standard output split in lines.
    type: list
    sample: [
        "+++ success SAVLICPGM LICPGM(5733D10) DEV(*SAVF) OPTION(*BASE) RSTOBJ(*ALL)"
    ]
    returned: When rc as 0(success)
stderr_lines:
    description: The standard error split in lines.
    type: list
    sample: [
        "CPF9801: Object QNOTE in library L10010125P not found"
    ]
    returned: When rc as non-zero(failure)
job_log:
    description: The IBM i job log of the task executed.
    type: list
    sample: [{
            "FROM_INSTRUCTION": "318F",
            "FROM_LIBRARY": "QSYS",
            "FROM_MODULE": "",
            "FROM_PROCEDURE": "",
            "FROM_PROGRAM": "QWTCHGJB",
            "FROM_USER": "CHANGLE",
            "MESSAGE_FILE": "QCPFMSG",
            "MESSAGE_ID": "CPD0912",
            "MESSAGE_LIBRARY": "QSYS",
            "MESSAGE_SECOND_LEVEL_TEXT": "Cause . . . . . :   This message is used by application programs as a general escape message.",
            "MESSAGE_SUBTYPE": "",
            "MESSAGE_TEXT": "Printer device PRT01 not found.",
            "MESSAGE_TIMESTAMP": "2020-05-20-21.41.40.845897",
            "MESSAGE_TYPE": "DIAGNOSTIC",
            "ORDINAL_POSITION": "5",
            "SEVERITY": "20",
            "TO_INSTRUCTION": "9369",
            "TO_LIBRARY": "QSYS",
            "TO_MODULE": "QSQSRVR",
            "TO_PROCEDURE": "QSQSRVR",
            "TO_PROGRAM": "QSQSRVR"
        }]
    returned: always
'''

import datetime
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.power_ibmi.plugins.module_utils.ibmi import ibmi_util

__ibmi_module_version__ = "0.0.1"


def main():
    module = AnsibleModule(
        argument_spec=dict(
            product=dict(type='str', required=True),
            option=dict(type='str', default='*BASE'),
            object_type=dict(type='str', default='*ALL', choices=['*ALL', '*PGM', '*LNG']),
            language=dict(type='str', default='*PRIMARY'),
            release=dict(type='str', default='*ONLY'),
            target_release=dict(type='str', default='*CURRENT'),
            savf_name=dict(type='str', required=True),
            savf_library=dict(type='str', required=True),
            check_signature=dict(type='str', default='*SIGNED', choices=['*SIGNED', '*ALL', '*NONE']),
            joblog=dict(type='bool', default=False),
            parameters=dict(type='str', default=' '),
        ),
        supports_check_mode=True,
    )

    ibmi_util.log_info("version: " + __ibmi_module_version__, module._name)

    product = module.params['product'].upper()
    option = module.params['option'].upper()
    object_type = module.params['object_type'].upper()
    language = module.params['language'].upper()
    release = module.params['release'].upper()
    target_release = module.params['target_release'].upper()
    savf_name = module.params['savf_name'].upper()
    savf_library = module.params['savf_library'].upper()
    parameters = module.params['parameters'].upper()
    check_signature = module.params['check_signature'].upper()
    joblog = module.params['joblog']

    if len(product) > 7:
        module.fail_json(rc=ibmi_util.IBMi_PARAM_NOT_VALID, msg="Value of product exceeds 7 characters")
    if len(option) > 5:
        module.fail_json(rc=ibmi_util.IBMi_PARAM_NOT_VALID, msg="Value of option exceeds 5 characters")
    if len(release) > 6:
        module.fail_json(rc=ibmi_util.IBMi_PARAM_NOT_VALID, msg="Value of release exceeds 6 characters")
    if len(target_release) > 8:
        module.fail_json(rc=ibmi_util.IBMi_PARAM_NOT_VALID, msg="Value of target_release exceeds 8 characters")
    if len(language) > 8:
        module.fail_json(rc=ibmi_util.IBMi_PARAM_NOT_VALID, msg="Value of language exceeds 8 characters")
    if len(savf_name) > 10:
        module.fail_json(rc=ibmi_util.IBMi_PARAM_NOT_VALID, msg="Value of savf_name exceeds 10 characters")
    if len(savf_library) > 10:
        module.fail_json(rc=ibmi_util.IBMi_PARAM_NOT_VALID, msg="Value of savf_library exceeds 10 characters")

    # Check if the library of savf is existed
    command = 'QSYS/CHKOBJ OBJ(QSYS/{pattern_savf_library}) OBJTYPE(*LIB)'.format(
        pattern_savf_library=savf_library.strip())
    args = ['system', command]
    rc, out, err = module.run_command(args, use_unsafe_shell=False)
    if rc != 0:  # library not exist, create it
        command = "QSYS/CRTLIB LIB({pattern_savf_library}) TEXT('Create by Ansible')".format(
            pattern_savf_library=savf_library.strip())
        args = ['system', command]
        rc, out, err = module.run_command(args, use_unsafe_shell=False)
        if rc != 0:  # fail to create library
            result = dict(
                stderr=err,
                rc=rc,
            )
            module.fail_json(msg="Fail to create library: {pattern_savf_library}".format(
                pattern_savf_library=savf_library.strip()), **result)

    # library exist, now check if the savf is existed
    command = 'QSYS/CHKOBJ OBJ({pattern_savf_library}/{pattern_savf_name}) OBJTYPE(*FILE)'.format(
        pattern_savf_name=savf_name.strip(),
        pattern_savf_library=savf_library.strip())
    # Check if the savf is existed
    args = ['system', command]
    rc, out, err = module.run_command(args, use_unsafe_shell=False)
    if rc != 0:  # savf not existed
        command = "QSYS/CRTSAVF FILE({pattern_savf_library}/{pattern_savf_name}) TEXT('Create by Ansible')".format(
            pattern_savf_name=savf_name.strip(),
            pattern_savf_library=savf_library.strip())
        args = ['system', command]
        rc, out, err = module.run_command(args, use_unsafe_shell=False)
        if rc != 0:  # fail to create savf
            result = dict(
                stderr=err,
                rc=rc,
            )
            module.fail_json(msg="Fail to create savf {pattern_savf_name} in library {pattern_savf_library}".format(
                pattern_savf_name=savf_name.strip(),
                pattern_savf_library=savf_library.strip()), **result)

    # run the SAVLICPGM command to save the product objects to the savf
    command = 'QSYS/SAVLICPGM LICPGM({pattern_product}) DEV(*SAVF) OPTION({pattern_option}) RLS({pattern_release}) \
        LNG({pattern_language})  OBJTYPE({pattern_object_type}) SAVF({pattern_savf_library}/{pattern_savf_name}) \
        TGTRLS({pattern_target_release}) CHKSIG({pattern_check_signature}) CLEAR(*ALL) {pattern_parameters}'.format(
        pattern_product=product,
        pattern_option=option,
        pattern_release=release,
        pattern_language=language,
        pattern_object_type=object_type,
        pattern_savf_library=savf_library.strip(),
        pattern_savf_name=savf_name.strip(),
        pattern_check_signature=check_signature,
        pattern_target_release=target_release,
        pattern_parameters=parameters)

    command = ' '.join(command.split())  # keep only one space between adjacent strings
    rc, out, err, job_log = ibmi_util.itoolkit_run_command_once(command)

    result = dict(
        command=command,
        stdout=out,
        stderr=err,
        rc=rc,
        job_log=job_log,
        changed=True,
    )

    if rc != 0:
        result = dict(
            command=command,
            stderr=err,
            job_log=job_log,
            rc=rc,
        )
        message = 'non-zero return code:{rc}'.format(rc=rc)
        module.fail_json(msg=message, **result)

    if not joblog:
        empty_list = []
        result.update({'job_log': empty_list})

    module.exit_json(**result)


if __name__ == '__main__':
    main()
