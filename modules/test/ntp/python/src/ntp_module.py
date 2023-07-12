# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""NTP test module"""
from test_module import TestModule
from scapy.all import rdpcap, NTP, IP

LOG_NAME = 'test_ntp'
NTP_SERVER_CAPTURE_FILE = '/runtime/network/ntp.pcap'
STARTUP_CAPTURE_FILE = '/runtime/device/startup.pcap'
MONITOR_CAPTURE_FILE = '/runtime/device/monitor.pcap'
LOGGER = None

class NTPModule(TestModule):
  """NTP Test module"""

  def __init__(self, module):
    super().__init__(module_name=module, log_name=LOG_NAME)
    # TODO: This should be fetched dynamically
    self._ntp_server = '10.10.10.5'

    global LOGGER
    LOGGER = self._get_logger()

  def _ntp_network_ntp_support(self):
    LOGGER.info('Running ntp.network.ntp_support')

    packet_capture = rdpcap(STARTUP_CAPTURE_FILE) + rdpcap(MONITOR_CAPTURE_FILE)

    device_sends_ntp4 = False
    device_sends_ntp3 = False

    for packet in packet_capture:

      if NTP in packet and packet.src == self._device_mac:
        if packet[NTP].version == 4:
          device_sends_ntp4 = True
          LOGGER.info(f'Device sent NTPv4 request to {packet[IP].dst}')
        elif packet[NTP].version == 3:
          device_sends_ntp3 = True
          LOGGER.info(f'Device sent NTPv3 request to {packet[IP].dst}')

    if not (device_sends_ntp3 or device_sends_ntp4):
      LOGGER.info('Device has not sent any NTP requests')

    return device_sends_ntp4 and not device_sends_ntp3

  def _ntp_network_ntp_dhcp(self):
    LOGGER.info('Running ntp.network.ntp_dhcp')

    packet_capture = rdpcap(STARTUP_CAPTURE_FILE) + rdpcap(MONITOR_CAPTURE_FILE)

    device_sends_ntp = False

    for packet in packet_capture:

      if NTP in packet and packet.src == self._device_mac:
        device_sends_ntp = True
        if packet[IP].dst == self._ntp_server:
          LOGGER.info('Device sent NTP request to DHCP provided NTP server')
          return True

    if not device_sends_ntp:
      LOGGER.info('Device has not sent any NTP requests')
    else:
      LOGGER.info('Device has not sent NTP requests to DHCP provided NTP server')

    return False
