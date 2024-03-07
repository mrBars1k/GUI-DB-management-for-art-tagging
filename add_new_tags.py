from tkinter import *
from tkinter import ttk
import datetime
import psycopg2
from psycopg2 import sql
from token import *
import re

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

adb = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port)

cur = adb.cursor()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

mainw = Tk() ## main window;
mainw.title("ADD NEW ") ## headline;
mainw.geometry("1920x1080") ## resolution;
mainw.wm_minsize(1280, 720)  ## min width and hight;
mainw.wm_maxsize(1920, 1080)  ## max width and hight;

## WINDOWS;
tab_control = ttk.Notebook(mainw)
add_tag = ttk.Frame(tab_control) ## add tags window;
# insert_tag = ttk.Frame(tab_control)

tab_control.add(add_tag, text="Add tags")
# tab_control.add(insert_tag, text="Link tags")
tab_control.pack(expand=1, fill='both')

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## MOVE BETWEEN INPUT FIELDS USING THE KEYBOARD ARROWS;
def focus_next(event):
    current_widget = event.widget
    if current_widget == ru_entry:
        eng_entry.focus_set()
    elif current_widget == eng_entry:
        alias1_entry.focus_set()
    elif current_widget == alias1_entry:
        alias2_entry.focus_set()
    elif current_widget == alias2_entry:
        alias3_entry.focus_set()
    elif current_widget == alias3_entry:
        alias4_entry.focus_set()

def focus_previous(event):
    current_widget = event.widget
    if current_widget == alias4_entry:
        alias3_entry.focus_set()
    elif current_widget == alias3_entry:
        alias2_entry.focus_set()
    elif current_widget == alias2_entry:
        alias1_entry.focus_set()
    elif current_widget == alias1_entry:
        eng_entry.focus_set()
    elif current_widget == eng_entry:
        ru_entry.focus_set()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## RESPONSE TO PRESSING ENTER IN DIFFERENT INPUT FIELDS;
def handle_enter(event):
    current_widget = event.widget ## define active widget;

    if current_widget == ru_entry:
        eng_entry.focus_set()
    elif current_widget == eng_entry:
        alias1_entry.focus_set()
    elif current_widget == alias1_entry:
        alias2_entry.focus_set()
    elif current_widget == alias2_entry:
        alias3_entry.focus_set()
    elif current_widget == alias3_entry:
        alias4_entry.focus_set()
    elif current_widget == alias4_entry:
        send_to_table() ## if the last input field is selected, then by pressing enter send the result to the database;
    elif current_widget == search_entry:
        search_go() ## if the search input field is selected, then by pressing enter perform the search;

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## CLEARING INPUT FIELDS AFTER SUBMITTING;
def clear_fields():
    ru_entry.delete(0, END)
    eng_entry.delete(0, END)
    alias1_entry.delete(0, END)
    alias2_entry.delete(0, END)
    alias3_entry.delete(0, END)
    alias4_entry.delete(0, END)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ADDING A TAG TO THE DATABASE;
