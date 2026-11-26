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
