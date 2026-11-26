p='project/app/src/main/java/com/hijoozati/app/MainActivity.kt'
s=open(p,encoding='utf-8').read()
# ScrollView inherits FrameLayout; use the public ViewGroup.LayoutParams type.
s=s.replace('android.view.ViewGroup.LayoutParams(-1,-2)','android.view.ViewGroup.LayoutParams(-1,-2)')
# Restore a full-width, naturally sized screen with comfortable internal spacing.
old=' private fun showApp(){root=LinearLayout(this).apply{orientation=1;layoutDirection=View.LAYOUT_DIRECTION_RTL;setBackgroundColor(Palette.bg);setPadding(dp(11),dp(5),dp(11),dp(5))};val sc=ScrollView(this).apply{isFillViewport=true};content=LinearLayout(this).apply{orientation=1};sc.addView(content);root.addView(sc,LinearLayout.LayoutParams(-1,0,1f));'
new=' private fun showApp(){root=LinearLayout(this).apply{orientation=1;layoutDirection=View.LAYOUT_DIRECTION_RTL;setBackgroundColor(Palette.bg);setPadding(0,0,0,0)};val sc=ScrollView(this).apply{isFillViewport=true;clipToPadding=false};content=LinearLayout(this).apply{orientation=1;setPadding(dp(14),dp(8),dp(14),dp(8))};sc.addView(content,android.view.ViewGroup.LayoutParams(-1,-2));root.addView(sc,LinearLayout.LayoutParams(-1,0,1f));'
if old in s: s=s.replace(old,new,1)
assert 'setPadding(dp(14),dp(8),dp(14),dp(8))' in s
# Show the complete one-hour booking range, including the next-hour end time.
old=' private fun hour(h:Int)="${if(h%12==0)12 else h%12}:00 ${if(h<12)"ص" else "م"}"'
new=old+'\n private fun hourRange(h:Int)="${hour(h)} – ${hour((h+1)%24)}"'
if 'private fun hourRange(h:Int)' not in s:
    assert old in s, 'hour formatter not found'
    s=s.replace(old,new,1)
old='line.addView(txt(hour(h),15f,Palette.white,true),LinearLayout.LayoutParams(dp(91),dp(43)))'
new='line.addView(txt(hourRange(h),14f,Palette.white,true),LinearLayout.LayoutParams(dp(116),dp(43)))'
if old in s: s=s.replace(old,new,1)
# Deleting a tournament also removes its linked match bookings.
old='db.writableDatabase.delete("fixtures","tournament_id=?",arrayOf(id.toString()));db.writableDatabase.delete("tournament_teams","tournament_id=?",arrayOf(id.toString()));'
new='db.writableDatabase.delete("bookings","tournament_id=?",arrayOf(id.toString()));db.writableDatabase.delete("fixtures","tournament_id=?",arrayOf(id.toString()));db.writableDatabase.delete("tournament_teams","tournament_id=?",arrayOf(id.toString()));'
if old in s: s=s.replace(old,new,1)
# Display complete one-hour ranges consistently throughout the app.
replacements={
 'hour(b.hour)}  •  ${if(b.recurring)':'hourRange(b.hour)}  •  ${if(b.recurring)',
 '${days[b.weekday]} • ${hour(b.hour)}':'${days[b.weekday]} • ${hourRange(b.hour)}',
 '${dateLabel(b.date)}\\n${hour(b.hour)}\\nالمدة: ساعة واحدة':'${dateLabel(b.date)}\\n${hourRange(b.hour)}\\nالمدة: ساعة واحدة',
 '${dateLabel(it.date)} ${hour(it.hour)}':'${dateLabel(it.date)} ${hourRange(it.hour)}'
}
for old,new in replacements.items():
 if old in s: s=s.replace(old,new)
# Keep tournament-linked booking rows in sync if an individual match booking is deleted.
old='fun deleteBooking(id:Long){writableDatabase.delete("bookings","id=?",arrayOf(id.toString()))}'
new='fun deleteBooking(id:Long){writableDatabase.delete("bookings","id=?",arrayOf(id.toString()));writableDatabase.update("fixtures",ContentValues().apply{put("booking_id",0);put("match_date","")},"booking_id=?",arrayOf(id.toString()))}'
if old in s: s=s.replace(old,new,1)
# Ensure the dedicated tournament booking view only lists live linked bookings.
old='val fs=db.fixtures(id).filter{it.bookingId>0}'
new='val fs=db.fixtures(id).filter{it.bookingId>0&&db.allBookings().any{b->b.id==it.bookingId}}'
if old in s: s=s.replace(old,new,1)
# Expose the monthly calendar from the bookings page.
old='  gap(10);weekPicker();gap(8)'
new='  gap(10);weekPicker();content.addView(btn("عرض التقويم الشهري",{monthPicker()},false),LinearLayout.LayoutParams(-1,dp(40)).apply{topMargin=dp(6)});gap(8)'
if old in s: s=s.replace(old,new,1)
# Give each tournament a dedicated list of its scheduled match bookings.
old='val opts=arrayOf("إضافة فريق مشارك","سحب القرعة وإنشاء المباريات","النتائج وجدول المباريات","إحصائيات البطولة","حذف البطولة");'
new='val opts=arrayOf("إضافة فريق مشارك","سحب القرعة وإنشاء المباريات","النتائج وجدول المباريات","إحصائيات البطولة","حجوزات البطولة","حذف البطولة");'
if old in s: s=s.replace(old,new,1)
old='3->showTournamentStats(id);4->AlertDialog.Builder(this).setMessage("حذف البطولة؟")'
new='3->showTournamentStats(id);4->showTournamentBookings(id);5->AlertDialog.Builder(this).setMessage("حذف البطولة؟")'
if old in s: s=s.replace(old,new,1)
# Implement a separate tournament booking list, linked back to match actions.
anchor=' private fun showTournamentStats(id:Long){'
method=''' private fun showTournamentBookings(id:Long){
val fs=db.fixtures(id).filter{it.bookingId>0}
if(fs.isEmpty()){Toast.makeText(this,"لا توجد حجوزات مباريات لهذه البطولة",Toast.LENGTH_LONG).show();return}
val lines=fs.map{"${it.home} × ${it.away} • ${dateLabel(it.date)} • ${hourRange(it.hour)}"}
AlertDialog.Builder(this).setTitle("حجوزات البطولة").setItems(lines.toTypedArray()){_,i->fixtureOptions(fs[i])}.setNegativeButton("رجوع",null).show()
         }
         '''
