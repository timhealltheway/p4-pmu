#!/usr/bin/env python3
import runtime_CLI
from sswitch_runtime import SimpleSwitch
from sswitch_runtime.ttypes import *
import struct
import nnpy
import socket
<<<<<<< HEAD
import math
from jpt_algo_evaluation.jpt_algo import calculate_complex_voltage, jpt_algo, phase_angle_and_magnitude_from_complex_voltage, calculate_approximation_error, calculate_angle_error
from statistics import mean, stdev
from sorted_list import KeySortedList
from threading import Thread
from queue import Queue
import time

#TODO: replace hardcoded values like 16000 and 17000 with values derived from Frequency

=======
import os.path
import ipaddress
import math
from jpt_algo_evaluation.jpt_algo import calculate_complex_voltage, jpt_algo, phase_angle_and_magnitude_from_complex_voltage, calculate_approximation_error, calculate_angle_error
from statistics import mean, stdev
import threading
from collections import namedtuple
from sorted_list import KeySortedList
import argparse

#TODO: replace hardcoded values like 16000 and 17000 with values derived from Frequency

counter = 0
buffer = []
>>>>>>> 1a060186327a1232ee12745d2eb04f05309b2109
missing_packet_counter = 0

class SimpleSwitchAPI(runtime_CLI.RuntimeAPI):
    @staticmethod
    def get_thrift_services():
        return [("simple_switch", SimpleSwitch.Client)]

    def __init__(self, pre_type, standard_client, mc_client, sswitch_client):
        runtime_CLI.RuntimeAPI.__init__(self, pre_type,
                                        standard_client, mc_client)
        self.sswitch_client = sswitch_client


pmu_recovery_data_buffer = KeySortedList(keyfunc = lambda obj: obj["timestamp"])

<<<<<<< HEAD

def queue_digests(terminate_after, digest_queue, sub):
    #### Define the controller logic below ###
    while missing_packet_counter < terminate_after:
        message = sub.recv()
        digest_queue.put(message)

=======
def parse_console_args(parser):
    parser.add_argument('terminate_after', type=int, help='Number of packets to generate before terminating')
    return parser.parse_args()

def main():


    #cmd_args = parse_console_args(parser)

    parser = runtime_CLI.get_parser()
    parser.add_argument('--terminate_after', type=int, help='Number of packets to generate before terminating')

    args = parser.parse_args()

    args.pre = runtime_CLI.PreType.SimplePreLAG

    services = runtime_CLI.RuntimeAPI.get_thrift_services(args.pre)
    services.extend(SimpleSwitchAPI.get_thrift_services())

    standard_client, mc_client, sswitch_client = runtime_CLI.thrift_connect(
        args.thrift_ip, args.thrift_port, services
    )

    runtime_CLI.load_json_config(standard_client, args.json)
    runtime_api = SimpleSwitchAPI(
        args.pre, standard_client, mc_client, sswitch_client)

    ######### Call the function listen_for_digest below #########
    listen_for_digests(runtime_api, args.terminate_after)

def listen_for_digests(controller, terminate_after):
    sub = nnpy.Socket(nnpy.AF_SP, nnpy.SUB)
    socket = controller.client.bm_mgmt_get_info().notifications_socket
    #s1 = Pair0()
    #s1.listen(socket)
    print("socket is : " + str(socket))
    sub.connect(socket)
    sub.setsockopt(nnpy.SUB, nnpy.SUB_SUBSCRIBE, '')
    #### Define the controller logic below ###
    while missing_packet_counter < terminate_after:
        message = sub.recv()
        #print(message)
        on_message_recv(message, controller)
>>>>>>> 1a060186327a1232ee12745d2eb04f05309b2109

def parse_phasors(phasor_data, settings={"num_phasors": 1, "pmu_measurement_bytes": 8}):
    phasor = {
        "magnitude": struct.unpack('>f', phasor_data[0:int(settings["pmu_measurement_bytes"]/2)])[0],
        "angle": math.degrees(struct.unpack('>f', phasor_data[int(settings["pmu_measurement_bytes"]/2) : settings["pmu_measurement_bytes"]])[0]),
    }
    return [phasor]

