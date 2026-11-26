from pathlib import Path

source = Path('project/app/src/main/java/com/hijoozati/app/MainActivity.kt')
if not source.is_file():
    raise SystemExit('MainActivity.kt is missing')
text = source.read_text(encoding='utf-8')
# The schedule includes the midnight start slot; it is sorted/displayed as 12:00 AM.
text = text.replace('(15..23).toList()', '(15..23).toList()+listOf(0)')
source.write_text(text, encoding='utf-8')
required = [
    'class LocalDb(c:android.content.Context):SQLiteOpenHelper(c,"hijoozati.db",null,6)',
    'tournament_groups',
    'private fun advanceTournament(id:Long)',
    'private fun groupStandings(id:Long,group:String)',
    'playerBelongsToFixture',
    'private fun hour(h:Int)',
    'setPadding(dp(14),dp(8),dp(14),dp(8))',
    '(15..23).toList()+listOf(0)',
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit('Required application features missing: ' + ', '.join(missing))
if 'hourRange' in text:
    raise SystemExit('The UI must display only the booking start time, not a time range')


# Replace the dashboard and bottom navigation with the approved full-screen redesign.
home_start = text.index(' private fun home(){')
home_end = text.index(' private fun bookingPage(){', home_start)
new_home = r''' private fun home(){
  val today=dateStr(Calendar.getInstance())
  val todays=db.bookingsFor(today)
  val tournaments=db.tournaments()
  val fixtures=tournaments.sumOf{db.fixtures(it.id).size}
  val available=(15..23).count{h->todays.none{it.hour==h}}+if(todays.none{it.hour==0})1 else 0

  val hero=LinearLayout(this).apply{
   orientation=1
   background=GradientDrawable(GradientDrawable.Orientation.TL_BR,intArrayOf(Color.rgb(83,39,125),Color.rgb(35,25,57),Color.rgb(18,19,32))).apply{
    cornerRadius=dp(23).toFloat();setStroke(dp(1),Color.rgb(126,78,178))
   }
   setPadding(dp(16),dp(15),dp(16),dp(15))
  }
  val heroTop=LinearLayout(this).apply{orientation=0;gravity=Gravity.CENTER_VERTICAL}
  val logo=ImageView(this).apply{setImageResource(R.drawable.hijoozati_logo);scaleType=ImageView.ScaleType.FIT_CENTER;background=GradientDrawable().apply{shape=GradientDrawable.OVAL;setColor(Color.rgb(255,255,255));setStroke(dp(2),Color.rgb(194,148,255))};setPadding(dp(5),dp(5),dp(5),dp(5))}
  heroTop.addView(logo,LinearLayout.LayoutParams(dp(54),dp(54)))
  val brand=LinearLayout(this).apply{orientation=1;gravity=Gravity.CENTER_VERTICAL}
  brand.addView(txt("حجوزاتي",23f,Palette.white,true).apply{gravity=Gravity.RIGHT})
  brand.addView(txt("إدارة الملعب والحجوزات",11f,Color.rgb(218,202,238)).apply{gravity=Gravity.RIGHT})
  heroTop.addView(brand,LinearLayout.LayoutParams(0,-2,1f).apply{marginStart=dp(10)})
  val datePill=txt(dateLabel(today),11f,Palette.white,true).apply{background=GradientDrawable().apply{cornerRadius=dp(11).toFloat();setColor(Color.argb(55,255,255,255));setStroke(dp(1),Color.argb(70,255,255,255))};setPadding(dp(10),dp(8),dp(10),dp(8))}
  heroTop.addView(datePill)
  hero.addView(heroTop)
  hero.addView(txt("كل مواعيد ملعبك في مكان واحد",17f,Palette.white,true).apply{gravity=Gravity.RIGHT;setPadding(0,dp(15),0,dp(2))})
  hero.addView(txt("تابع الحجوزات، نظّم الفرق، وأدر البطولات بسهولة.",11f,Color.rgb(218,202,238)).apply{gravity=Gravity.RIGHT})
  val heroActions=LinearLayout(this).apply{orientation=0;gravity=Gravity.CENTER_VERTICAL}
  heroActions.addView(btn("＋ حجز جديد",{page="bookings";showApp()},true),LinearLayout.LayoutParams(0,dp(49),1f).apply{marginEnd=dp(6);topMargin=dp(12)})
  heroActions.addView(btn("حجز ثابت",{page="fixed";showApp()},false),LinearLayout.LayoutParams(0,dp(49),1f).apply{marginStart=dp(6);topMargin=dp(12)})
  hero.addView(heroActions)
  content.addView(hero,LinearLayout.LayoutParams(-1,-2).apply{topMargin=dp(5)})

  gap(17)
  val section=LinearLayout(this).apply{orientation=0;gravity=Gravity.CENTER_VERTICAL}
  section.addView(txt("ملخص الملعب",17f,Palette.white,true).apply{gravity=Gravity.RIGHT},LinearLayout.LayoutParams(0,-2,1f))
  section.addView(txt("اليوم",10.5f,Palette.gold,true).apply{background=panel(10);setPadding(dp(10),dp(5),dp(10),dp(5))})
  content.addView(section)
  val stats=listOf(
   Triple("حجوزات اليوم",todays.size.toString(),Palette.gold),
   Triple("الساعات المتاحة",available.toString(),Palette.green),
   Triple("الفرق المسجلة",db.teams().size.toString(),Color.rgb(112,174,255)),
   Triple("البطولات",tournaments.size.toString(),Palette.fixed)
  )
  stats.chunked(2).forEach{pair->
   val row=LinearLayout(this).apply{orientation=0}
   pair.forEach{(label,value,color)->
    val tile=LinearLayout(this).apply{
     orientation=1;background=panel(17);setPadding(dp(13),dp(11),dp(13),dp(11))
     addView(View(this@MainActivity).apply{background=GradientDrawable().apply{cornerRadius=dp(3).toFloat();setColor(color)}},LinearLayout.LayoutParams(dp(27),dp(3)).apply{bottomMargin=dp(8)})
     addView(txt(value,25f,color,true).apply{gravity=Gravity.RIGHT})
     addView(txt(label,10.5f,Palette.muted,true).apply{gravity=Gravity.RIGHT})
    }
    row.addView(tile,LinearLayout.LayoutParams(0,dp(91),1f).apply{marginEnd=dp(5);marginStart=dp(5)})
   }
   content.addView(row,LinearLayout.LayoutParams(-1,-2).apply{topMargin=dp(8)})
  }

  gap(17)
  head("الوصول السريع","اختر القسم الذي تريد إدارته")
  val actions=listOf(
   Triple("جدول الحجوزات","المواعيد المتاحة والمحجوزة","bookings"),
   Triple("الحجوزات الثابتة","المواعيد الأسبوعية المتكررة","fixed"),
   Triple("البطولات","القرعة والنتائج والترتيب","tournaments"),
   Triple("الفرق واللاعبون","إدارة الفرق وقوائم اللاعبين","players")
  )
  actions.chunked(2).forEach{pair->
   val row=LinearLayout(this).apply{orientation=0}
   pair.forEachIndexed{index,item->
    val (title,sub,target)=item
    val tile=LinearLayout(this).apply{
     orientation=1;gravity=Gravity.CENTER_VERTICAL;background=panel(16);setPadding(dp(12),dp(11),dp(12),dp(11))
     addView(txt(if(target=="bookings")"▦" else if(target=="fixed")"◷" else if(target=="tournaments")"♜" else "♟",22f,if(index==0)Palette.purple else Palette.gold,true).apply{gravity=Gravity.RIGHT})
     addView(txt(title,13f,Palette.white,true).apply{gravity=Gravity.RIGHT})
     addView(txt(sub,9.5f,Palette.muted).apply{gravity=Gravity.RIGHT})
     setOnClickListener{page=target;showApp()}
    }
    row.addView(tile,LinearLayout.LayoutParams(0,dp(103),1f).apply{marginStart=dp(5);marginEnd=dp(5)})
   }
   content.addView(row,LinearLayout.LayoutParams(-1,-2).apply{topMargin=dp(8)})
  }

  gap(17)
  val todayHeader=LinearLayout(this).apply{orientation=0;gravity=Gravity.CENTER_VERTICAL}
  todayHeader.addView(txt("حجوزات اليوم",17f,Palette.white,true).apply{gravity=Gravity.RIGHT},LinearLayout.LayoutParams(0,-2,1f))
  todayHeader.addView(btn("عرض الكل  ←",{page="bookings";showApp()},false),LinearLayout.LayoutParams(dp(105),dp(40)))
  content.addView(todayHeader)
  if(todays.isEmpty()){
   val empty=LinearLayout(this).apply{
    orientation=1;gravity=Gravity.CENTER;background=panel(17);setPadding(dp(15),dp(18),dp(15),dp(18))
    addView(txt("لا توجد حجوزات لهذا اليوم",13f,Palette.white,true))
    addView(txt("ابدأ بإضافة موعد جديد للملعب",10.5f,Palette.muted))
    addView(btn("＋ إضافة حجز",{page="bookings";showApp()},true),LinearLayout.LayoutParams(dp(165),dp(44)).apply{topMargin=dp(10)})
   }
   content.addView(empty,LinearLayout.LayoutParams(-1,-2).apply{topMargin=dp(8)})
  }else todays.forEach{b->
   val color=if(b.recurring)Palette.fixed else Palette.red
   val row=LinearLayout(this).apply{
    orientation=0;gravity=Gravity.CENTER_VERTICAL;background=panel(15);setPadding(dp(12),dp(8),dp(12),dp(8))
    addView(View(this@MainActivity).apply{background=GradientDrawable().apply{cornerRadius=dp(3).toFloat();setColor(color)}},LinearLayout.LayoutParams(dp(4),dp(43)))
    val details=LinearLayout(this@MainActivity).apply{orientation=1}
    details.addView(txt(b.teams,13f,Palette.white,true).apply{gravity=Gravity.RIGHT})
    details.addView(txt(if(b.recurring)"حجز ثابت أسبوعياً" else "حجز عادي",10f,color).apply{gravity=Gravity.RIGHT})
    addView(details,LinearLayout.LayoutParams(0,-2,1f).apply{marginStart=dp(10)})
    addView(txt(hour(b.hour),12f,Palette.gold,true))
    setOnClickListener{bookingDetails(b)}
   }
   content.addView(row,LinearLayout.LayoutParams(-1,-2).apply{topMargin=dp(7)})
  }
 }'''
text = text[:home_start] + new_home + text[home_end:]

nav_start = text.index(' private fun nav():LinearLayout {')
nav_end = text.index(' private fun card(', nav_start)
new_nav = r''' private fun nav():LinearLayout {
  val n=LinearLayout(this).apply{
   orientation=0;gravity=Gravity.CENTER;background=GradientDrawable(GradientDrawable.Orientation.TL_BR,intArrayOf(Color.rgb(27,24,43),Color.rgb(13,14,25))).apply{cornerRadius=dp(21).toFloat();setStroke(dp(1),Color.rgb(62,55,87))}
   setPadding(dp(5),dp(5),dp(5),dp(5));elevation=dp(8).toFloat()
  }
  listOf(Triple("home","⌂","الرئيسية"),Triple("bookings","▦","الحجوزات"),Triple("tournaments","♜","البطولات"),Triple("more","⋯","المزيد")).forEach{(p,ico,label)->
   val active=page==p
   val item=LinearLayout(this).apply{
    orientation=1;gravity=Gravity.CENTER
    if(active)background=GradientDrawable(GradientDrawable.Orientation.TL_BR,intArrayOf(Color.rgb(93,48,135),Color.rgb(48,34,73))).apply{cornerRadius=dp(15).toFloat();setStroke(dp(1),Color.rgb(151,91,207))}
    addView(txt(ico,19f,if(active)Palette.gold else Palette.muted,true))
    addView(txt(label,9.5f,if(active)Palette.white else Palette.muted,true))
    isClickable=true;isFocusable=true
   }
   n.addView(item,LinearLayout.LayoutParams(0,-1,1f).apply{setMargins(dp(2),0,dp(2),0)})
   item.setOnClickListener{page=p;showApp()}
  }
  return n
 }
'''
text = text[:nav_start] + new_nav + text[nav_end:]
# Update dashboard-specific validation markers so future builds fail if the new design is omitted.
if 'ملخص الملعب' not in text or 'الوصول السريع' not in text or 'val available=' not in text:
    raise SystemExit('Dashboard redesign validation failed')

print('Source validation passed')

# Apply the approved button and navigation polish without replacing existing screens.
text = source.read_text(encoding='utf-8')
needle = 'import android.graphics.drawable.GradientDrawable'
text = text.replace(needle, needle + chr(10) + 'import android.graphics.drawable.RippleDrawable' + chr(10) + 'import android.content.res.ColorStateList')
old_btn = ' private fun btn(s:String,action:()->Unit,accent:Boolean=false)=txt(s,14f,Palette.white,true).apply{minHeight=dp(44);minimumHeight=dp(44);background=panel(14,accent);setOnClickListener{action()}}'
new_btn = ''' private fun btn(s:String,action:()->Unit,accent:Boolean=false)=txt(s,14f,Palette.white,true).apply{
  minHeight=dp(48);minimumHeight=dp(48);minWidth=dp(64)
  gravity=Gravity.CENTER;maxLines=2;ellipsize=android.text.TextUtils.TruncateAt.END
  setPadding(dp(12),dp(9),dp(12),dp(9));letterSpacing=0.015f
  background=if(accent) GradientDrawable(GradientDrawable.Orientation.TL_BR,intArrayOf(Color.rgb(142,55,244),Color.rgb(82,31,166))).apply{cornerRadius=dp(15).toFloat();setStroke(dp(1),Color.rgb(190,137,255))}
    else GradientDrawable(GradientDrawable.Orientation.TL_BR,intArrayOf(Color.rgb(37,34,57),Color.rgb(19,19,32))).apply{cornerRadius=dp(15).toFloat();setStroke(dp(1),Color.rgb(75,68,105))}
  foreground=RippleDrawable(ColorStateList.valueOf(Color.argb(55,255,255,255)),null,GradientDrawable().apply{cornerRadius=dp(15).toFloat();setColor(Color.WHITE)})
  elevation=dp(1).toFloat();isClickable=true;isFocusable=true
  setOnClickListener{action()}
 }'''
if old_btn not in text:
    raise SystemExit('Button helper did not match; refusing unsafe UI patch')
text = text.replace(old_btn, new_btn)
text = text.replace('root.addView(nav(),LinearLayout.LayoutParams(-1,dp(56)))', 'root.addView(nav(),LinearLayout.LayoutParams(-1,dp(64)))')
text = text.replace('val v=txt(t,10f,if(active)Palette.gold else Palette.muted,true)', 'val v=txt(t,10.5f,if(active)Palette.gold else Palette.muted,true).apply{minHeight=dp(48);setPadding(dp(3),dp(5),dp(3),dp(5));isClickable=true;isFocusable=true}')
source.write_text(text, encoding='utf-8')
