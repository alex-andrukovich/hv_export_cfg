#!/usr/bin/env python3
import subprocess
import re
import pandas as pd
import os
import numpy as np
from openpyxl import load_workbook
import logging
import traceback
import time
import optparse

# Create a custom logger
logger = logging.getLogger("logger")
# Set the level of this logger. INFO means that it will handle all messages with a level of INFO and above
logger.setLevel(logging.DEBUG)
# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('hv_export_cfg.log')
c_handler.setLevel(logging.DEBUG)
f_handler.setLevel(logging.DEBUG)
# Create formatters and add it to handlers
c_format = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-s", "--storage", dest="storage", help="Enter a storage IP address xxx.xxx.xxx.xxx, UDP port 31001 will be used automatically")
    parser.add_option("-u", "--user", dest="user", help="Enter the username for the storage system")
    parser.add_option("-p", "--password", dest="password", help="Enter the password for the storage system")
    (options, arguments) = parser.parse_args()
    if not options.storage:
        parser.exit("[-] Please specify a storage system IP address, use --help or -h for more info.")
    elif not options.user:
        parser.exit("[-] Please specify the username to connect the storage system, use --help or -h for more info.")
    elif not options.password:
        parser.exit("[-] Please specify the password to connect the storage system, use --help or -h for more info.")
    return options

def get_home_path():
    logger.info("Function execution started")
    start_time = time.time()
    homedrive = os.environ.get('HOMEDRIVE')
    homepath = os.environ.get('HOMEPATH')
    full_homepath = homedrive + homepath
    # logger.info("using " + full_homepath + "as the home path")
    logger.info("queried for home directory, returned: " + full_homepath + " horcmXXX.conf and Excel files will be created here")
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return full_homepath

def init_excel_file(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    get_system = subprocess.check_output(["raidcom", "get", "system", "-fx", "-I" + horcm_instance]).decode().splitlines()
    get_resource = subprocess.check_output(["raidcom", "get", "resource", "-fx", "-key", "opt", "-I" + horcm_instance]).decode().splitlines()
    get_system_opt = subprocess.check_output(["raidcom", "get", "system_opt", "-fx", "-I" + horcm_instance]).decode().splitlines()
    get_system_opt_som = subprocess.check_output(["raidcom", "get", "system_opt", "-key", "mode", "-lpr", "system", "-I" + horcm_instance]).decode().splitlines()
    serial = get_system[0].split(":")[1].strip()
    init = get_system + ['\n'] + get_resource + ['\n'] + get_system_opt + ['\n'] + get_system_opt_som
    init_df = pd.DataFrame(init)
    excel_file_path = get_home_path() + "\\" + serial + "_cfg_export.xlsx"
    init_df.to_excel(excel_file_path, header=False, index=False, sheet_name='Summary_' + serial)
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return excel_file_path

def create_vsm_dict(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    vsm_dict = {}
    get_resource = subprocess.check_output(["raidcom", "get", "resource", "-fx", "-key", "opt", "-I" + horcm_instance]).decode().splitlines()
    for vsm in get_resource[1:]:
        vsm_dict[vsm.split()[1].strip()] = vsm.split()[0].strip()
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return vsm_dict
def create_horcm_file(horcm_instance, path, storage_ip):
        logger.info("Function execution started")
        start_time = time.time()
        horcm_file_full_path = path + "\\" + "horcm" + horcm_instance + ".conf"
        with open(horcm_file_full_path, 'w') as horcm_file:
                horcm_file.write("HORCM_MON" + '\n')
                horcm_file.write("#ip_address" + '\t' + "service" + '\t' + "poll(10ms)" + '\t' + "timeout(10ms)" + '\n')
                horcm_file.write("#localhost" + '\t' + "44666" + '\t' + "1000" + '\t\t' + "3000" + '\n\n\n')
                horcm_file.write("HORCM_CMD" + '\n')
                horcm_file.write("#dev_name" + '\t' + "dev_name" + '\t' + "dev_name)" + '\t' + "dev_name" + '\n')
                horcm_file.write("\\\\.\\IPCMD-" + storage_ip + "-31001" + '\n')
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"The function took {execution_time} seconds to execute.")

def shutdown_horcm_instance(horcm_instance, path):
    logger.info("Function execution started")
    start_time = time.time()
    horcm_file_full_path = path + "\\" + "horcm" + horcm_instance + ".conf"
    os.environ['HORCM_CONF'] = horcm_file_full_path
    os.environ['HORCMINST'] = horcm_instance
    os.environ['HORCM_EVERYCLI'] = "1"
    subprocess.run(["horcmshutdown"])
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")

def start_horcm_instance(horcm_instance, path):
        logger.info("Function execution started")
        start_time = time.time()
        try:
            shutdown_horcm_instance(horcm_instance, path)
        except:
            logger.info("Could not shutdown HORCM instance, might be down already")
        horcm_file_full_path = path + "\\" + "horcm" + horcm_instance + ".conf"
        os.environ['HORCM_CONF'] = horcm_file_full_path
        os.environ['HORCMINST'] = horcm_instance
        os.environ['HORCM_EVERYCLI'] = "1"
        subprocess.run(["horcmstart"])
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"The function took {execution_time} seconds to execute.")