def send_to_table():
    try: ## get all the data entered in the fields;
        ru_text = ru_entry.get()
        eng_text = eng_entry.get()
        alias1_text = alias1_entry.get()
        alias2_text = alias2_entry.get()
        alias3_text = alias3_entry.get()
        alias4_text = alias4_entry.get()
        type_text = type_selected_value.get()
        y = [ru_text.strip(), eng_text.strip(), alias1_text.strip(), alias2_text.strip(), alias3_text.strip(), alias4_text.strip(), type_text.strip()]
        y = [i.lower() for i in y]  ## make all entered data in lower case;
        x = [i if i.strip() != "" else None for i in y]  ## checks for an empty string and, if empty, returns None;

        cur.execute("""INSERT INTO main_tags (ru, eng, alias1, alias2, alias3, alias4, type)
        VALUES (%s, %s, %s, %s, %s, %s, %s)""", (x[0], x[1], x[2], x[3], x[4], x[5], x[6]))
        adb.commit()

        clear_fields()
        ru_entry.focus_set() ## return focus to the first input field;
        update_table() ## update the table with new tags;
        print("The tag was successfully added to the database!")

    except:
        adb.rollback() ## canceling a failed transaction;
        update_table()
        print("ERROR 0001: tag adding error")

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## INACCURATE SEARCH OF TAGS FROM THE ENTIRE DATABASE;
def search_go():
    search_e = search_entry.get() ## entered data in the search field;
    type_t = spinbox_type.get()

    if search_e == "": ## if the field is empty, then update the table to its original form;
        update_table()
    else:
        if type_t == 'all': ## checking the search tag type;
            cur.execute(f"""
                        SELECT mt.id, mt.ru, mt.eng, mt.alias1, mt.alias2, mt.alias3, mt.alias4, mt.type,
                        COUNT(tta.art) AS count
                        FROM main_tags as mt
                        LEFT JOIN tag_to_art AS tta ON mt.ru = tta.tag
                        WHERE
                        ru LIKE '%{search_e}%' 
                        OR eng LIKE '%{search_e}%' 
                        OR alias1 LIKE '%{search_e}%' 
                        OR alias2 LIKE '%{search_e}%' 
                        OR alias3 LIKE '%{search_e}%' 
                        OR alias4 LIKE '%{search_e}%'
                        GROUP BY mt.id
                        ORDER BY count DESC, date DESC     
            """)
        else:
            cur.execute(f"""
                        SELECT mt.id, mt.ru, mt.eng, mt.alias1, mt.alias2, mt.alias3, mt.alias4, mt.type,
                        COUNT(tta.art) AS count
                        FROM main_tags as mt
                        LEFT JOIN tag_to_art AS tta ON mt.ru = tta.tag
                        WHERE type = '{type_t}' AND
                        (ru LIKE '%{search_e}%' 
                        OR eng LIKE '%{search_e}%' 
                        OR alias1 LIKE '%{search_e}%' 
                        OR alias2 LIKE '%{search_e}%' 
                        OR alias3 LIKE '%{search_e}%' 
                        OR alias4 LIKE '%{search_e}%')
                        GROUP BY mt.id
                        ORDER BY count DESC, date DESC     
            """)

        data = cur.fetchall() ## [(id, 'ru_name', 'en_name', 'al1', 'al2', 'al3', 'al4', 'tag type', count), (. . .))]

        for i in tree.get_children(): ## delete previous data;
            tree.delete(i)

        for j in data: ## fill with new ones;
            tree.insert("", "end", values=j)
        global count_tags ## global visibility to show outside the function the count of tags;

        count_tags.place_forget() ## remove old calculation;
        count_tags = Label(add_tag, text=f'Total tags: {len(data)}', font=("Arial", 18))
        count_tags.place(x=500, y=10)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

count_tags = Label(add_tag, text=f'Total tags:', font=("Arial", 18))
count_tags.place(x=500, y=10) ## total tags by categories;

search = Label(add_tag, text=f'Search:', font=("Arial", 18))
search.place(x=1200, y=10)

search_entry = Entry(add_tag, width=30, borderwidth=3, font=("Arial", 18))
search_entry.place(x=1300, y=10)

search_btn = Button(add_tag, width=16, height=2, text="OK", command=search_go)
search_btn.place(x=1740, y=6)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## THE VERY TOP PART OF THE PROGRAM;
def update_table():
    tree.place_forget() ## delete old table;
    tree.place(x=500, y=50, height=780, width=1210)
    find_type = spinbox_type.get()

    all_types = ['other', 'unknown', 'copyright', 'author', 'object', 'description', 'character']

    params = [find_type if t == find_type else '' for t in all_types] ## ['', '', '', '', '', '', ''] or ['', '', '', '', '', 'description', ''] etc
    if find_type == 'all': ## find tags of all categories if <all> is specified;
        query = """SELECT mt.id, mt.ru, mt.eng, mt.alias1, mt.alias2, mt.alias3, mt.alias4, mt.type,
            COUNT(tta.art) AS count
            FROM main_tags AS mt
            LEFT JOIN tag_to_art AS tta ON mt.ru = tta.tag
            GROUP BY mt.id
            ORDER BY count DESC, date DESC"""
        cur.execute(query)

    else: ## find tags by specified category;
        query = f"""SELECT mt.id, mt.ru, mt.eng, mt.alias1, mt.alias2, mt.alias3, mt.alias4, mt.type,
            COUNT(tta.art) AS count
            FROM main_tags AS mt
            LEFT JOIN tag_to_art AS tta ON mt.ru = tta.tag
            WHERE
            type = %s OR type = %s OR type = %s OR type = %s OR type = %s OR type = %s OR type = %s
            GROUP BY mt.id
            ORDER BY count DESC, date DESC"""
        cur.execute(query, params)

    data = cur.fetchall() ## [(id, 'ru', 'eng', None, None, None, None, 'type', count), (. . .),]

    for i in tree.get_children(): ## delete previous data;
        tree.delete(i)

    for j in data: ## fill with new ones;
        tree.insert("", "end", values=j)

    global count_tags
    count_tags.place_forget() ## remove old calculation;
    count_tags = Label(add_tag, text=f'Total tags: {len(data)}', font=("Arial", 18))
    count_tags.place(x=500, y=10)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## DATA ENTRY FIELDS;

