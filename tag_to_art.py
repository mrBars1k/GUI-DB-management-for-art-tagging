from tkinter import *
from tkinter import ttk
import datetime
import psycopg2
from psycopg2 import sql
from token import *

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
ttaw = Tk() ## main window;
ttaw.title("ADD NEW ") ## headline;
ttaw.geometry("1920x1080") ## resolution;
ttaw.wm_minsize(1280, 720)  ## min width and hight;
ttaw.wm_maxsize(1920, 1080)  ## max width and hight;

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
adb = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port)

cur = adb.cursor()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## TABLE WITH TAGS FROM DATABASE;
tree = ttk.Treeview(ttaw, columns=("ID", "Russian", "count"))
tree.column("#0", width=0, anchor="center")
tree.column("#1", width=5, anchor="center")
tree.column("#2", width=300, anchor="center")
tree.column("#3", width=30, anchor="center")

## ## ## ##

tree.heading("#1", text="ID")
tree.heading("#2", text="Russian")
tree.heading("#3", text="Сount")

tree.place(x=20, y=160, height=800, width=500)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## FILL TAGS;
def get_similar_tags(tag_to_find):  ## find all tags similar in name;
    cur.execute("""
        SELECT mt.ru, COUNT(tta.art) AS count
        FROM main_tags AS mt
        LEFT JOIN tag_to_art AS tta ON mt.ru = tta.tag
        WHERE 
        mt.ru LIKE %s 
        OR mt.eng LIKE %s 
        OR mt.alias1 LIKE %s 
        OR mt.alias2 LIKE %s 
        OR mt.alias3 LIKE %s 
        OR mt.alias4 LIKE %s
        GROUP BY mt.id
        ORDER BY count DESC, date DESC""",
                ('%' + tag_to_find + '%', '%' + tag_to_find + '%', '%' + tag_to_find + '%', '%' + tag_to_find + '%',
                 '%' + tag_to_find + '%', '%' + tag_to_find + '%'))
    return [row[0] for row in cur.fetchall()]  ## sorted by usage and date;

def fill_parent_sim(event):  ## fill out the dropdown list;
    tag_to_find = in_tag_art.get()  ## entered data in the add parent tag field;
    similar_tags = get_similar_tags(tag_to_find)  ## found all similar tags (ru version) to those entered by the user;
    ## ['рукава', 'длинные рукава', 'короткие рукава']

    in_tag_art["values"] = similar_tags  ## fill out the dropdown list;
    in_tag_art.event_generate('<Down>')  ## expand the list;

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## FIND ARTS;
def find_arts():
    cur.execute("SELECT id, artist, date FROM arts ORDER BY id DESC")
    arts = cur.fetchall()
    formatted_arts = []
    n_a = 0
    for i in arts:
        n_a += 1
        formatted_date = i[2].strftime("%d.%m.%Y-%H:%M")
        formatted_arts.append((i[0], "|", i[1], formatted_date))
        art_to_tag["values"] = formatted_arts

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## INPUT TAG TO ART;
in_tag_art = ttk.Combobox(ttaw, width=43, font=("Arial", 14))
in_tag_art.place(x=20, y=90)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ART TO TAG;
art_to_tag = ttk.Combobox(ttaw, width=43, font=("Arial", 14))
art_to_tag.place(x=20, y=40)

def up_in_tag(event):
    att = art_to_tag.get()
    tag_id = int(att.split("|")[0].strip())

    cur.execute(f"""SELECT main_tags.id, tag_to_art.tag, COUNT(tag_to_art.art) AS count
                FROM main_tags
                JOIN tag_to_art ON main_tags.ru = tag_to_art.tag
                WHERE tag_to_art.art = {tag_id}
                GROUP BY main_tags.id, tag_to_art.tag
                ORDER BY count, date DESC
                """)
    data = cur.fetchall()

    for i in tree.get_children(): ## delete previous data;
        tree.delete(i)

    for j in data: ## fill with new ones;
        tree.insert("", "end", values=j)

def adta(event):
    ita = in_tag_art.get()
    att = art_to_tag.get()
    tag_id = int(att.split("|")[0].strip())
    try:
        cur.execute(f"""INSERT INTO tag_to_art (tag, art) VALUES ('{ita}', {tag_id});""")
        adb.commit()
        print(f"Тег <{ita}> успешно добавлен к арту <{att}>.")
    except:
        adb.rollback()
        print(f"Не удалось добавить тег <{ita}> к арту <{att}>!")
    up_in_tag()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## REACTIONS;
in_tag_art.bind("<Return>", fill_parent_sim)
in_tag_art.bind("<App>", adta)
art_to_tag.bind("<<ComboboxSelected>>", up_in_tag)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
fill_parent_sim("")
find_arts()

ttaw.mainloop() # START;
cur.close()
adb.close()