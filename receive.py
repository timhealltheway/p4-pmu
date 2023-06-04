import socket
import struct
import math
import sys
from sorted_list import KeySortedList
import signal
import argparse
import time

UDP_IP_ADDRESS = "0.0.0.0"  # listen on all available interfaces
UDP_PORT_NO = 4712  # PMU data port number
sorted_pmus = KeySortedList(keyfunc = lambda pmu: pmu["soc"] + pmu["frac_sec"] / 1000000)

# create a UDP socket object
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# bind the socket to the specified IP address and port number
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

def parse_phasors(phasor_data, settings={"num_phasors": 1, "pmu_measurement_bytes": 8}):
    phasor = {
        "magnitude": struct.unpack('>f', phasor_data[0:int(settings["pmu_measurement_bytes"]/2)])[0],
        "angle": math.degrees(struct.unpack('>f', phasor_data[int(settings["pmu_measurement_bytes"]/2) : settings["pmu_measurement_bytes"]])[0]),
    }
    return [phasor]

def pmu_packet_parser(data, settings={"pmu_measurement_bytes": 8, "num_phasors": 1, "freq_bytes": 2, "dfreq_bytes": 2}):
    freq_start_byte = 16 + settings["num_phasors"] * settings["pmu_measurement_bytes"]
    dfreq_start_byte = freq_start_byte + settings["freq_bytes"]
    analog_start_byte = dfreq_start_byte + settings["dfreq_bytes"]
    digital_start_byte = analog_start_byte + 4
    chk_start_byte = digital_start_byte + 2

    # convert each field to correct data type
    pmu_packet = {
        "sync": int.from_bytes(data[0:2], byteorder="big"),
        "frame_size": int.from_bytes(data[2:4], byteorder="big"),
        "id_code": int.from_bytes(data[4:6], byteorder="big"),
        "soc": int.from_bytes(data[6:10], byteorder="big"),
        "frac_sec": int.from_bytes(data[10:14], byteorder="big"),
        "stat": int.from_bytes(data[14:16], byteorder="big"),
        "phasors": parse_phasors(data[16:16 + settings["pmu_measurement_bytes"]], {"num_phasors": settings["num_phasors"], "pmu_measurement_bytes": settings["pmu_measurement_bytes"]}),
        "freq": data[freq_start_byte:dfreq_start_byte],
        "dfreq": data[dfreq_start_byte:analog_start_byte],
        "analog": data[analog_start_byte:digital_start_byte],
        "digital": data[digital_start_byte:chk_start_byte],
        "chk": data[chk_start_byte:]
    }

    return pmu_packet

#stuff you want to print out if you have to cntrl-c out of program due to error
def cntrl_c_handler(signum, frame):
    sorted_pmus.print_pmu()
    exit(1)


def parse_console_args(parser):
    parser.add_argument('terminate_after', type=int, help='Number of packets to receive before terminating')
    return parser.parse_args()


# wait for incoming PMU packets
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        prog='pmu-packet-receiver',
                        description='Receives pmu packets',
                        epilog='Text at the bottom of help')
    args = parse_console_args(parser)
    signal.signal(signal.SIGINT, cntrl_c_handler)
    received_counter = 0
    buffer = []
    predicted_magnitude = 0
    predicted_pa = 0
    end_time = 0


    while received_counter <1000: #received_counter < args.terminate_after
        data, addr = serverSock.recvfrom(1500)  # receive up to 1500 bytes of data
        received_counter += 1
        # end_time = time.time()
                    #check if receive end packet
        # if data == b"END_OF_TRANSMISSION" :
        #     # end_packet_received = True
        #     end_time = time.time()
        #     break
        # if received_counter == 1000:
        #     end_time = time.time()
        #     break

        # print float value of pmu_packet_parser(data)["frame_size"]
        pmu_data = pmu_packet_parser(data)
        sorted_pmus.insert(pmu_data)

        # print(str(received_counter))
        print(str(received_counter) + " : " + str(pmu_data["sync"]) + " | " + "Magnitude: " + str(pmu_data["phasors"][0]["magnitude"]) + " | Phase_angle: " + str(pmu_data["phasors"][0]["angle"]))
        # for dp -> cp -> dp speed analysis
    end_time = time.time()
    with open('receiver_missing.txt','w') as f:
        f.write(f"End time: {end_time} \n")
        """
        if int.from_bytes(pmu_data["analog"], byteorder="big") != 0:
            print(str("Data plane -> Controller"))
            print(str(int.from_bytes(pmu_data["analog"], byteorder="big")))

        if int.from_bytes(pmu_data["digital"], byteorder="big") != 0:
            cntrl2dp = pmu_data["digital"] + pmu_data["chk"]
            print(str("Controller -> Data Plane"))
            print(str(int.from_bytes(cntrl2dp, byteorder="big")))
            #print(pmu_data["phasors"][0]["magnitude"])
        """
        # sorted_pmus.print_pmu()
