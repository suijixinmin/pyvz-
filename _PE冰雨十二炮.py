# coding=utf-8
"""
阵名：PE火焰十二炮
出处：https://tieba.baidu.com/p/701647038#
节奏：P6: PP|PP|PP|PP|PP|PP
"""

from pvz import *
import time

# 全局变量
f = 0  # 脚本累计完成flag数
Sun = ReadMemory("int", 0x6a9ec0, 0x768, 0x5560)  # 目前阳光数量
FireCobTime = 0  # 计算发射次数，以制定发射列表
cob_crood = []  # [(3, 1), (4, 1), (3, 3), (4, 3), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (3, 7), (4, 7)]

# 根据发射次数重新排列发射顺序
def relist(cob_crood, n):
    n %= len(cob_crood)
    return cob_crood[n:] + cob_crood[:n]

# 修补南瓜头
def PumpkinFix():
    plants_offset = ReadMemory("int", 0x6a9ec0, 0x768, 0xac)
    plants_max = ReadMemory("int", 0x6a9ec0, 0x768, 0xb0)

    for i in range(0, plants_max):
        if ReadMemory("int", plants_offset + 0x24 + 0x14c * i) == 30 and ReadMemory("int", plants_offset + 0x40 + 0x14c * i) < 2666:
            PumpkinCooling = ReadMemory("int", 0x6a9ec0, 0x768, 0x144, 0x24 + 0x28 + 0x50 * 3)
            if PumpkinCooling == 0:
                Card(4, (ReadMemory("int", plants_offset + 0x1c + 0x14c * i) + 1, ReadMemory("int", plants_offset + 0x28 + 0x14c * i) + 1))

# 开局整理发炮顺序
def ListCobCrood():
    global cob_crood
    plants_offset = ReadMemory("int", 0x6a9ec0, 0x768, 0xac)
    plants_max = ReadMemory("int", 0x6a9ec0, 0x768, 0xb0)
    cob_temp = 0
    ct = []
    for i in range(0, plants_max):
        if ReadMemory("int", plants_offset + 0x24 + 0x14c * i) == 47:
            ct.append(ReadMemory("int", plants_offset + 0x54 + 0x14c * i))
            cob_crood.append((ReadMemory("int", plants_offset + 0x1c + 0x14c * i) + 1, ReadMemory("int", plants_offset + 0x28 + 0x14c * i) + 1))
    for i in range(0, len(cob_crood)):
         for j in range(0, len(cob_crood) - i - 1):
            if ct[j] > ct[j + 1]:
                cob_temp = ct[j]
                ct[j] = ct[j + 1]
                ct[j + 1] = cob_temp
                cob_temp = cob_crood[j]
                cob_crood[j] = cob_crood[j + 1]
                cob_crood[j + 1] = cob_temp

# 找出并返回阵型中某个植物的所有位置
def FindPlantsInLineup(plants_type):
    plants_offset = ReadMemory("int", 0x6a9ec0, 0x768, 0xac)
    plants_max = ReadMemory("int", 0x6a9ec0, 0x768, 0xb0)
    PlantsList = []

    for i in range(0, plants_max):
        if ReadMemory("int", plants_offset + 0x24 + 0x14c * i) == plants_type:
            PlantsList.append((ReadMemory("int", plants_offset + 0x1c + 0x14c * i) + 1, ReadMemory("int", plants_offset + 0x28 + 0x14c * i) + 1))
    if PlantsList != []:
        return PlantsList
    else:
        print("场上并未存在该植物类型")
        return 1

# 找出并返回某一个失去的植物位置
def FindDeadPlantsInLineup(plants_type):
    plants_offset = ReadMemory("int", 0x6a9ec0, 0x768, 0xac)
    plants_max = ReadMemory("int", 0x6a9ec0, 0x768, 0xb0)
    PlantsLoseCol = 0
    PlantsLoseRow = 0
            
    for i in range(0, plants_max):
        if ReadMemory("int", plants_offset + 0x24 + 0x14c * i) == plants_type:
            if ReadMemory("bool", plants_offset + 0x141 + 0x14c * i) == "true":
                PlantsLoseCol = ReadMemory("int", plants_offset + 0x1c + 0x14c * i)
                PlantsLoseRow = ReadMemory("int", plants_offset + 0x28 + 0x14c * i)
    if PlantsLoseCol != 0:
        PlantsLoseColAndRow = (PlantsLoseCol, PlantsLoseRow)
        return PlantsLoseColAndRow
    return 0

