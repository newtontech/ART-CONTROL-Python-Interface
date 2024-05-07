'''
[DAM-3060V]
ChannelNum=4
RangeNum=4
RangeAddr=272
AOAddr=352
lChanAddr = 2
AOMode0=-10V ～ 10V
-10V ～ 10V=9
AOMode1=- 5V ～ 5V
- 5V ～ 5V=8
AOMode2=  0V ～ 10V
0V ～ 10V=14
AOMode3=  0V ～ 5V
0V ～ 5V=13

请选择波特率：
 0: 1200 bps
 1: 2400 bps
 2: 4800 bps
 3: 9600 bps
 4: 19200 bps
 5: 38400 bps
 6: 57600 bps
 7: 115200 bps
'''



'''
[DAM-3151]
ChannelNum=32
lShareRangeChannel=0
RangeNum=12
RangeAddr=137
fLsbType=65535.0
lRangeStretch = 0
CHEnable=1
CHEnableAddr=221
ADAddr=1
ADDataBits=2
IEnableType = 1
ADMode0=-10 ～ 10V
-10 ～ 10V=9
ADMode1=-5 ～ 5V
-5 ～ 5V=8
ADMode2=-1 ～ 1V
-1 ～ 1V=6
ADMode3=-500 ～ 500mV
-500 ～ 500mV=5
ADMode4=-150 ～ 150mV
-150 ～ 150mV=4
ADMode5=0 ～ 10V
0 ～ 10V=14
ADMode6=0 ～ 5V
0 ～ 5V=13
ADMode7=1 ～ 5V
1 ～ 5V=130
ADMode8=-20 ～ 20mA
-20 ～ 20mA=10
ADMode9=0 ～ 20mA
0 ～ 20mA=11
ADMode10=4 ～ 20mA
4 ～ 20mA=12
ADMode11=0 ～ 22mA
0 ～ 22mA=128

'''

from math import ceil
import ctypes
from ctypes import wintypes

# Load the DLL
dll_path = "./DAM3000M_64.dll"
dam3000m = ctypes.WinDLL(dll_path)

# Define necessary structures and constants
class DeviceInfo(ctypes.Structure):
    _fields_ = [
        ("DeviceType", wintypes.LONG),
        ("TypeSuffix", wintypes.LONG),
        ("ModusType", wintypes.LONG),
        ("VesionID", wintypes.LONG),
        ("DeviceID", wintypes.LONG),
        ("BaudRate", wintypes.LONG),
        ("bParity", wintypes.LONG)
    ]

# Define function prototypes
DAM3000M_CreateDevice = dam3000m.DAM3000M_CreateDevice
DAM3000M_CreateDevice.argtypes = [wintypes.LONG]
DAM3000M_CreateDevice.restype = wintypes.HANDLE

DAM3000M_InitDevice = dam3000m.DAM3000M_InitDevice
DAM3000M_InitDevice.argtypes = [wintypes.HANDLE, wintypes.LONG, wintypes.LONG, wintypes.LONG, wintypes.LONG, wintypes.LONG, wintypes.LONG]
DAM3000M_InitDevice.restype = wintypes.BOOL

DAM3000M_ReleaseDevice = dam3000m.DAM3000M_ReleaseDevice
DAM3000M_ReleaseDevice.argtypes = [wintypes.HANDLE]
DAM3000M_ReleaseDevice.restype = wintypes.BOOL

DAM3000M_GetDeviceInfo = dam3000m.DAM3000M_GetDeviceInfo
DAM3000M_GetDeviceInfo.argtypes = [wintypes.HANDLE, wintypes.LONG, ctypes.POINTER(DeviceInfo)]
DAM3000M_GetDeviceInfo.restype = wintypes.BOOL

DAM3000M_WriteMultiRegsUInt32=dam3000m.DAM3000M_WriteMultiRegsUInt32
DAM3000M_WriteMultiRegsUInt32.argtypes = [wintypes.HANDLE, wintypes.LONG, wintypes.LONG, wintypes.LONG, ctypes.POINTER(wintypes.ULONG)]
DAM3000M_WriteMultiRegsUInt32.restype = wintypes.BOOL

DAM3000M_WriteMultiRegsUInt16=dam3000m.DAM3000M_WriteMultiRegsUInt16
DAM3000M_WriteMultiRegsUInt16.argtypes = [wintypes.HANDLE, wintypes.LONG, wintypes.LONG, wintypes.LONG, ctypes.POINTER(wintypes.USHORT)]
DAM3000M_WriteMultiRegsUInt16.restype = wintypes.BOOL