# russian;
ru_lbl = Label(add_tag, text="Russian:", font=("Arial", 14))
ru_entry = Entry(add_tag, width=20, borderwidth=3, font=("Arial", 18))
ru_lbl.place(x=20, y=30)
ru_entry.place(x=20, y=60)

# english;
eng_lbl = Label(add_tag, text="English:", font=("Arial", 14))
eng_entry = Entry(add_tag, width=20, borderwidth=3, font=("Arial", 18))
eng_lbl.place(x=20, y=110)
eng_entry.place(x=20, y=140)

# alias 1;
alias1_lbl = Label(add_tag, text="First alias:", font=("Arial", 14))
alias1_entry = Entry(add_tag, width=20, borderwidth=3, font=("Arial", 18))
alias1_lbl.place(x=20, y=190)
alias1_entry.place(x=20, y=220)

# alias 2;
alias2_lbl = Label(add_tag, text="Second alias:", font=("Arial", 14))
alias2_entry = Entry(add_tag, width=20, borderwidth=3, font=("Arial", 18))
alias2_lbl.place(x=20, y=270)
alias2_entry.place(x=20, y=300)

# alias 3;
alias3_lbl = Label(add_tag, text="Third alias:", font=("Arial", 14))
alias3_entry = Entry(add_tag, width=20, borderwidth=3, font=("Arial", 18))
alias3_lbl.place(x=20, y=350)
alias3_entry.place(x=20, y=380)

# alias 4;
alias4_lbl = Label(add_tag, text="Fourth alias:", font=("Arial", 14))
alias4_entry = Entry(add_tag, width=20, borderwidth=3, font=("Arial", 18))
alias4_lbl.place(x=20, y=430)
alias4_entry.place(x=20, y=460)

# types for inserting;
type_selected_value = StringVar(value="description") ## default value;

type_lbl = Label(add_tag, text='Type:', font=('Arial', 14))
type_lbl.place(x=20, y=520)

type_options = ["description", "object", "other", "author", "copyright", "character", "unknown"] ## possible tag types;

type_combo = ttk.Combobox(add_tag, values=type_options, textvariable=type_selected_value, state="readonly", width=20, font=('Helvetica', 16))
type_combo.place(x=20, y=550) ## type dropdown list;

# types for sorting;
default_spinbox_var = StringVar(value="all") ## default value;
tag_types = ['other', 'unknown', 'copyright', 'author', 'character', 'object', 'description', 'all']

spinbox_type = ttk.Spinbox(add_tag, textvariable=default_spinbox_var, values=tag_types, width=12, font=("Arial", 10))
spinbox_type.place(x=320, y=620) ## types of tags for table sorting;

# button to send tag to database;
add_button = Button(add_tag, text="S\n\n\nE\n\n\nN\n\n\nD", width=12, height=29, borderwidth=2, bg='#fcfcee', command=send_to_table)
add_button.place(x=320, y=55)

