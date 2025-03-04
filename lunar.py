from lunar_python import Lunar

lunar = Lunar(1986, 4, 21,21,15,00)

#获取节日
l = lunar.getFestivals()
if l:
    print(l)
else:
    print("不是节日")
#获取干支，年月日
gz_year=lunar.getYearInGanZhi()
print(gz_year)

gz_month=lunar.getMonthInGanZhi()
print(gz_month)

gz_day=lunar.getDayInGanZhi()
print(gz_day)

#获取干支，时辰
gz_hour=lunar.getTimeInGanZhi()
print(gz_hour)


#获取生肖，年
sx_year=lunar.getYearShengXiao()
print(sx_year)


#获取节气
jq=lunar.getJieQi()
if jq:
    print(jq)
else:
    print("没有节气")

#彭祖百忌
bj_gan=lunar.getPengZuGan()
bj_zhi=lunar.getPengZuZhi()
bzbj=bj_gan+'\n'+bj_zhi
print(bzbj)

#喜神方位
xi=lunar.getDayPositionXi()
xi_desc=lunar.getDayPositionXiDesc()
print(f'喜神方位：{xi}，{xi_desc}')


#福神方位
fu=lunar.getDayPositionFu()
fu_desc=lunar.getDayPositionFuDesc()
print(f'福神方位：{fu}，{fu_desc}')

#财神方位
cai=lunar.getDayPositionCai()
cai_desc=lunar.getDayPositionCaiDesc()
print(f'财神方位：{cai}，{cai_desc}')


#宜
yi=lunar.getDayYi()
print(yi)

#忌
ji=lunar.getDayJi()
print(ji)

#吉神凶煞
ji_shen=lunar.getDayJiShen()
xiong_sha=lunar.getDayXiongSha()
print(f'吉神宜趋：{ji_shen}')
print(f'凶煞宜忌：{xiong_sha}')