def pmu_packet_parser(data, settings={"pmu_measurement_bytes": 8, "num_phasors": 1, "freq_bytes": 4, "dfreq_bytes": 4}):
    freq_start_byte = 16 + settings["num_phasors"] * settings["pmu_measurement_bytes"]
    dfreq_start_byte = freq_start_byte + settings["freq_bytes"]
    analog_start_byte = dfreq_start_byte + settings["dfreq_bytes"]
    digital_start_byte = analog_start_byte + 4

    # convert each field to correct data type
    pmu_packet = {
        "sync": data[0:2],
        "frame_size": int.from_bytes(data[2:4], byteorder="big"),
        "id_code": int.from_bytes(data[4:6], byteorder="big"),
        "soc": int.from_bytes(data[6:10], byteorder="big"),
        "frac_sec": int.from_bytes(data[10:14], byteorder="big"),
        "stat": int.from_bytes(data[14:16], byteorder="big"),
        "phasors": parse_phasors(data[16:16 + settings["pmu_measurement_bytes"]], {"num_phasors": settings["num_phasors"], "pmu_measurement_bytes": settings["pmu_measurement_bytes"]}),
        "freq": struct.unpack('>f', data[freq_start_byte:dfreq_start_byte]),
        "dfreq": struct.unpack('>f', data[dfreq_start_byte:analog_start_byte]),
        "analog": data[analog_start_byte:digital_start_byte],
        "digital": data[digital_start_byte:],
    }

    return pmu_packet

def generate_new_packets(interface, num_packets, initial_jpt_inputs, last_stored_soc, last_stored_fracsec, curr_soc, curr_fracsec):
    jpt_inputs = initial_jpt_inputs[0:]
    for i in range(num_packets):
        new_soc = last_stored_soc
        new_frac = last_stored_fracsec + 16666
        complex_voltage_estimate = jpt_algo(jpt_inputs[0], jpt_inputs[1], jpt_inputs[2])
        generated_mag, generated_pa = phase_angle_and_magnitude_from_complex_voltage(complex_voltage_estimate)
        if (new_frac) / 1000000 >= 1:
            new_frac = (new_frac) % 1000000
            new_soc = new_soc + 1

        #make sure not generating too many
        #print(str((curr_soc * 1000000 + curr_fracsec) - (new_soc * 1000000 + new_frac)))
        if (curr_soc * 1000000 + curr_fracsec) - (new_soc * 1000000 + new_frac) > 16000:
            generate_new_packet("s1-eth2", new_soc, new_frac, generated_mag, generated_pa)
<<<<<<< HEAD
            #time.sleep(.017)

=======

        """
        print("sending packet with: ")
        print("soc: " + str(new_soc))
        print("frac: " + str(new_frac))
        print("magnitude: " + str(generated_mag))
        print("phase_angle: " + str(generated_pa))
        """
>>>>>>> 1a060186327a1232ee12745d2eb04f05309b2109

        last_stored_soc = new_soc
        last_stored_fracsec = new_frac
        jpt_inputs = [complex_voltage_estimate] + jpt_inputs[0:2]



