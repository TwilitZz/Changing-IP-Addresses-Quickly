from asyncio.windows_events import NULL
import os
import random
import re
import configparser
from time import sleep
from wmi import WMI

conf = configparser.ConfigParser()
conf.read("config\\ip_config.ini")

allConf = conf.sections()
i = 0
print("选择要加载的环境：")
for section in allConf:
    print((str(i+1)) + ": " + section)
    i = i+1
confIndex = int(input())-1
ipaddress = [conf.get(allConf[confIndex], "ipaddress")]
subnetMask = [conf.get(allConf[confIndex], "subnetMask")]
gateways = [conf.get(allConf[confIndex], "gateways")]
dns = [conf.get(allConf[confIndex], "dns")]


class updateIP:
    def __init__(self):
        self.wmiService = WMI()
        # 获取到本地有网卡信息
        self.colNicConfigs = self.wmiService.Win32_NetworkAdapterConfiguration(
            IPEnabled=True)

    def getAdapter(self):
        index = 0
        # 遍历所有网卡，找到要修改的那个，这里我是用原ip的第一段正则出来的
        for obj in self.colNicConfigs:
            # print(obj)
            adapter = re.findall("QCA9377", obj.Description)
            if len(adapter) > 0:
                return index
            else:
                index = index+1

    def runSet(self):
        adapter = self.colNicConfigs[self.getAdapter()]
        if (ipaddress[0] == ""):
            adapter.EnableDHCP()
            adapter.SetDNSServerSearchOrder()
            sleep(3)
            # 刷新DNS缓存使DNS生效
            os.system('ipconfig /flushdns')
            return print("设置为动态DHCP")
        arrGatewayCostMetrics = [1]  # 这里要设置成1，代表非自动选择
        # 开始执行修改ip、子网掩码、网关
        ipRes = adapter.EnableStatic(
            IPAddress=ipaddress, SubnetMask=subnetMask)
        if ipRes[0] == 0:
            print(u'\ttip:设置IP成功')
            print(u'\t当前ip：%s' % ipaddress[0])
        else:
            if ipRes[0] == 1:
                print(u'\ttip:设置IP成功，需要重启计算机！')
            else:
                print(u'\ttip:修改IP失败: IP设置发生错误')
                return False
        # 开始执行修改dns
        wayRes = adapter.SetGateways(
            DefaultIPGateway=gateways, GatewayCostMetric=arrGatewayCostMetrics)
        if wayRes[0] == 0:
            print(u'\ttip:设置网关成功')
        else:
            print(u'\ttip:修改网关失败: 网关设置发生错误')
            return False
        dnsRes = adapter.SetDNSServerSearchOrder(
            DNSServerSearchOrder=dns)
        if dnsRes[0] == 0:
            print(u'\ttip:设置DNS成功,等待3秒刷新缓存')
            sleep(3)
            # 刷新DNS缓存使DNS生效
            os.system('ipconfig /flushdns')
        else:
            print(u'\ttip:修改DNS失败: DNS设置发生错误')
            return False


if __name__ == '__main__':
    update = updateIP()
    update.runSet()