def raidcom_login(horcm_instance, username, password):
        logger.info("Function execution started")
        start_time = time.time()
        subprocess.run(["raidcom", "-login", username, password, "-I"+horcm_instance])
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"The function took {execution_time} seconds to execute.")

def add_sheet_to_excel(data, excel_file_path ,sheet_name, transpose):
    logger.info("Function execution started")
    start_time = time.time()
    data_df = pd.DataFrame(data)
    if transpose:
        data_df = data_df.transpose()
    data_df.reset_index(inplace=True, drop=True)
    if type(data) is list:
        try:
            numpy_data = np.array(data)
            data_df = pd.DataFrame(numpy_data[1:], columns=numpy_data[0])
        except Exception as e:
            logger.warning("numpy_data error", exc_info=True)
    with pd.ExcelWriter(excel_file_path, mode='a') as writer:
            data_df.to_excel(writer, sheet_name=sheet_name,  freeze_panes=(1, 0), index=False)
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")



def get_ldev_list_mapped(horcm_instance):
        logger.info("Function execution started")
        start_time = time.time()
        array_of_ldevs = []
        ldevs = subprocess.check_output(
            ["raidcom", "get", "ldev", "-ldev_list", "mapped", "-fx", "-key", "front_end", "-I" + horcm_instance])
        ldevs = ldevs.splitlines()
        for ldev in ldevs:
            ldev = ldev.decode()
            if not "VOL_TYPE" in ldev:
                ldev = ldev.split()
                array_of_ldevs.append(ldev)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"The function took {execution_time} seconds to execute.")
        return array_of_ldevs
def get_ldev_list_defailed_by_type(horcm_instance, type):
        logger.info("Function execution started")
        start_time = time.time()
        vsm_dict = create_vsm_dict(horcm_instance)
        ldev_dict = {}
        ldev_dict_of_dict = {}
        ldevs_by_type = subprocess.check_output(
            ["raidcom", "get", "ldev", "-fx", "-ldev_list", type, "-I" + horcm_instance])
        ldevs_by_type = ldevs_by_type.decode()
        array_ldevs_by_type = ldevs_by_type.split("\r\n\r\n")
        array_ldevs_by_type.pop()
        for ldev in array_ldevs_by_type:
            ldev_details_list = ldev.splitlines()
            main_key = ldev_details_list[1].split(":")[1]
            main_key = main_key.strip()
            for line in ldev_details_list:
                l = line.split(":")
                value = ''.join(l[1:])
                key = l[0]
                if not re.search("VIR_LDEV", value.strip()):
                    ldev_dict[key.strip()] = value.strip()
                else:
                    ldev_dict[key.strip()] = value.split()[0].strip()
                    ldev_dict['VIR_LDEV'] = value.split()[2].strip()
                if re.search("RSGID", key.strip()):
                    ldev_dict[key.strip()] = value.strip()
                    ldev_dict['RSGID_NAME'] = vsm_dict[value.strip()]
            ldev_dict_of_dict[main_key] = ldev_dict
            ldev_dict = {}
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"The function took {execution_time} seconds to execute.")
        return ldev_dict_of_dict