if 'private fun showTournamentBookings(id:Long)' not in s:
    assert anchor in s, 'tournament stats anchor missing'
    s=s.replace(anchor,method+anchor,1)
# Keep the monthly calendar visible when navigating between months.
old='monthCursor.add(Calendar.MONTH,-1);showApp()}'
new='monthCursor.add(Calendar.MONTH,-1);showApp();monthPicker()}'
if old in s: s=s.replace(old,new,1)
old='monthCursor.add(Calendar.MONTH,1);showApp()}'
new='monthCursor.add(Calendar.MONTH,1);showApp();monthPicker()}'
if old in s: s=s.replace(old,new,1)
# Regenerating a tournament draw must remove its old linked bookings too.
old='db.writableDatabase.delete("fixtures","tournament_id=?",arrayOf(id.toString()));createDraw(id,teams)'
new='db.writableDatabase.delete("bookings","tournament_id=?",arrayOf(id.toString()));db.writableDatabase.delete("fixtures","tournament_id=?",arrayOf(id.toString()));createDraw(id,teams)'
if old in s: s=s.replace(old,new,1)
# Generate a full round-robin group stage for the groups tournament type.
old='}else{val pool=teams.map{it.name}.toMutableList();if(pool.size%2==1)pool.add("تأهل تلقائي");for(i in 0 until pool.size/2){if(pool[i]!="تأهل تلقائي"&&pool[pool.lastIndex-i]!="تأهل تلقائي")db.addFixture(id,pool[i],pool[pool.lastIndex-i],"الدور الأول")}};showFixtures(id)}'
new='}else if(t.type=="مجموعات ثم خروج المغلوب"){for(i in teams.indices)for(j in i+1 until teams.size)db.addFixture(id,teams[i].name,teams[j].name,"دور المجموعات")}else{val pool=teams.map{it.name}.toMutableList();if(pool.size%2==1)pool.add("تأهل تلقائي");for(i in 0 until pool.size/2){if(pool[i]!="تأهل تلقائي"&&pool[pool.lastIndex-i]!="تأهل تلقائي")db.addFixture(id,pool[i],pool[pool.lastIndex-i],"الدور الأول")}};showFixtures(id)}'
if old in s: s=s.replace(old,new,1)
assert 'private fun showTournamentBookings(id:Long)' in s
assert 'عرض التقويم الشهري' in s
# Calculate a real league table from recorded scores instead of showing only a score list.
start=s.find(' private fun showTournamentStats(id:Long)')
end=s.find('\n private fun playersPage()',start)
assert start>=0 and end>start, 'tournament statistics function not found'
replacement=''' private fun showTournamentStats(id:Long){
val fixtures=db.fixtures(id).filter{it.homeScore>=0&&it.awayScore>=0}
val table=linkedMapOf<String,MutableList<Int>>()
db.tournamentTeams(id).forEach{table[it.name]=mutableListOf(0,0,0,0,0,0,0)}
fixtures.forEach{f->
 val h=table.getOrPut(f.home){mutableListOf(0,0,0,0,0,0,0)}
 val a=table.getOrPut(f.away){mutableListOf(0,0,0,0,0,0,0)}
 h[0]++;a[0]++;h[4]+=f.homeScore;h[5]+=f.awayScore;a[4]+=f.awayScore;a[5]+=f.homeScore
 when{f.homeScore>f.awayScore->{h[1]++;a[3]++;h[6]+=3};f.homeScore<f.awayScore->{a[1]++;h[3]++;a[6]+=3};else->{h[2]++;a[2]++;h[6]++;a[6]++}}
}
val lines=table.entries.sortedWith(compareByDescending<Map.Entry<String,MutableList<Int>>>{it.value[6]}.thenByDescending{it.value[4]-it.value[5]}.thenByDescending{it.value[4]}).mapIndexed{index,e->
 val v=e.value
 "${index+1}. ${e.key} • لعب ${v[0]} • فاز ${v[1]} • تعادل ${v[2]} • خسر ${v[3]} • له ${v[4]} • عليه ${v[5]} • نقاط ${v[6]}"
}
AlertDialog.Builder(this).setTitle("ترتيب البطولة").setMessage(lines.joinToString("\\n").ifBlank{"لا توجد نتائج مسجلة بعد"}).setPositiveButton("حسناً",null).show()
         }'''
s=s[:start]+replacement+s[end:]
open(p,'w',encoding='utf-8').write(s)
