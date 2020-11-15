from typing import List, Union

import telegram


def list_to_string(l: List[str]) -> str:
    if len(l) == 0:
        return ''
    if len(l) == 1:
        return l[0]
    return ', '.join(l[:-1]) + ' ' + vav + l[-1]


def everything_but(l: List[str], everything_str: str = 'הכול') -> str:
    if len(l) == 0:
        return everything_str
    return everything_str + ' ' + except_for + list_to_string(l)


def mention(user: Union[telegram.User, telegram.Chat], text=None):
    return '<a href="tg://user?id=%i">%s</a>' % (user.id, user.first_name if text is None else text)


def wrap_in_code_tag(text: str) -> str:
    return '`<u>%s</u>`' % text


greet_msg = 'שלום, לקבלת עזרה ניתן ללחוץ על אחד מהכפתורים ששלחתי או לשלוח לי "עזרה"\n'
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
no_users_err = 'אין משתתפים ברשימה חוץ ממך'
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
no_name_err = 'לא כתבת את שם הרשימה'
send_btn = 'הצגת הרשימה הנוכחית'
list_btn = 'עריכת רשימה אחרת'
lists_btn = 'הצגת כלל הרשימות'
users_btn = 'הצגת המשתתפים ברשימה הנוכחית'
new_list_btn = 'יצירת רשימה חדשה'
write_btn = 'הוספת פריטים'
remove_btn = 'הסרת פריטים'
remove_all_btn = 'הסרת כל הפריטים'
bought_btn = 'קניתי הכול'
bought_but_btn = 'קניתי הכול חוץ מ-'
share_btn = 'הוספת משתתפים לרשימה'
help_btn = 'עזרה'
help_msg = 'באיזה נושא ברצונך לקבל עזרה?'
new_list_help = 'ליצירת רשימה חדשה:\n<code>רשימה חדשה &lt;שם הרשימה&gt;</code>'
list_help = 'לעריכת רשימה קיימת:\n<code>רשימה &lt;שם הרשימה&gt;</code>'
lists_help = 'להצגת כלל הרשימות שיש לך גישה אליהן:\n<code>רשימות</code>'
share_help = 'לשיתוף הרשימה הנוכחית עם משתתפים נוספים:\n<code>שתף</code>\nלאחר מכן, ניתן לצרף בהודעות את אנשי הקשר ' \
             'שברצונך לשתף.\nלאחר שליחת כלל אנשי הקשר יש לשלוח "זהו" '
users_help = 'להצגת כלל המשתתפים ברשימה הנוכחית:\n<code>משתתפים</code>'
write_help = 'ישנן שתי דרכים להוספת פריטים לרשימה:\n• ' + \
             wrap_in_code_tag('תרשום') + \
             ', ולאחר מכן לשלוח את הפריטים בהודעות נפרדות ובסיום לשלוח "זהו"\n• ' + \
             wrap_in_code_tag('תרשום &lt;פריט אחד או יותר&gt;') + \
             ', עם פסיק בין כל פריט ופריט\nניתן להחליף פריט קיים בפריט אחר בהודעה אחת, לדוגמה: ' + \
             wrap_in_code_tag('תרשום מלפפון במקום עגבניה') + \
             '\nהמשתתפים האחרים ברשימה יוכלו לצפות בפריטים ששלחת, וברגע שמישהו מהם יקנה את הפריטים אני אעדכן אותך'
remove_help = 'ישנן שתי דרכים למחיקת פריטים מהרשימה:\n• %s, ולאחר מכן לשלוח את הפריטים בהודעות נפרדות ' \
              'ובסיום לשלוח "זהו"\n• %s, עם פסיק בין כל פריט ופריט\nניתן ' \
              'למחוק את כל הפריטים בהודעה אחת באופן הבא:%s\nניתן למחוק את כל הפריטים חוץ מכמה ' \
              'פריטים מסוימים באופן הבא:\n%s ' % (
                  wrap_in_code_tag('תמחק'),
                  wrap_in_code_tag('תמחק &lt;פריט אחד או יותר&gt;'),
                  wrap_in_code_tag('תמחק הכול'),
                  wrap_in_code_tag('תמחק הכול חוץ מ&lt;פריט אחד או יותר&gt;')
              )
bought_help = 'לעדכון על ביצוע קניה:\n%s, עם פסיק בין כל פריט ופריט\nניתן ' \
              'לעדכן על קניה של כל הפריטים בהודעה אחת באופן הבא:\n%s או פשוט ' \
              '%s\nניתן לעדכן על קניה של כל הפריטים חוץ מכמה פריטים מסוימים באופן הבא:\n%s ' \
              '\nלאחר שליחת ההודעה הרשימה תתעדכן ושאר המשתמשים יקבלו הודעה ' \
              'על הקניה שביצעת ' % (
                  wrap_in_code_tag('קניתי &lt;פריט אחד או יותר&gt;'),
                  wrap_in_code_tag('קניתי הכול'),
                  wrap_in_code_tag('קניתי'),
                  wrap_in_code_tag('קניתי הכול חוץ מ&lt;פריט אחד או יותר&gt;')
              )
