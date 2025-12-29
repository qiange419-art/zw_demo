import struct
import time
import serial

# 定义接受数据的字典
receive_dict={
    "注册次数": None,
    "指纹模板大小": None,
    "指纹库大小": None,
    "分数等级": None,
    "设备地址": None,
    "数据包大小": None,
    "波特率设置": None
}





HEADER="EF01"
ADDRESS="FFFFFFFF"
ser=serial.Serial("COM3",57600)
print(ser.is_open)

# 数据解析模块
def read_data_from_finger(timeout):
     # 读出数据
        start_time=time.time()
        receive_data=bytearray()
        while time.time() - start_time <timeout:
            # 缓冲区是否有数据
            if ser.in_waiting > 0:
                temp_data= ser.read(ser.in_waiting)
                receive_data.extend(temp_data)
            time.sleep(0.01)  # 短暂等待避免CPU占用过高
        print(receive_data)
        # 先判断大小，在判断包头，在校验，最后取数据
        if len(receive_data)>2+4+1+2+1:
            # 在判断是否找到包头
            head_idx=receive_data.find(bytes.fromhex(HEADER))
            if head_idx!=-1:
                data=receive_data[:10]   #对应该信号进行解析
                result=struct.unpack(">HIBHB",data)
                # 计算校验码
                comfirm_code=result[4]
                data=receive_data[10:-2] #数据部分
                receive_code=receive_data[-2:] #接受的校验码
                check_code=sum(receive_data[6:-2])
                # print(f"接收到的校验码是{receive_code},计算的校验码是{check_code}")
                return comfirm_code ,data
def PS_ReadSysPara():
        # 创建一个字节数组
        data=bytearray()
        data.extend(bytes.fromhex(HEADER)) #  包头
        data.extend(bytes.fromhex(ADDRESS))# 设备地址
        data.append(0x01) #包表示  指令表示
        data.extend(0x0003.to_bytes(2)) #包长度
        data.append(0x0f)  #指令码
        data.extend(0x0013.to_bytes(2))
        # 验证码进行校验
        check_sum=hex(sum(data[6:-2]))
        print(check_sum,data)
        ser.write(data)
        print("*"*50)
        # 读出数据
        start_time=time.time()
        receive_data=bytearray()
        while time.time() - start_time <0.5:
            if ser.in_waiting > 0:
                temp_data= ser.read(ser.in_waiting)
                receive_data.extend(temp_data)
            time.sleep(0.01)  # 短暂等待避免CPU占用过高
        print(receive_data)
        # 对接受的数据进行解析 通过大小进行判断
        # 先判断大小，在判断包头，在校验，最后取数据
        if len(receive_data)>2+4+1+2+1:
            # 在判断是否找到包头
            head_idx=data.find(bytes.fromhex(HEADER))
            if head_idx!=-1:
                data=receive_data[:10]   #对应该信号进行解析
                result=struct.unpack(">HIBHB",data)
                print(f"解析结果: 包头=0x{result[0]:04X}, 地址=0x{result[1]:08X}, 标识=0x{result[2]:02X}, 长度={result[3]},确认吗={result[4]}")
                # 计算校验码
                check_code=result[4]
                if check_code==0x00:
                    print("校验成功")
                    # 对数据进行解析
                    data=receive_data[10:-2]
                    result=struct.unpack(">HHHHIHH",data)
                    receive_dict.update({
                         "注册次数": result[0],
                        "指纹模板大小": result[1],
                        "指纹库大小": result[2],
                        "分数等级": result[3],
                        "设备地址": result[4],
                        "数据包大小": result[5],
                        "波特率设置": result[6]*9600
                    })
                    print(receive_dict)
                else:
                    print("校验失败")
# 注册用获取图像
def PS_GetEnrollImage():
     # 创建一个字节数组
        data=bytearray()
        data.extend(bytes.fromhex(HEADER)) #  包头
        data.extend(bytes.fromhex(ADDRESS))# 设备地址
        data.append(0x01) #包表示  指令表示
        data.extend(0x0003.to_bytes(2)) #包长度
        data.append(0x29)  #指令码
        data.extend(0x002D.to_bytes(2))
        ser.write(data)
        print("*"*50)
        # 接受数据
        comfirm_code ,data=read_data_from_finger(0.5)
        if comfirm_code==0x00:
            print("成功")
            return True
        else:
            print("失败")
            return False
# 生成特征 
def PS_GenChar(BufferID):
    # 创建一个字节数组
    data=bytearray()
    data.extend(bytes.fromhex(HEADER)) #  包头
    data.extend(bytes.fromhex(ADDRESS))# 设备地址
    data.append(0x01) #包表示  指令表示
    data.extend(0x0004.to_bytes(2)) #包长度
    data.append(0x02)  #指令码
    data.append(BufferID)  #指令码
    # 验证码进行校验
    check_sum=hex(sum(data[6:]))
    data.extend(check_sum.to_bytes(2))
    ser.write(data)
    comfirm_code ,data=read_data_from_finger(0.5)
    if comfirm_code==0x00:
            print("成功")
            return True
    else:
        print("失败")
        return False
# 合并特征（生成模板）
def PS_RegModel():
    data=bytearray()
    data.extend(bytes.fromhex(HEADER)) #  包头
    data.extend(bytes.fromhex(ADDRESS))# 设备地址
    data.append(0x01) #包表示  指令表示
    data.extend(0x0003.to_bytes(2)) #包长度
    data.append(0x05)  #指令码
    data.extend(0x0009.to_bytes(2))
    ser.write(data)
    comfirm_code ,data=read_data_from_finger(0.5)
    comfirm_code ,data=read_data_from_finger(0.5)
    if comfirm_code==0x00:
            print("成功")
            return True
    else:
        print("失败")
        return False
#储存模板 
def PS_StoreChar(BufferID,PageID):
    data=bytearray()
    data.extend(bytes.fromhex(HEADER)) #  包头
    data.extend(bytes.fromhex(ADDRESS))# 设备地址
    data.append(0x01) #包表示  指令表示
    data.extend(0x0006.to_bytes(2)) #包长度
    data.append(0x06)  #指令码
    data.append(BufferID)  #指令码
    data.extend(PageID.to_bytes(2))
    # 验证码进行校验
    check_sum=hex(sum(data[6:]))
    data.extend(check_sum.to_bytes(2))
    ser.write(data)
    comfirm_code ,data=read_data_from_finger(0.5)
    if comfirm_code==0x00:
        print("成功")
        return True
    else:
        print("失败")
        return False
if __name__=="__main__":
    # PS_ReadSysPara()
    while True:
        flag=PS_GetEnrollImage()
        if flag:
            break
        else:
            print("获取图像失败")
            time.sleep(1)
    