DAM3000M_WriteSingleReg=dam3000m.DAM3000M_WriteSingleReg
DAM3000M_WriteSingleReg.argtypes = [wintypes.HANDLE, wintypes.LONG, wintypes.LONG, wintypes.ULONG]
DAM3000M_WriteSingleReg.restype = wintypes.BOOL


DAM3000M_ReadInputRegsUInt16=dam3000m.DAM3000M_ReadInputRegsUInt16
DAM3000M_ReadInputRegsUInt16.argtypes=[wintypes.HANDLE, wintypes.LONG, wintypes.INT, wintypes.INT, ctypes.POINTER(wintypes.USHORT)]

class DAMDevice:
    handles={}
    def __init__(self, com_id: int, baud_rate: int,device_id:int):
        self.com_id = com_id
        self.baud_rate = baud_rate
        self.device_id = device_id
        self.handle=self._get_handle()
        self.get_device_info(device_id)
    def _get_handle(self):
        if self.com_id not in self.handles:
            handle=DAM3000M_CreateDevice(self.com_id)
            assert handle not in (-1,None, 0) ,"Failed to create device."
            assert DAM3000M_InitDevice(handle, self.baud_rate, 8, 0, 0x00, 200, 0),"Failed to initialize device."
            self.handles[self.com_id]=handle
        return self.handles[self.com_id]
    @property
    def device_name(self):
        return f"Device Model: DAM-{self.device_info.DeviceType:02X}{chr(self.device_info.TypeSuffix >> 8 & 0xFF)}".removesuffix(' ')

    def get_device_info(self,device_id):
        self.device_info = DeviceInfo()
        assert DAM3000M_GetDeviceInfo(self.handle, device_id, ctypes.byref(self.device_info)),"Failed to get device info."
        
    def __exit__(self):
        assert DAM3000M_ReleaseDevice(self.handle),"Failed to release device."

class DAM3060V(DAMDevice):
    AOAddr = 352
    RangeAddr = 272
    ChannelNum = 4
    RangeNum = 4
    ChannelAddr = 2
    RangeModes = {
        9: (-10, 10),   # Mode 0: -10V to 10V
        8: (-5, 5),     # Mode 1: -5V to 5V
        14: (0, 10),     # Mode 2: 0V to 10V
        13: (0, 5)       # Mode 3: 0V to 5VW
    }
    ModeList=[8,8,8,8]
    def __init__(self, com_id, baud_rate,device_id):
        super().__init__(com_id, baud_rate,device_id)
        for lChannel in range(self.ChannelNum):
            self.set_output_range_mode(lChannel, self.ModeList[lChannel])
    def set_analog_output(self, lChannel:int, value:float):
        range_bottom, range_top = self.RangeModes[self.ChannelModes[lChannel]]
        dal_lsb = ceil((value - range_bottom) * 0xFFF / (range_top - range_bottom))
        assert DAM3000M_WriteMultiRegsUInt32(self.handle, self.device_id, self.AOAddr + lChannel * self.ChannelAddr, 1, ctypes.byref(ctypes.c_ulong(dal_lsb))) ,"Failed to set analog output."
    def set_output_range_mode(self, lChannel:int, range_mode:int):
        assert range_mode in self.RangeModes
        assert DAM3000M_WriteSingleReg(self.handle,self.device_id,self.RangeAddr+lChannel,range_mode),f'Failed to set range mode for  {self.handle=}, {self.device_id =}, {self.RangeAddr+lChannel =}, {range_mode =}.'
        self.ChannelModes[lChannel]=range_mode


