
## 阳历 Solar

**阳历的实例化有以下几种方式：**
Solar.fromYmd(year, month, day)
指定阳历年(数字)、阳历月(数字)、阳历日(数字)生成阳历对象。注意月份为1到12。

Solar.fromYmdHms(year, month, day, hour, minute, second)
指定阳历年(数字)、阳历月(数字)、阳历日(数字)、阳历小时(数字)、阳历分钟(数字)、阳历秒钟(数字)生成阳历对象。注意月份为1到12。

Solar.fromDate(date)
指定日期(Date)生成阳历对象

Solar.fromJulianDay(julianDay)
指定儒略日(小数)生成阳历对象

Solar.fromBaZi(yearGanZhi, monthGanZhi, dayGanZhi, timeGanZhi, sect, baseYear)
通过八字年柱、月柱、日柱、时柱获取匹配的阳历列表。sect为流派，可选1或2，不传则默认为2。baseYear为起始年份，支持最小传1，不传则默认为1900。该方法可能返回多条满足条件的记录。


## 阴历 Lunar

**阴历的实例化有以下几种方式：**
Lunar.fromYmd(lunarYear, lunarMonth, lunarDay)
指定阴历年(数字)、阴历月(数字)、阴历日(数字)生成阴历对象。注意月份为1到12，闰月为负，即闰2月=-2。

Lunar.fromYmdHms(lunarYear, lunarMonth, lunarDay, hour, minute, second)
指定阴历年(数字)、阴历月(数字)、阴历日(数字)、阳历小时(数字)、阳历分钟(数字)、阳历秒钟(数字)生成阴历对象。注意月份为1到12，闰月为负，即闰2月=-2。

Lunar.fromDate(date)
指定阳历日期(Date)生成阴历对象。

**获取阴历年、月**
.getYear()
获取阴历年(数字)

.getMonth()
获取阴历月(数字)

**获取阴历月天数**
阴历一个月只可能是30天或者29天。获取天数可以判断当月是大月(30天)还是小月(29天)。

.getDayCount()
获取当月天数
```
var lunarMonth = LunarMonth.fromYm(2021, 9);
console.log(lunarMonth.getDayCount());
```

***阴历转阳历***
阴历和阳历之间的相互转换。

.getSolar()
返回对应的阳历对象。
```
// 实例化
var lunar = Lunar.fromYmd(1986, 4, 21);

console.log(lunar);

// 转阳历
var solar = lunar.getSolar();

console.log(solar.toString());
console.log(solar.toFullString());
```