def generate_new_packet(interface, soc_in, frac_sec_in, voltage, angle, settings={"pmu_measurement_bytes": 8, "destination_ip": "10.0.2.2", "destination_port": 4712}):
    # 2 byte
    sync = b'\xAA\x01'

    # 2 byte, 44 for 32 bit values of PMU, 40 for 16 bit values of PMU
    # 36 - 8 + 8 * number of PMUs || 36 - 8 + 4 * number PMUs
    frame_size = b'\x00\x24'

    # 2 byte, 12 for this
    id_code = b'\x00\x0C'

    # 4 byte
    soc = int(soc_in).to_bytes(4, 'big')

    # 4 byte
    frac_sec = int(frac_sec_in).to_bytes(4, 'big')

    # 2 byte
    #0000000000001001 = controller generated pmu
    stat = b'\x00\x09'

    # 4 or 8 byte x number of phasors (see doc, 8 is for float)
    voltage_bytes = struct.pack('>f', voltage)
    angle_bytes = struct.pack('>f', math.radians(angle))
    phasors = voltage_bytes + angle_bytes

    # 2 byte, assumed 60
    freq = b'\x09\xC4'

    # 2 byte
    dfreq = b'\x00\x00'

    # 4 byte
    analog = b'\x00\x00\x00\x00'

    # 2 byte
    digital = b'\x00\x00'

    # 2 byte
    chk = b'\x00\x00'

    pmu_packet = sync + frame_size + id_code + soc + frac_sec + \
        stat + phasors + freq + dfreq + analog + digital + chk

    # Set the destination IP address and port number
    #TODO: make command line arguments
    destination_ip = "10.0.2.2"
    destination_port = 4712

    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, 25, str(interface + '\0').encode('utf-8'))
    # Send the PMU packet to the destination IP address and port number
    udp_socket.sendto(pmu_packet, (destination_ip, destination_port))

    # Close the UDP socket
    udp_socket.close()

"""
def run_nnpy_thread(q, sock):
    # Create the thread
    nnpy_thread = Thread(target=fetch_traffic, args=([q], [sock]))

    # Start the thread and set as daemon (kills the thread once main thread ends)
    nnpy_thread.daemon = True
    nnpy_thread.start()

def listen_for_events(q, controller):
    while True:
        event_data = q.get()
<<<<<<< HEAD
        on_digest_recv(event_data)
=======
        on_message_recv(event_data)
>>>>>>> 1a060186327a1232ee12745d2eb04f05309b2109
        q.task_done()

def fetch_traffic(q, sock):
    q = q[0]
    sock = sock[0]

    # Listen for incoming datagrams
    while(True):
        # Receive traffic from socket
        data = sock.recv(bufferSize)


        # Update the queue with the message
        q.put(data)
"""

def calc_missing_packet_count(curr_soc, curr_fracsec, last_stored_soc, last_stored_fracsec, freq_hz=60):
    soc_diff = curr_soc - last_stored_soc
    fracsec_diff = 0
    if curr_fracsec < last_stored_fracsec:
        soc_diff -= 1
        fracsec_diff = 1000000 - last_stored_fracsec + curr_fracsec
    else:
        fracsec_diff = curr_fracsec - last_stored_fracsec
    if soc_diff < 0:
        soc_diff = 0

    total_fracsec_passed = soc_diff * 1000000 + fracsec_diff
    #17000
    #print(total_fracsec_passed / 1000000 * 60)
    missing_packet_count = round(total_fracsec_passed / 1000000 * 60) - 1

    return missing_packet_count


<<<<<<< HEAD
def on_digest_recv(msg):
=======
mag_approx_errors = []
angle_approx_errors = []
def on_message_recv(msg, controller):
>>>>>>> 1a060186327a1232ee12745d2eb04f05309b2109
    _, _, ctx_id, list_id, buffer_id, num = struct.unpack("<iQiiQi", msg[:32])
    ### Insert the receiving logic below ###
    msg = msg[32:]
    #pmu_packet = pmu_packet_parser(msg)
    #offset = 36
    controller_phasor_info_packet_length = 16
    controller_phasor_info_packet_count = 3

    # the extra 8 here is for the most current timestamp
    offset = controller_phasor_info_packet_length * controller_phasor_info_packet_count + 8

    # For listening the next digest
    for m in range(num):
<<<<<<< HEAD
=======
        global counter
        global buffer
        global mag_approx_errors
        global angle_approx_errors
>>>>>>> 1a060186327a1232ee12745d2eb04f05309b2109
        global pmu_recovery_data_buffer
        global missing_packet_counter
        jpt_inputs = []
        msg_copy = msg[0:]
<<<<<<< HEAD
=======
        new_soc = 0
        new_frac_sec = 0