class DAM3151(DAMDevice):
    ChannelNum=32
    lShareRangeChannel=0
    RangeNum=12
    RangeAddr=137-1
    fLsbType=65535.0
    lRangeStretch = 0
    CHEnable=1
    CHEnableAddr=221
    ADAddr=0#??? 0 1 
    ADDataBits=2
    IEnableType = 1
    RangeModes = {
        9: (-10, 10),    # Mode 0: -10V to 10V
        8: (-5, 5),      # Mode 1: -5V to 5V
        14: (0, 10),     # Mode 5: 0V to 10V
        13: (0, 5),      # Mode 6: 0V to 5V
        130: (1, 5),     # Mode 7: 1V to 5V
        10: (-20, 20),   # Mode 8: -20mA to 20mA
        11: (0, 20),     # Mode 9: 0mA to 20mA
        12: (4, 20),     # Mode 10: 4mA to 20mA
        128: (0, 22)     # Mode 11: 0mA to 22mA
    }
    ModeList=[10 if not i%2 else 8 for i in range(ChannelNum)]
    def __init__(self, com_id, baud_rate,device_id):
        super().__init__(com_id, baud_rate,device_id)
        self._enable_channel()
        for channel in range(self.ChannelNum):
            self.set_measurement_range_mode(channel, self.ModeList[channel])
    def _enable_channel(self):
        mask=(1 << self.ChannelNum) - 1
        assert DAM3000M_WriteSingleReg(self.handle,self.device_id,self.CHEnableAddr,mask),f'Failed to enable {self.handle,self.device_id,self.CHEnableAddr}.'
    def _data_converter(self,raw_data:int,range_top:float,range_bottom:float):
        return raw_data/self.fLsbType*(range_top-range_bottom)+range_bottom
    def measure_all_channels_mA_V(self):
        buffer_type = ctypes.c_ushort * self.ChannelNum
        data_buffer = buffer_type()
        assert DAM3000M_ReadInputRegsUInt16(self.handle, self.device_id, self.ADAddr, self.ChannelNum, data_buffer),f'Failed to set {self.handle=}, {self.device_id =}, {self.ADAddr =}, {self.ChannelNum =}, {data_buffer =}.'
        current_list_in_mA=[self._data_converter(data_buffer[i*2],*self.RangeModes[self.ModeList[i*2]]) for i in range(self.ChannelNum//2)]
        voltage_list_in_V=[self._data_converter(data_buffer[i*2+1],*self.RangeModes[self.ModeList[i*2+1]]) for i in range(self.ChannelNum//2)]
        return current_list_in_mA,voltage_list_in_V
    def set_measurement_range_mode(self, lChannel:int,range_mode:int):
        assert range_mode in self.RangeModes
        self.Current_Range_Mode=range_mode
        assert DAM3000M_WriteSingleReg(self.handle,self.device_id,self.RangeAddr+lChannel,range_mode),f'Failed to set range mode for  {self.handle=}, {self.device_id =}, {self.RangeAddr+lChannel =}, {range_mode =}.'



# DAM3151_device=DAM3151(4,3,5)
# data=DAM3151_device.measure_all_channels_mA_V()
# print(data)

# class ChannelController:
#     DAM3060V_device_id_list=[1,2,3,4]
#     DAM3151_device_id_list=[5]
#     def __init__(self,com_id:int,baud_rate:int) -> None:
#         self.DAM3060V_device_list=[DAM3060V(com_id,baud_rate,device_id) for device_id in self.DAM3060V_device_id_list]
#         self.DAM3151_device=DAM3151(com_id,baud_rate,self.DAM3151_device_id_list[0])
#     def __enter__(self):
#         return self
#     def __exit__(self):
#         for device in self.DAM3060V_device_list:
#             device.__exit__()
#         self.DAM3151_device.__exit__()
#     def ChannelController(self,channel:int):
#         assert channel in range(16)
#         #create 16 channel, channel 0-15.
#         #voltage controller: channel 0-3 are (analog output lChannel=0-3) of DAM3060V device_id 1, and so on. each device_id of DAM3060V controls 4 channels. 4-7 are (analog output lChannel=0-3) of DAM3060V device_id 2, 8-11 are (analog output lChannel=0-3) of DAM3060V device_id 3, 12-15 are (analog output lChannel=0-3) of DAM3060V device_id 4.
#         #measurement controller: channel 0 current is measured by DAM3151 device_id 5, lChannel=0, voltage is measured by DAM3060V device_id 5, lChannel=1. channel i current is measured by DAM3151 device_id 5, lChannel=2*i, voltage is measured by DAM3060V device_id 5, lChannel=2*i+1.
#         pass
#     def set_output_manually(self,channel:int,voltage_V:float):
#         from math import floor
#         device_id_3060V=floor(channel/4)
#         lChannel=channel%4
#         self.DAM3060V_device_list[device_id_3060V].set_analog_output(lChannel,voltage_V)
#     def measure_current(self,channel:int):
#         channel_id_3151=channel*2
#         device_id_3151=5
#         data_list=self.DAM3151_device.measure_all_channels_mA_V()















def main_3151():
    device = DAM3151(com_id=4, baud_rate=3, device_id=5)
    import time
    t0=time.time()
    for i in range(10):
        device.calc_measurement_data(device.det_raw_measurement_data())
    t1=time.time()
    print(f'Time used: {t1-t0:.6f} s')
def main_3060V():
    devices_3060_4=[DAM3060V(com_id=4,baud_rate=3,device_id=i) for i in range(1,5)]
    for device in devices_3060_4:
        for channel in range(4):
            device.set_output_range_mode(channel, 8)  # Set channel -5 to 5V range mode
            device.set_analog_output(channel, 2)

if __name__ == '__main__':
    main_3060V()
    main_3151()