# button to update the table;
upd_btn = Button(add_tag, text="Update", command=update_table, width=12, height=5, bg='#fcfcee')
upd_btn.place(x=320, y=510)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## TABLE WITH TAGS FROM DATABASE;
tree = ttk.Treeview(add_tag, columns=("ID", "Russian", "English", "Alias 1", "Alias 2", "Alias 3", "Alias 4", "Type", "Count"))
tree.column("#0", width=0, anchor="center")
tree.column("#1", width=10, anchor="center")
tree.column("#2", width=150, anchor="center")
tree.column("#3", width=150, anchor="center")
tree.column("#4", width=100, anchor="center")
tree.column("#5", width=100, anchor="center")
tree.column("#6", width=100, anchor="center")
tree.column("#7", width=100, anchor="center")
tree.column("#8", width=60, anchor="center")
tree.column("#9", width=10, anchor="center")

## ## ## ##

tree.heading("#1", text="ID")
tree.heading("#2", text="Russian")
tree.heading("#3", text="English")
tree.heading("#4", text="Alias 1")
tree.heading("#5", text="Alias 2")
tree.heading("#6", text="Alias 3")
tree.heading("#7", text="Alias 4")
tree.heading("#8", text="Type")
tree.heading("#9", text="Count")

tree.place(x=500, y=50, height=780, width=1200)

## ## ## ##

vsb = ttk.Scrollbar(add_tag, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)
vsb.place(x=1710, y=50, height=800) ## sidebar for scrolling;

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## TAG CHANGE WINDOW;

def description_window(): ## window for setting up an individual tag;
    item = tree.selection() ## selected cell in table;

    if item == ():
        pass ## if not selected item;
    else:
        item = tree.selection()[0]  ## selected cell in table;
        id_text = tree.item(item, "values")[0]  ## id of the selected object from the database;

        def get_similar_tags(tag_to_find): ## find all tags similar in name;
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
            return [row[0] for row in cur.fetchall()] ## sorted by usage and date;

        def fill_parent_sim(event=None): ## fill out the dropdown list;
            tag_to_find = pch_entry.get() ## entered data in the add parent tag field;
            similar_tags = get_similar_tags(tag_to_find) ## found all similar tags (ru version) to those entered by the user;
            ## ['рукава', 'длинные рукава', 'короткие рукава']

            pch_entry["values"] = similar_tags ## fill out the dropdown list;
            pch_entry.event_generate('<Down>') ## expand the list;

            selected_item = tree.selection()
            if selected_item:
                tree.selection_remove(selected_item[0])

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

        popup = Toplevel() ## tag change window instance;
        popup.title("Menu:")

        screen_width = mainw.winfo_screenwidth()
        screen_height = mainw.winfo_screenheight()

        popup_width = 1020
        popup_height = 600
        x_position = (screen_width - popup_width) // 2
        y_position = (screen_height - popup_height) // 2

        popup.geometry("{}x{}+{}+{}".format(popup_width, popup_height, x_position, y_position))

        cur.execute(f"""SELECT ru, eng, alias1, alias2, alias3, alias4, type FROM main_tags WHERE id = {id_text}""")
        pop_tag_info = cur.fetchone() ## all info about tag (tuple)

        name_entry = Entry(popup, width=36, borderwidth=3, font=("Arial", 13))
        name_entry.insert(0, f"{pop_tag_info[0]}")
        name_entry.grid(row=0, column=0, padx=30, pady=15) ## ru;

        name2_entry = Entry(popup, width=36, borderwidth=3, font=("Arial", 13))
        name2_entry.insert(0, f"{pop_tag_info[1]}")
        name2_entry.grid(row=1, column=0, padx=30, pady=15) ## eng;

        name3_entry = Entry(popup, width=36, borderwidth=3, font=("Arial", 13))
        name3_entry.insert(0, f"{pop_tag_info[2]}")
        name3_entry.grid(row=2, column=0, padx=30, pady=15) ## alias1;

        name4_entry = Entry(popup, width=36, borderwidth=3, font=("Arial", 13))
        name4_entry.insert(0, f"{pop_tag_info[3]}")
        name4_entry.grid(row=3, column=0, padx=30, pady=15) ## alias2;

        name5_entry = Entry(popup, width=36, borderwidth=3, font=("Arial", 13))
        name5_entry.insert(0, f"{pop_tag_info[4]}")
        name5_entry.grid(row=4, column=0, padx=30, pady=15) ## alias3;

        name6_entry = Entry(popup, width=36, borderwidth=3, font=("Arial", 13))
        name6_entry.insert(0, f"{pop_tag_info[5]}")
        name6_entry.grid(row=5, column=0, padx=30, pady=15) ## alias4;

        what_type = pop_tag_info[6] ## tag type;

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

        if what_type == 'author': ## if the type is "author", then insert links instead of descriptions;
            cur.execute(f"SELECT type_source, link FROM author_links WHERE artist = (SELECT ru FROM main_tags WHERE id = {id_text})")
            links = cur.fetchall() ## [('source1', 'https://link'), ('source2', 'https://link2')]
            all_links = ''

            for i in links: ## "source: link"\n;
                all_links += f'{i[0]}: {i[1]}\n'

            links_text = Text(popup, width=60, height=10, wrap=WORD) ## multiline input field for displaying sources;
            links_text.grid(row=0, column=1, rowspan=3, columnspan=2)
            links_text.insert(END, all_links)


## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
        else:
            cur.execute(f"SELECT text, language FROM descriptions WHERE id = '{id_text}' ORDER BY language DESC")
            description_all = cur.fetchall() ## [('<текст описания>', 'RU'), ('<description text>', 'EN')];

            if description_all: ## if there is a description;

                if description_all[0]: ## if there is a description in Russian;
                    description_ru = description_all[0]
                else: ## if there is no description, then return an empty list of strings;
                    description_ru = ['', '', '', '']

                if description_all[1]: ## if there is a description in English;
                    description_eng = description_all[1]
                else:
                    description_eng = ['', '', '', '']

            else: ## if there is no description in all languages;
                description_ru = ['', '', '', '']
                description_eng = ['', '', '', '']

            description_text = Text(popup, width=60, height=6, wrap=WORD)
            description_text.grid(row=0, column=1, rowspan=2, columnspan=2)
            description_text.insert(END, description_ru[0]) ## RU;

            description_text2 = Text(popup, width=60, height=6, wrap=WORD)
            description_text2.grid(row=2, column=1, rowspan=2, columnspan=2)
            description_text2.insert(END, description_eng[0]) # EN;

            ## if need another language;
            # description_text3 = Text(popup, width=60, height=6, wrap=WORD)
            # description_text3.grid(row=4, column=1, rowspan=2, columnspan=2)
            # description_text3.insert(END, description_eng[0])

        type_op = ["description", "object", "other", "author", "copyright", "character", "unknown"]

        spinbox_var = StringVar(value=f"{pop_tag_info[6]}") ## tag type;

        type_c = ttk.Combobox(popup, values=type_op, state="readonly", width=20, font=("Arial", 13))
        type_c.grid(row=6, column=0, pady=10, padx=30, sticky='we') ## dropdown list with tag types;
        type_c.set(spinbox_var.get()) ## set the type corresponding to the tag;

        def get_pop():
            name_e = name_entry.get()
            name2_e = name2_entry.get()
            name3_e = name3_entry.get()
            name4_e = name4_entry.get()
            name5_e = name5_entry.get()
            name6_e = name6_entry.get()
            type = type_c.get()

            v = [name_e, name2_e, name3_e, name4_e, name5_e, name6_e, type]
            v = [i.lower() for i in v] ## all tag data in the list is in lowercase;

            for i in range(len(v)):
                if v[i].lower() == 'none': ## if it was text, it will become a data type;
                    v[i] = None
                elif v[i].lower() == '': ## if it was an empty string, it will become type None;
                    v[i] = None

            cur.execute('''UPDATE main_tags
                            SET ru = %s, eng = %s, alias1 = %s, alias2 = %s, alias3 = %s, alias4 = %s, type = %s
                            WHERE id = %s''', (v[0], v[1], v[2], v[3], v[4], v[5], v[6], id_text))
            adb.commit() ## changing/adding translations, aliases and tag type;

            ## ## ## ##
            if what_type == 'author':
                lt1 = links_text.get(1.0, END).strip()  ## all string;

                def extract_sources(input_string):
                    pattern = re.compile(r'(\w+):\s(https?://\S+)')
                    matches = pattern.findall(input_string)

                    result = [(match[0], match[1]) for match in matches]
                    return result
                output = extract_sources(lt1)

                try:
                    cur.execute(f"DELETE FROM author_links WHERE artist = '{name_e}'")
                    adb.commit()
                    for i in output:
                        cur.execute("INSERT INTO author_links (artist, link, type_source) VALUES (%s, %s, %s)",
                                       (name_e, i[1], i[0]))
                        adb.commit()
                    print('1. Links updated!')
                except:
                    adb.rollback()
                    print('1. Links failed!')
            else:
                dt1 = description_text.get(1.0, END).strip() ## ru;
                dt2 = description_text2.get(1.0, END).strip() ## eng;

                try: ## delete the old description if there was one and add a new one;
                    cur.execute(f"DELETE FROM descriptions WHERE id = '{id_text}'")

                    cur.execute(f"""INSERT INTO descriptions (id, text, language)
                                VALUES ('{id_text}', '{dt1}', 'RU')""")

                    cur.execute(f"""INSERT INTO descriptions (id, text, language)
                                VALUES ('{id_text}', '{dt2}', 'EN')""")
                    adb.commit()

                    update_table()
                    print('1. Description updated!')

                except:
                    adb.rollback()
                    print('1. Description failed!')

            try:
                ru_need = pch_entry.get() ## get the ru name of the tag that will become the parent;
                cur.execute(f"SELECT id FROM main_tags WHERE ru = '{ru_need}'")
                need = cur.fetchone() ## get the id;
                if int(need[0]) == int(id_text): ## check for same anchor tag;
                    pass
                else:
                    cur.execute(f"INSERT INTO parents_children (mother, child) VALUES (%s, %s)", (need[0], id_text))
                    adb.commit() ## link parent and selected tags;
                    print("2. The parent tag has been successfully installed!")
            except:
                adb.rollback()
                print("2. The parent tag is not set!")

            print("3. All updated!\n")
            pch_entry.delete(0, END)
            new_values_combo()

        get_en = Button(popup, text="CONFIRM", command=get_pop, width=20, height=2)
        get_en.grid(row=7, column=0, padx=20, pady=40, sticky='we')

        pch_entry = ttk.Combobox(popup, width=30, font=("Arial", 13)) ## dropdown list with all tags and search;

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

        mother_tags_cmb = ttk.Combobox(popup, font=("Arial", 13), state="readonly")
        child_tags_cmb = ttk.Combobox(popup, font=("Arial", 13), state="readonly")

        def new_values_combo(): ## fill parent and child lists with new values;
            cur.execute(f"""SELECT ru FROM parents_children
                            JOIN main_tags ON main_tags.id = parents_children.mother
                            WHERE child = '{id_text}'
                            """)
            mother_tags = cur.fetchall()
            mother_tags_form = []
            for i in mother_tags:
                mother_tags_form += i
            mother_tags_cmb["values"] = mother_tags_form

            ## ## ## ##

            cur.execute(f"""SELECT ru FROM parents_children
                            JOIN main_tags ON main_tags.id = parents_children.child
                            WHERE mother = '{id_text}'
                        """)
            child_tags = cur.fetchall()
            child_tags_form = []
            for i in child_tags:
                child_tags_form += i
            child_tags_cmb["values"] = child_tags_form

        new_values_combo() ## updating data after confirmation;

        pch_entry.grid(row=7, column=1, columnspan=2, sticky='n') ## specify parent tag;;
        mother_tags_cmb.grid(row=8, column=1, sticky='we', padx=10) ## already specified parent tags;
        child_tags_cmb.grid(row=8, column=2, sticky='we', padx=10) ## already specified child tags;

        ## ##

        pch_lbl = Label(popup, text='Добавить родителя:', font=("Arial", 13))
        pch_lbl.grid(row=6, column=1, columnspan=2, sticky='s')

        mother_tags_lbl = Label(popup, text='Родительные:', font=("Arial", 13))
        mother_tags_lbl.grid(row=7, column=1, sticky='s')

        child_tags_lbl = Label(popup, text='Дочерние:', font=("Arial", 13))
        child_tags_lbl.grid(row=7, column=2, sticky='s')

        ## ##

        cur.execute(f"SELECT date FROM main_tags WHERE id = '{id_text}'")
        date_added = cur.fetchone()[0]
        formatted_date = date_added.strftime("%d.%m.%Y")
        date_lbl = Label(popup, text=f'Тег добавлен:\n{formatted_date}', font=("Arial", 13))
        date_lbl.grid(row=1, column=3, padx=10, rowspan=2) ## date the tag was added to the database;

        ## ##

        ## expand and fill the list of tags;
        # pch_entry.bind("<Button-1>", fill_parent_sim) ## LBM;
        pch_entry.bind("<Return>", fill_parent_sim) ## Enter;
        pch_entry.bind("<<ComboboxSelected>>", fill_parent_sim)
        fill_parent_sim()

