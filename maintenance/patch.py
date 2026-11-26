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