def get_port(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    array_of_ports = []
    array_of_keys = []
    dict_of_port_dict = {}
    port_dict = {}
    port_state_dict = {}
    ports = subprocess.check_output(["raidcom", "get", "port", "-fx", "-key", "detail", "-I" + horcm_instance])
    for i, port in enumerate(ports.splitlines()):
        if i == 0:
            port = port.decode()
            array_of_keys = port.split()
        else:
            port = port.decode()
            array_of_ports = port.split()
            for j, key in enumerate(array_of_keys):
                port_dict[array_of_keys[j]] = array_of_ports[j]
            if array_of_ports[0] in dict_of_port_dict:
                # dict1 = port_dict
                # dict2 = dict_of_port_dict[array_of_ports[0]]
                # keys_in_both_with_diff_values = {k: (dict1[k], dict2[k]) for k in
                #                                  dict1.keys() & dict2.keys() if dict1[k] != dict2[k]}
                dict_of_port_dict[array_of_ports[0]]['ATTR'] = dict_of_port_dict[array_of_ports[0]]['ATTR'] + ";" + \
                                                               port_dict['ATTR']

            else:
                dict_of_port_dict[array_of_ports[0]] = port_dict
                port_dict = {}
    for key in dict_of_port_dict:
        if dict_of_port_dict[key]['TYPE'] == "FIBRE":
            text_wwn = ':'.join(
                dict_of_port_dict[key]['WWN'][i:i + 2] for i in range(0, len(dict_of_port_dict[key]['WWN']), 2))
            dict_of_port_dict[key]['WWN_DELIM'] = text_wwn
            port_host_grps = subprocess.check_output(
                ["raidcom", "get", "host_grp", "-port", key, "-fx", "-I" + horcm_instance])
            host_grps_of_a_port_str = ""
            for i, port_host_grp in enumerate(port_host_grps.splitlines()):
                if i > 0:
                    port_host_grp = port_host_grp.decode()
                    port_host_grp = port_host_grp.split()
                    host_grps_of_a_port_str = host_grps_of_a_port_str + port_host_grp[2] + ";"
            dict_of_port_dict[key]['HOST_GROUP_LIST'] = host_grps_of_a_port_str
            port_state_list = subprocess.check_output(
                ["raidcom", "get", "port", "-fx", "-port", key, "-key", "opt", "-I" + horcm_instance])
            for i, port_state in enumerate(port_state_list.splitlines()):
                if i == 0:
                    port_state = port_state.decode()
                    array_of_port_state_keys = port_state.split()
                else:
                    port_state = port_state.decode()
                    array_of_port_state = port_state.split()
                    for j, state in enumerate(array_of_port_state_keys):
                        dict_of_port_dict[key][array_of_port_state_keys[j]] = array_of_port_state[j]
        if dict_of_port_dict[key]['TYPE'] == "ISCSI":
            port_state = subprocess.check_output(
                ["raidcom", "get", "port", "-fx", "-port", key, "-key", "opt", "-I" + horcm_instance])
            for i, port_state in enumerate(port_state.splitlines()):
                port_state = port_state.decode()
                array_of_port_state_keys = port_state.split(":")
                array_of_port_state_values = ''.join(array_of_port_state_keys[1:])
                dict_of_port_dict[key][array_of_port_state_keys[0]] = array_of_port_state_values
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return dict_of_port_dict


def create_host_grp_array_of_arrays(horcm_instance):
        logger.info("Function execution started")
        start_time = time.time()
        vsm_dict=create_vsm_dict(horcm_instance)
        array_of_ports=[]
        array_of_host_grps=[['PORT', 'GID','PORT-GID', 'GROUP_NAME', 'Serial', 'HMD', 'HMO_BITs', 'VSM_NAME', 'VSM_ID']]
        ports=subprocess.check_output(["raidcom", "get", "port", "-fx", "-I" + horcm_instance])
        for port in ports.splitlines():
                port=port.decode()
                if "FIBRE" in port:
                        array_of_ports.append(port.split()[0])
        array_of_unique_ports = set(array_of_ports)
        for port in array_of_unique_ports:
            for key in vsm_dict:
                get_host_grps_of_a_port = subprocess.check_output(["raidcom", "get", "host_grp", "-port", port, "-fx", "-resource", key, "-I" + horcm_instance])
                get_host_grps_of_a_port = get_host_grps_of_a_port.splitlines()
                for host_grp in get_host_grps_of_a_port:
                        host_grp = host_grp.decode()
                        if not "GROUP_NAME" in host_grp:
                                host_grp=host_grp.split()
                                hmo = " ".join(host_grp[5:])
                                if host_grp[4] == "LINUX/IRIX":
                                        host_grp[4] = "LINUX"
                                host_grp_concat_hmo =  [host_grp[0] , host_grp[1] ,host_grp[0]+ "-" + host_grp[1] ,host_grp[2] ,host_grp[3] ,host_grp[4], hmo, vsm_dict[key], key]
                                array_of_host_grps.append(host_grp_concat_hmo)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"The function took {execution_time} seconds to execute.")
        return array_of_host_grps