descption_window_btn = Button(add_tag, text="Check description", command=description_window, width=16, height=2)
descption_window_btn.place(x=1740, y=60) ## button to open the tag editing window;

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## REMOVING A TAG FROM DATABASE;
def delete_tag():
    item = tree.selection() ## selected cell in table;
    if item == ():
        pass
    else:
        item = tree.selection()[0]
        id_text = tree.item(item, "values")[0] ## id from table;

        cur.execute(f"SELECT ru, eng FROM main_tags WHERE id = '{id_text}'")
        confirm_del_tag = cur.fetchall() ## RU and EN tag name;

        popup2 = Toplevel() ## delete window instance;
        popup2.title("Delete menu:")

        screen_width = mainw.winfo_screenwidth()
        screen_height = mainw.winfo_screenheight()

        popup_width = 440
        popup_height = 170

        popup2.geometry("{}x{}+{}+{}".format(popup_width, popup_height, 1200, 140))

        frame = Frame(popup2)
        frame.pack(expand=True, fill='both')

        confirm_lbl = Label(frame, text=f'Are you sure you want to remove the tag\n<{confirm_del_tag[0][0]} / {confirm_del_tag[0][1]}>?')
        confirm_lbl.pack(pady=10)

        button_frame = Frame(frame)
        button_frame.pack(pady=20)

        def del_tag(): ## remove tag and close a window;
            cur.execute(f"""DELETE FROM main_tags WHERE id = '{id_text}'""")
            adb.commit()
            popup2.destroy()
            update_table()

        def on_no(): ## close the window;
            popup2.destroy()

        yes_confirm = Button(button_frame, text='YES', width=15, height=2, command=del_tag)
        yes_confirm.pack(side='left', padx=10, pady=20)

        no_confirm = Button(button_frame, text='NO', width=15, height=2, command=on_no)
        no_confirm.pack(side='right', padx=10, pady=20)

