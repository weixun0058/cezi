import sxtwl
import datetime

# 天干地支表
gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 月支对应的节气索引（立春、惊蛰、清明...）
jie_qi_to_month_zhi = {
    0: 2,  2: 3,  4: 4,  6: 5,  8: 6, 10: 7, 
    12: 8, 14: 9, 16: 10, 18: 11, 20: 0, 22: 1
}

year_gan_to_start = {0:2,1:4,2:6,3:8,4:0,5:2,6:4,7:6,8:8,9:0}
day_gan_to_start = {0:0,1:2,2:4,3:6,4:8,5:0,6:2,7:4,8:6,9:8}

def get_month_zhi(dt):
    lunar = sxtwl.Lunar()
    jd = sxtwl.JD(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    jd = jd.jd

    # 获取前后两年的节气
    all_jq = []
    for y in [dt.year-1, dt.year, dt.year+1]:
        for i in range(24):
            jq_jd = lunar.getJieQiJD(y, i)
            all_jq.append( (y, i, jq_jd) )

    # 找到jd之前最近的节
    nearest_jie = None
    for y, i, jq_jd in sorted(all_jq, key=lambda x: x[2]):
        if jq_jd <= jd and i % 2 == 0:  # 只考虑“节”
            nearest_jie = (y, i, jq_jd)
        elif jq_jd > jd:
            break

    if nearest_jie and nearest_jie[1] in jie_qi_to_month_zhi:
        return jie_qi_to_month_zhi[nearest_jie[1]]
    return 2  # 默认寅月

def get_year_gan_zhi(year):
    return ((year -4) % 10, (year -4) % 12)

def get_day_gan_zhi(dt):
    day = sxtwl.fromSolar(dt.year, dt.month, dt.day)
    day_gz = day.getDayGZ()
    return (day_gz % 10, day_gz % 12)

def get_bazi(dt):
    lunar = sxtwl.Lunar()
    year = dt.year

    # 确定年柱
    jd_lichun = lunar.getJieQiJD(year, 0)
    lic_date = sxtwl.JD(jd_lichun).getSolar()
    lic_dt = datetime.datetime(lic_date.Y, lic_date.M, lic_date.D, 
                              lic_date.h, lic_date.m, int(lic_date.s))
    year_used = year if dt >= lic_dt else year-1
    yg, yz = get_year_gan_zhi(year_used)

    # 月柱
    mz = get_month_zhi(dt)
    mg = (year_gan_to_start[yg] + (mz - 2)) %10

    # 日柱
    dg, dz = get_day_gan_zhi(dt)

    # 时柱
    hour = dt.hour + dt.minute/60
    hz = int((hour +1)/2) %12
    hg = (day_gan_to_start[dg] + hz) %10

    return [(yg, yz), (mg, mz), (dg, dz), (hg, hz)]

def bazi_to_str(bazi):
    return ' '.join([f"{gan[g]}{zhi[z]}" for g, z in bazi])

# 示例：1990年3月18日10点30分
dt = datetime.datetime(1990, 3, 18, 10, 30)
bazi = get_bazi(dt)
print(bazi_to_str(bazi))  # 输出：庚午 己卯 壬午 乙巳