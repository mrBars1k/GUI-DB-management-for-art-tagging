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

def fill_parent_sim(event=None):  ## fill out the dropdown list;
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
## UPDATE TABLE;
art_to_tag = ttk.Combobox(ttaw, width=43, font=("Arial", 14))
art_to_tag.place(x=20, y=40)

def up_in_tag(event=None):
    att = art_to_tag.get()
    art_id = int(att.split("|")[0].strip())

    cur.execute(f"""SELECT t1.id, t2.tag, COUNT(*) AS "count"
            FROM main_tags t1
            JOIN tag_to_art t2 ON t1.ru = t2.tag
            JOIN arts t3 ON t2.art = t3.id
            GROUP BY t1.id, t2.tag
            HAVING MAX((t2.art = {art_id})::INT) = 1
            ORDER BY count DESC;
            """)
    data = cur.fetchall()

    for i in tree.get_children(): ## delete previous data;
        tree.delete(i)

    for j in data: ## fill with new ones;
        tree.insert("", "end", values=j)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## TAG TO ART;
def adta(event=None):
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
    in_tag_art.delete(0, END)

add_tag_to_art_btn = Button(ttaw, text="Add", width=5, height=3, font=("Arial", 14), command=adta)
add_tag_to_art_btn.place(x=540, y=38)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## DELETE TAG FROM ART;
def delete_from_art():
    att = art_to_tag.get()
    art_id = int(att.split("|")[0].strip())

    item = tree.selection()[0] # selected cell in table;
    id_text = tree.item(item, "values")[0] # id from table;
    cur.execute(f"""DELETE FROM tag_to_art
                    USING main_tags
                    WHERE tag_to_art.tag = main_tags.ru
                    AND main_tags.id = {id_text}
                    AND tag_to_art.art = {art_id}""")
    adb.commit()
    up_in_tag()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## CONTEXT MENU;
def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)

context_menu = Menu(ttaw, tearoff=0)
context_menu.add_command(label="Удалить", command=delete_from_art)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## FIND AUTHORS;
def find_sim_au(author):
    cur.execute(f"""SELECT ru FROM main_tags 
    WHERE ru LIKE '%{author}%'
    AND type = 'author'
    ORDER BY date DESC""")
    all_authors = cur.fetchall()
    return all_authors

def find_artist(event=None):  ## fill out the dropdown list;
    au_to_find = author_name.get()  ## entered data in the add parent tag field;
    similar_au = find_sim_au(au_to_find)  ## found all similar artists to those entered by the user;
    ## ['author', 'artist', 'mrBars1k']

    author_name["values"] = similar_au  ## fill out the dropdown list;
    author_name.event_generate('<Down>')  ## expand the list;

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ADD ART;
def add_art():
    a_name = author_name.get().strip()
    a_url = art_url.get().strip()
    o_link = orig_link.get().strip()

    cur.execute(f"""INSERT INTO arts (artist, url, original_link) VALUES (
                '{a_name}', '{a_url}', '{o_link}'
                );""")
    adb.commit()

    author_name.delete(0, END)
    art_url.delete(0, END)
    orig_link.delete(0, END)
    fill_parent_sim()
    find_arts()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## AUTHORS SIDE;
author_name = ttk.Combobox(ttaw, width=30, font=("Arial", 14))
art_url = Entry(ttaw, width=40, borderwidth=3, font=("Arial", 18))
orig_link = Entry(ttaw, width=40, borderwidth=3, font=("Arial", 18))
add_art_btn = Button(ttaw, text="Add art", width=32, font=("Arial", 14), command=add_art)

author_name.place(x=700, y=50)
art_url.place(x=700, y=100)
orig_link.place(x=700, y=150)
add_art_btn.place(x=700, y=210)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## REACTIONS;
in_tag_art.bind("<Return>", fill_parent_sim)
in_tag_art.bind("<Shift_R>", adta)
art_to_tag.bind("<<ComboboxSelected>>", up_in_tag)
tree.bind("<Button-3>", show_context_menu)
author_name.bind("<Return>", find_artist)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
fill_parent_sim()
find_arts()
find_artist()

ttaw.mainloop() # START;
cur.close()
adb.close()