delete_tag_btn = Button(add_tag, text="DELETE", command=delete_tag, width=16, height=2)
delete_tag_btn.place(x=1740, y=120)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## CONTEXT MENU;
def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)

context_menu = Menu(mainw, tearoff=0)
context_menu.add_command(label="Description", command=description_window)
context_menu.add_command(label="Delete", command=delete_tag)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## USING THE ARROWS TO SWITCH BETWEEN INPUT FIELDS: UP / DOWN;

ru_entry.bind("<Down>", focus_next)
ru_entry.bind("<Up>", focus_previous)

eng_entry.bind("<Down>", focus_next)
eng_entry.bind("<Up>", focus_previous)

alias1_entry.bind("<Down>", focus_next)
alias1_entry.bind("<Up>", focus_previous)

alias2_entry.bind("<Down>", focus_next)
alias2_entry.bind("<Up>", focus_previous)

alias3_entry.bind("<Down>", focus_next)
alias3_entry.bind("<Up>", focus_previous)

alias4_entry.bind("<Down>", focus_next)
alias4_entry.bind("<Up>", focus_previous)

## ## action after pressing Enter (go below or send);

ru_entry.bind("<Return>", handle_enter)
eng_entry.bind("<Return>", handle_enter)
alias1_entry.bind("<Return>", handle_enter)
alias2_entry.bind("<Return>", handle_enter)
alias3_entry.bind("<Return>", handle_enter)
alias4_entry.bind("<Return>", handle_enter)

search_entry.bind("<Return>", handle_enter)

tree.bind("<Button-3>", show_context_menu)

## ## ## ##
update_table()
mainw.mainloop()
cur.close()
adb.close()










