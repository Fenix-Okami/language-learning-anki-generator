

wanikani_radicals="""
create view wanikani_radicals as(

select
"id",
"level",
"slug" as "meaning",
coalesce("characters",'N/A') as "radical",
string_to_array(trim('[]' from meanings), ',') as meanings,
"meaning_mnemonic"

from public.wanikani_subjects

where object='radical'
order by "level" asc,"id" asc)
"""

wanikani_kanji="""
create view wanikani_kanji as(

select
"id",
"level",
"slug" as "kanji",

"primary_reading",
string_to_array(trim('[]' from meanings), ',') as meanings,
string_to_array(trim('[]' from "onyomi_readings"), ',') as "onyomi_readings",
string_to_array(trim('[]' from "kunyomi_readings"), ',') as "kunyomi_readings",

"meaning_mnemonic",
"reading_mnemonic"

from public.wanikani_subjects

where object='kanji'
order by "level" asc,"id" asc)
"""

wanikani_vocab="""
create view wanikani_vocab as(

select
"id",
"level",
"slug" as "word",

string_to_array(trim('[]' from readings), ',') as readings,
string_to_array(trim('[]' from meanings), ',') as meanings,
string_to_array(trim('[]' from auxiliary_meanings), ',') as auxiliary_meanings,

"meaning_mnemonic",
"reading_mnemonic"

from public.wanikani_subjects

where object='vocabulary'
order by "level" asc,"id" asc)
"""

views=[wanikani_radicals, wanikani_kanji, wanikani_vocab]