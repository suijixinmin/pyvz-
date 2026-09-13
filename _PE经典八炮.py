# coding=utf-8
"""
阵名：PE经典八炮
出处：未知
节奏：P4:PP|PP|PP|PP(9,9,9,9)
"""

from pvz import *
import time

cob_crood = []
f = 0

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
    PlantsLoseCol = -1
    PlantsLoseRow = -1
            
    for i in range(0, plants_max):
        if ReadMemory("int", plants_offset + 0x24 + 0x14c * i) == plants_type:
            if ReadMemory("bool", plants_offset + 0x141 + 0x14c * i) == True:
                PlantsLoseCol = ReadMemory("int", plants_offset + 0x1c + 0x14c * i)
                PlantsLoseRow = ReadMemory("int", plants_offset + 0x28 + 0x14c * i)
    if PlantsLoseCol != -1:
        PlantsLoseCol += 1
        PlantsLoseRow += 1
        PlantsLoseColAndRow = (PlantsLoseCol, PlantsLoseRow)
        return PlantsLoseColAndRow
    return 0

ListCobCrood()

while(1):
    time.sleep(2)  # 选卡时概率出现的bug

    SelectCards([30])  # 南瓜头

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

        Prejudge(-199, wave)

        # 每波延迟炸（每9秒炸一次，每波延迟6秒炸）
        Until(500)
        Pao((2, 8), (5, 8))
        FireCobTime += 2
        PumpkinFix()

        # 当有红眼时，收尾额外多炸两轮
        if wave in (9, ):
            if a == 1:
                Delay(401)
                Pao((2, 8), (5, 8))
                FireCobTime += 2
            Delay(401)
            Pao((2, 8), (5, 8))
            FireCobTime += 2

        if wave in (19, ):
            if a == 1:
                Delay(401)
                Pao((2, 8), (5, 8))
                FireCobTime += 2
            Delay(401)
            Pao((2, 8), (5, 8))
            FireCobTime += 2

        if wave in (20, ):
            if a == 1:
                Delay(401)
                Pao((2, 8), (5, 8))
                FireCobTime += 2
            Delay(401)
            Pao((2, 8), (5, 8))
            FireCobTime += 2

    # 完成2f的详细报告
    f += 2
    print("\n----------分割线----------\n已经完成 2 f，此脚本从启用至今已累计完成",f ,"f\n阳光增长：", (ReadMemory("int", 0x6a9ec0, 0x768, 0x5560) - Sun),"\n----------分割线----------\n\n")
    Sun = ReadMemory("int", 0x6a9ec0, 0x768, 0x5560)

    cob_crood = relist(cob_crood, FireCobTime)
    print("现发炮顺序为：", cob_crood, "\n上 2 f共发射", FireCobTime)