Plants_List = FindPlantsInLineup(41)
ListCobCrood()

while(1):
    time.sleep(2)  # 选卡时概率出现的bug

    SelectCards([8, 14, 35, 30, 1])  # 小喷 寒冰菇 咖啡豆 南瓜头 向日葵

    AutoCollect()  # 自动收集资源

    FireCobTime = 0

    UpdatePaoList(cob_crood)

    a, b, c, d = 0, 0, 0, 0

    for wave in range(1, 21):
        # 看看9、19、20有没有红眼，需不需要炸两轮
        if a != 1 and wave in (1, ):
            for zom in range(0xcf4, 0xdbc):
                if ReadMemory("int", 0x6a9ec0, 0x768, zom) == 32:
                    a = 1
                    break
        if b != 1 and wave in (1, ):
            for zom in range(0x14c4, 0x158c):
                if ReadMemory("int", 0x6a9ec0, 0x768, zom) == 32:
                    b = 1
                    break
        if c != 1 and wave in (1, ):
            for zom in range(0x158c, 0x1654):
                if ReadMemory("int", 0x6a9ec0, 0x768, zom) == 32:
                    c = 1
                    break

        print("当前操作波次: " + str(wave))
        
        # 关底冰消珊瑚，经过测试阳光会回升，且更加稳定
        if wave in (20, ):
            Prejudge(-350, 20)
            plants_offset = ReadMemory("int", 0x6a9ec0, 0x768, 0xac)
            plants_max = ReadMemory("int", 0x6a9ec0, 0x768, 0xb0)
            # 如果没有存冰，默认将会在一行九列的位置种植寒冰菇，可自行修改
            for i in range(0, plants_max):
                if ReadMemory("int", plants_offset + 0x24 + 0x14c * i) == 14:
                    Card(3, (ReadMemory("int", plants_offset + 0x14 + 0x14c * i) + 1, ReadMemory("int", plants_offset + 0x28 + 0x14c * i) + 1))
                    Card(2, (ReadMemory("int", plants_offset + 0x14 + 0x14c * i) + 1, ReadMemory("int", plants_offset + 0x28 + 0x14c * i) + 1))
                    break
                else:
                    Card(2, (1, 9))
                    Card(3, (1, 9))
                    break

        Prejudge(-199, wave)

        # 每波预判炸
        Until(-95)
        if wave in (10, 20):
            Until(-40)
        Pao((2, 9), (5, 9))
        FireCobTime += 2
        PumpkinFix()

        # 当有红眼时，收尾额外多炸两轮
        if wave in (9, ):
            if a == 1:
                Delay(601)
                Pao((2, 9), (5, 9))
                FireCobTime += 2
            Delay(601)
            Pao((2, 9), (5, 9))
            FireCobTime += 2

        if wave in (19, ):
            if a == 1:
                Delay(601)
                Pao((2, 9), (5, 9))
                FireCobTime += 2
            Delay(601)
            Pao((2, 9), (5, 9))
            FireCobTime += 2

        if wave in (20, ):
            if a == 1:
                Delay(601)
                Pao((2, 9), (5, 9))
                FireCobTime += 2
            Delay(601)
            Pao((2, 9), (5, 9))
            FireCobTime += 2

        DeadPlants_cr = FindDeadPlantsInLineup(41)
        if DeadPlants_cr != 0:
            Card(5, DeadPlants_cr)
            Card(7, DeadPlants_cr)

    # 完成2f的详细报告
    f += 2
    print("\n----------分割线----------\n已经完成 2 f，此脚本从启用至今已累计完成",f ,"f\n阳光增长：", (ReadMemory("int", 0x6a9ec0, 0x768, 0x5560) - Sun),"\n----------分割线----------\n\n")
    Sun = ReadMemory("int", 0x6a9ec0, 0x768, 0x5560)

    cob_crood = relist(cob_crood, FireCobTime)
    print("现发炮顺序为：", cob_crood, "\n上 2 f共发射", FireCobTime)