def get_hba_wwns_of_a_host_grp_by_name(port, host_grp_name, horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    array_of_wwns = []
    wwns = subprocess.check_output(
        ["raidcom", "get", "hba_wwn", "-port", port, host_grp_name, "-fx", "-I" + horcm_instance])
    wwns = wwns.splitlines()
    for wwn in wwns:
        wwn = wwn.decode()
        wwn = wwn.split()
        array_of_wwns.append(wwn)
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return array_of_wwns

def get_hba_wwns_of_all_host_groups(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    wwn = []
    columns = []
    array_of_wwns = []
    array_of_host_grps = []
    host_grp_array_of_arrays = create_host_grp_array_of_arrays(horcm_instance)
    for host_grp in host_grp_array_of_arrays:
        if not re.search("GROUP_NAME", host_grp[3]):
            wwns = get_hba_wwns_of_a_host_grp_by_name(host_grp[0], host_grp[3], horcm_instance)
            for w in wwns:
                if not "GROUP_NAME" in w:
                    array_of_wwns.append(w)
                    w.append(host_grp[7])
                    w.append(host_grp[8])
                else:
                    columns = w
                    w.append("VSM_NAME")
                    w.append("VSM_ID")
    array_of_wwns.insert(0,columns)
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return array_of_wwns

def get_luns_of_a_host_grp_by_name(port, host_grp_name, horcm_instance):
        logger.info("Function execution started")
        start_time = time.time()
        dict_of_luns = {}
        luns = subprocess.check_output(
            ["raidcom", "get", "lun", "-port", port, host_grp_name, "-fx", "-I" + horcm_instance])
        luns = luns.splitlines()
        for lun in luns:
            lun = lun.decode()
            if not "HMO_BITs" in lun:
                lun = lun.split()
                # dict_of_luns["0x" + lun[5]] = lun[3]
                dict_of_luns[lun[5]] = lun[3]
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"The function took {execution_time} seconds to execute.")
        return dict_of_luns

def get_luns_of_all_host_groups(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    luns = []
    columns = []
    array_of_luns = []
    array_of_host_grps = []
    host_grp_array_of_arrays = create_host_grp_array_of_arrays(horcm_instance)
    for host_grp in host_grp_array_of_arrays:
        if not re.search("GROUP_NAME", host_grp[3]):
            luns = get_luns_of_a_host_grp_by_name(host_grp[0], host_grp[3], horcm_instance)
            for l in luns:
                array_of_luns.append([host_grp[0], host_grp[1], host_grp[2], host_grp[3], host_grp[4], host_grp[5], host_grp[6], host_grp[7], host_grp[8], l, luns[l]])
        else:
            columns = host_grp
            columns.append("LDEV_ID")
            columns.append("LUN_ID")
    array_of_luns.insert(0, columns)
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return array_of_luns


def output_horcm_text_data(horcm_instance):
        logger.info("Function execution started")
        start_time = time.time()
        horcm_ldev = []
        get_ldev_list_mapped_output = []
        get_ldev_list_mapped_output = get_ldev_list_mapped(horcm_instance)
        for i in get_ldev_list_mapped_output:
                if re.search(r'HORC', i[7]) or re.search(r'GAD', i[7]):
                        chars_ldev = [char for char in i[1]]
                        if len(chars_ldev) == 1:
                                chars_ldev.insert(0, "0")
                                chars_ldev.insert(0, "0")
                                chars_ldev.insert(0, "0")
                        if len(chars_ldev) == 2:
                                chars_ldev.insert(0, "0")
                                chars_ldev.insert(0, "0")
                        if len(chars_ldev) == 3:
                                chars_ldev.insert(0, "0")
                        chars_ldev.insert(2, ":")
                        text_ldev = ''.join(chars_ldev)
                        horcm_ldev.append("discover_remote" + '\t' + "discover_remote_" + i[1] + "_0" + '\t' + i[0] + '\t' + text_ldev + '\t' + "0")
                        horcm_ldev.append("discover_remote" + '\t' + "discover_remote_" + i[1] + "_h1" + '\t' + i[0] + '\t' + text_ldev + '\t' + "h1")
                        horcm_ldev.append("discover_remote" + '\t' + "discover_remote_" + i[1] + "_h2" + '\t' + i[0] + '\t' + text_ldev + '\t' + "h2")
                        horcm_ldev.append("discover_remote" + '\t' + "discover_remote_" + i[1] + "_h3" + '\t' + i[0] + '\t' + text_ldev + '\t' + "h3")
                if re.search(r'QS', i[7]) or re.search(r'MRCF', i[7]):
                        chars_ldev = [char for char in i[1]]
                        if len(chars_ldev) == 1:
                                chars_ldev.insert(0, "0")
                                chars_ldev.insert(0, "0")
                                chars_ldev.insert(0, "0")
                        if len(chars_ldev) == 2:
                                chars_ldev.insert(0, "0")
                                chars_ldev.insert(0, "0")
                        if len(chars_ldev) == 3:
                                chars_ldev.insert(0, "0")
                        chars_ldev.insert(2, ":")
                        text_ldev = ''.join(chars_ldev)
                        horcm_ldev.append("discover_local" + '\t' + "discover_local_" + i[1] + "_0" + '\t' + i[0] + '\t' + text_ldev + '\t' + "0")
                        horcm_ldev.append("discover_local" + '\t' + "discover_local_" + i[1] + "_1" + '\t' + i[0] + '\t' + text_ldev + '\t' + "1")
                        horcm_ldev.append("discover_local" + '\t' + "discover_local_" + i[1] + "_2" + '\t' + i[0] + '\t' + text_ldev + '\t' + "2")
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"The function took {execution_time} seconds to execute.")
        return horcm_ldev

def add_horcm_ldev_data_to_horcm(horcm_instance, path):
    logger.info("Function execution started")
    start_time = time.time()
    local = False
    remote = False
    f = []
    horcm_ldev_data = output_horcm_text_data(horcm_instance)
    shutdown_horcm_instance(horcm_instance, get_home_path())
    horcm_file_full_path = path + "\\" + "horcm" + horcm_instance + ".conf"
    with open(horcm_file_full_path, 'a') as horcm_file:
        horcm_file.write('\n' + "HORCM_LDEV" + '\n')
        horcm_file.write("# dev_group" + '\t' + "dev_name" + '\t' + "Serial#" + '\t' + "CU:LDEV(LDEV#)" + '\t' + "MU#" + '\n')
        for mu in horcm_ldev_data:
            horcm_file.write(mu + '\n')
            if re.search(r'local', mu):
                local = True
            if re.search(r'remote', mu):
                remote = True
        horcm_file.write('\n' + "HORCM_INSTP" + '\n')
        if remote:
            horcm_file.write("discover_remote" + '\t' + "localhost" + '\t' + "44667" + '\n')
        if local:
            horcm_file.write("discover_local" + '\t' + "localhost" + '\t' + "44667" + '\n')
    start_horcm_instance(horcm_instance, get_home_path())
    with open(horcm_file_full_path, 'r') as horcm_file:
        horcm_data = horcm_file.read()
    horcm_data = horcm_data.splitlines()
    for l in horcm_data:
        l = l.split()
        f.append(l)
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return f
def discover_replication_remote(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    array_of_mus = []
    try:
        pairdisplay_fxe = subprocess.check_output(["pairdisplay", "-g", "discover_remote", "-fxe", "-CLI", "-l", "-IH" + horcm_instance])
        pairdisplay_fxc = subprocess.check_output(["pairdisplay", "-g", "discover_remote", "-fxc", "-CLI", "-l", "-IH" + horcm_instance])
        pairdisplay_fxe = pairdisplay_fxe.decode().splitlines()
        for i , line in enumerate(pairdisplay_fxe):
            mu = line.split()
            array_of_mus.append(mu)
        pairdisplay_fxc = pairdisplay_fxc.decode().splitlines()
        for i , line in enumerate(pairdisplay_fxc):
            mu = line.split()
            for obj in mu:
                array_of_mus[i].append(obj)
    except:
        logger.error("pairdisplay did not work")
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return array_of_mus

def discover_replication_local(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    array_of_mus = []
    try:
        pairdisplay_local_fcxe = subprocess.check_output(
            ["pairdisplay", "-g", "discover_local", "-fxce", "-CLI", "-l", "-ISI" + horcm_instance])
        pairdisplay_local_fcxe = pairdisplay_local_fcxe.decode().splitlines()
        for i , line in enumerate(pairdisplay_local_fcxe):
            mu = line.split()
            array_of_mus.append(mu)
        array_of_mus[0].append("#")
    except:
        logger.error("pairdisplay did not work")
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return array_of_mus

def get_rcu(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    array_of_rcu = []
    get_rcus = subprocess.check_output(
        ["raidcom", "get", "rcu", "-fx", "-I" + horcm_instance])
    get_rcus = get_rcus.decode().splitlines()
    for line in get_rcus[1:]:
        line = line.split()
        get_rcu = subprocess.check_output(["raidcom", "get", "rcu", "-fx", "-cu_free", line[0], line[1], line[2], "-I" + horcm_instance])
        rcu = get_rcu.decode().splitlines()
        for i in rcu:
            i = i.splitlines()
            for j in i:
                j = j.split()
                array_of_rcu.append(j[0:12])
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return array_of_rcu

def get_license(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    array_of_lic = []
    lic = subprocess.check_output(
        ["raidcom", "get", "license", "-I" + horcm_instance])
    lic = lic.decode().splitlines()
    for i , line in enumerate(lic):
        license = line.split()
        license = [license[0], license[1], license[2], license[3], license[4], license[5], license[6], license[7], ' '.join(license[8:])]
        array_of_lic.append(license)
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return array_of_lic

def get_pool(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    array_of_pools = []
    pools = subprocess.check_output(
        ["raidcom", "get", "pool", "-key", "opt", "-fx", "-I" + horcm_instance])
    pools_used = subprocess.check_output(
        ["raidcom", "get", "pool",  "-fx", "-I" + horcm_instance])
    pools = pools.decode().splitlines()
    pools_used = pools_used.decode().splitlines()
    for i , line in enumerate(pools):
        pool = line.split()
        array_of_pools.append(pool)
    for i , line in enumerate(pools_used):
        pool_used = line.split()
        for p in pool_used:
            array_of_pools[i].append(p)
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return array_of_pools

def get_quorum(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    dict_of_quorum = {}
    dict_of_dict_of_quorum = {}
    quorum = subprocess.check_output(
        ["raidcom", "get", "quorum", "-fx", "-I" + horcm_instance])
    quorum = quorum.decode().split('\r\n\r\n')
    for line in quorum:
        qline = line.splitlines()
        dict_of_quorum = {}
        for attrib in qline:
            attrib = attrib.split(":")
            key = attrib[0].strip()
            value = attrib[1].strip()
            if key == "QRDID":
                main_key = value
            dict_of_quorum[key] = value
        dict_of_dict_of_quorum[main_key] = dict_of_quorum
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return dict_of_dict_of_quorum

def get_jnl(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    array_of_jnl = []
    get_jnls = subprocess.check_output(["raidcom", "get", "journal", "-fx", "-I" + horcm_instance])
    get_jnls = get_jnls.decode().splitlines()
    for jnl in get_jnls:
        jnl = jnl.split()
        array_of_jnl.append(jnl)
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return array_of_jnl

def get_jnl_mus(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    array_of_jnl = []
    get_jnls = subprocess.check_output(["raidcom", "get", "journal", "-fx", "-key", "opt", "-I" + horcm_instance])
    get_jnls = get_jnls.decode().splitlines()
    for jnl in get_jnls:
        jnl = jnl.split()
        array_of_jnl.append(jnl)
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return array_of_jnl

def get_snapshot(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    array_of_snap = []
    get_snaps = subprocess.check_output(["raidcom", "get", "snapshot", "-fx", "-I" + horcm_instance])
    get_snaps = get_snaps.decode().splitlines()
    for line in get_snaps[1:]:
        line = line.split()
        get_snap_grp = subprocess.check_output(["raidcom", "get", "snapshot", "-fx", "-format_time", "-snapshotgroup", line[0], "-I" + horcm_instance])
        snap = get_snap_grp.decode().splitlines()
        columns = snap[0].split()
        for i in snap[1:]:
            i = i.splitlines()
            for j in i:
                j = j.split()
                array_of_snap.append(j)
    array_of_snap[:0] = [columns]
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return array_of_snap

def is_valid_ip(ip):
    logger.info("Function execution started")
    start_time = time.time()
    pattern = re.compile(r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return bool(pattern.match(ip))

user_input = get_arguments()

horcm_instance = "666"
storage_ip = user_input.storage
if not is_valid_ip(storage_ip):
    logger.error("Invalid IP address was specified: {storage_ip}")
    exit()
username = user_input.user
password = user_input.password
create_horcm_file(horcm_instance, get_home_path(), storage_ip)
start_horcm_instance(horcm_instance, get_home_path())
raidcom_login(horcm_instance, username, password)
file = init_excel_file(horcm_instance)
##
##

add_sheet_to_excel(get_snapshot(horcm_instance), file, "Snapshots", False)
add_sheet_to_excel(get_jnl(horcm_instance), file, "Journals", False)
add_sheet_to_excel(get_jnl_mus(horcm_instance), file, "Journal_MUs", False)
add_sheet_to_excel(get_rcu(horcm_instance), file, "RCUs", False)
add_sheet_to_excel(get_license(horcm_instance), file, "Licenses", False)
add_sheet_to_excel(get_pool(horcm_instance), file, "Pools", False)
add_sheet_to_excel(get_quorum(horcm_instance), file, "Quorum", True)
add_sheet_to_excel(get_port(horcm_instance), file, "Ports", True)
add_sheet_to_excel(add_horcm_ldev_data_to_horcm(horcm_instance, get_home_path()), file, "Horcm", False)
add_sheet_to_excel(discover_replication_remote(horcm_instance), file, "Replication_remote", False)
add_sheet_to_excel(discover_replication_local(horcm_instance), file, "Replication_local", False)
add_sheet_to_excel(get_luns_of_all_host_groups(horcm_instance), file, "Luns", False)
add_sheet_to_excel(get_hba_wwns_of_all_host_groups(horcm_instance), file, "Hba_wwns", False)
add_sheet_to_excel(get_ldev_list_defailed_by_type(horcm_instance, "mapped"), file, "Ldevs_mapped", True)
add_sheet_to_excel(get_ldev_list_defailed_by_type(horcm_instance, "defined"), file, "Ldevs_defined", True)
add_sheet_to_excel(get_ldev_list_defailed_by_type(horcm_instance, "unmapped"), file, "Ldevs_unmapped", True)
## undefined on simulators = raidcom: [EX_ENOOBJ] No such Object in the RAID ; exit code 1
##add_sheet_to_excel(get_ldev_list_defailed_by_type(horcm_instance, "undefined"), file, "Ldevs_undefined", True)
add_sheet_to_excel(create_host_grp_array_of_arrays(horcm_instance), file, "Host_groups", False)




