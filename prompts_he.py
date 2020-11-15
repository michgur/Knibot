from typing import List, Union

import telegram

greet_msg = '''שלום, אני קניבוט, בוט הקניות.🤖
אני עוזר לנהל רשימות קניות משותפות בין כמה משתתפים 📝.
'''
send_cmd = 'שלח'
send_msg = 'הנה הרשימה:\n'
write_cmd = 'רשום'
instead_cmd = 'במקום'
write_msg = 'אני רושם 📝. בסיום הרשימה נא לשלוח "זהו"'
remove_msg = 'אני מוחק. בסיום הרשימה נא לשלוח "זהו"'
finish_cmd = 'זהו'
finish_write_msg = 'אחלה, רשמתי את הפריטים שביקשת'
failed_msg = 'אופס חלה אצלי תקלה'
bought_cmd = 'קניתי'
bought_msg = 'סגור, איפסתי את הרשימה'
remove_cmd = 'בטל'
finish_remove_msg = 'הסרתי את הפריטים'
debug_cmd = 'דבג'
list_cmd = 'רשימה'
new_cmd = 'חדשה'
already_exists_err = 'כבר יש רשימה בשם "%s"...'
not_exists_err = 'אין לך רשימה בשם "%s"...'
list_msg = 'מעכשיו אני עורך את הרשימה "%s"'
new_msg = 'יצרתי רשימה חדשה בשם "%s"'
new_list_msg = 'יצרתי רשימה חדשה בשם "%s" ומעכשיו אני עורך אותה'
no_item_err = 'סליחה, לא הצלחתי להבין למה התכוונת'
no_working_list_err = 'לא פתחת אף רשימה...'
default_working_state_err = 'לא הבנתי מה לעשות עם מה שכתבת...'
empty_list_err = 'הרשימה ריקה...'
no_lists_err = 'אין לך גישה לאף רשימה...'
mem = 'מ'
vav = 'ו'
everything = 'הכול'
bought_everything = 'קנה כל מה שביקשת'
except_for = 'חוץ מ'
existing_item_err = 'חוץ מ%s שכבר יש ברשימה'
non_existing_item_err = 'חוץ מ%s, פריט שלא הופיע ברשימה'
non_existing_items_err = 'חוץ מ%s, פריטים שלא הופיעו ברשימה'
share_msg = 'נא לשלוח את אנשי הקשר שברצונך לשתף איתם את הרשימה. בסיום נא לשלוח "זהו"'
finish_share_msg = 'שיתפתי את הרשימה עם המשתמשים'
set_admins_msg = 'הפכתי את המשתמשים למנהלים'
unrecognized_msg_err = 'סליחה, לא הבנתי את ההודעה שלך. לקבלת עזרה ניתן לשלוח "עזרה"'
exception_err = 'סליחה, חלה תקלה:\n'
not_admin_err = 'סליחה, לא ניתן לבצע את הפעולה ללא הרשאות מנהל. ניתן לבקש הרשאות מאחד המנהלים של הרשימה'
send_btn = 'שליחת הרשימה הנוכחית'
list_btn = 'עריכת רשימה אחרת'
lists_btn = 'הצגת כלל הרשימות'
new_list_btn = 'יצירת רשימה חדשה'
write_btn = 'הוספת פריטים לרשימה'
remove_btn = 'הסרת פריטים מהרשימה'
remove_all_btn = 'הסרת כל הפריטים מהרשימה'
bought_btn = 'קניתי הכול'
bought_but_btn = 'קניתי הכול חוץ מ-'


def list_to_string(l: List[str]) -> str:
    if len(l) == 0:
        return ''
    if len(l) == 1:
        return l[0]
    return ', '.join(l[:-1]) + ' ' + vav + l[-1]


def everything_but(l: List[str], everything_str: str = everything) -> str:
    if len(l) == 0:
        return everything_str
    return everything_str + ' ' + except_for + list_to_string(l)


def mention(user: Union[telegram.User, telegram.Chat], text=None):
    return '<a href="tg://user?id=%i">%s</a>' % (user.id, user.first_name if text is None else text)