>>>>>>> 1a060186327a1232ee12745d2eb04f05309b2109
        last_stored_soc = 0
        last_stored_fracsec = 0
        # extracting phasor data from digest messages
        for j in range(controller_phasor_info_packet_count):
            frac = int.from_bytes(msg_copy[4:8], byteorder="big")
            soc = int.from_bytes(msg_copy[0:4], byteorder="big")
            phasor = parse_phasors(msg_copy[8:controller_phasor_info_packet_length])


            pmu_recovery_data_buffer.insert({"timestamp": soc + frac / 1000000, "magnitude": phasor[0]["magnitude"], "phase_angle": phasor[0]["angle"]})
            #top of receive stack =     most recent measurement
            if j == 0:
<<<<<<< HEAD
=======
                new_soc = soc
                new_frac = frac + 16666
>>>>>>> 1a060186327a1232ee12745d2eb04f05309b2109
                last_stored_soc = soc
                last_stored_fracsec = frac

            #jpt_inputs.append(calculate_complex_voltage(phasor[0]["magnitude"], phasor[0]["angle"]))
            #move to next jpt_phasor in triplet of
            msg_copy = msg_copy[controller_phasor_info_packet_length:]

        # extracting most recent time measurement
        curr_soc = int.from_bytes(msg_copy[0:4], byteorder="big")
        curr_fracsec = int.from_bytes(msg_copy[4:8], byteorder="big")

        #getting last 3 measurements from pmu_data buffer
        jpt_inputs = list(map(lambda pmu_data: calculate_complex_voltage(pmu_data["magnitude"], pmu_data["phase_angle"]), pmu_recovery_data_buffer.get_last_n(3)))

        #put measurements in correct order for current recovery functions
        jpt_inputs.reverse()

        missing_packets = calc_missing_packet_count(curr_soc, curr_fracsec, last_stored_soc, last_stored_fracsec)

        missing_packet_counter += missing_packets
        print("NUM MISSING TOTAL: " + str(missing_packet_counter))


<<<<<<< HEAD

        if len(jpt_inputs) > 2:
            generate_new_packets("s1-eth2", missing_packets, jpt_inputs, last_stored_soc, last_stored_fracsec, curr_soc, curr_fracsec)

        #move to next digest packet
        msg = msg[offset:]

def setup():
    parser = runtime_CLI.get_parser()
    parser.add_argument('--terminate_after', type=int, help='Number of packets to generate before terminating')

    args = parser.parse_args()

    args.pre = runtime_CLI.PreType.SimplePreLAG

    services = runtime_CLI.RuntimeAPI.get_thrift_services(args.pre)
    services.extend(SimpleSwitchAPI.get_thrift_services())

    standard_client, mc_client, sswitch_client = runtime_CLI.thrift_connect(
        args.thrift_ip, args.thrift_port, services
    )

    runtime_CLI.load_json_config(standard_client, args.json)
    runtime_api = SimpleSwitchAPI(
        args.pre, standard_client, mc_client, sswitch_client)

    sub = nnpy.Socket(nnpy.AF_SP, nnpy.SUB)
    socket = runtime_api.client.bm_mgmt_get_info().notifications_socket
    print("socket is : " + str(socket))
    sub.connect(socket)
    sub.setsockopt(nnpy.SUB, nnpy.SUB_SUBSCRIBE, '')

    return runtime_api, args.terminate_after, sub

def listen_for_new_digests(q):
    while True:
        event_data = q.get()
        on_digest_recv(event_data)
        q.task_done()

if __name__ == "__main__":

    runtime_api, terminate_after, sub = setup()


    digest_message_queue = Queue()
    # Create the thread to listen for digest messages
    digest_message_thread = Thread(target=queue_digests, args=(terminate_after, digest_message_queue, sub))
    digest_message_thread.daemon = True
    digest_message_thread.start()

    #does some stuff when a digest is received
    listen_for_new_digests(digest_message_queue)
=======
        if len(jpt_inputs) > 2:
            generate_new_packets("s1-eth2", missing_packets, jpt_inputs, last_stored_soc, last_stored_fracsec, curr_soc, curr_fracsec)
        #move to next digest packet
        msg = msg[offset:]

main()
>>>>>>> 1a060186327a1232ee12745d2eb04f05309b2109
