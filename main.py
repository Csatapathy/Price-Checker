from tkinter import *
import sqlite3
import tkinter.ttk as ttk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
import smtplib

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/84.0.4147.105 Safari/537.36'}  # typing user agent in chrome

root = Tk()
root.title("WATCHLIST")
root.geometry('1000x450')

left_frame = Frame(root, width=700, height=230, background='#3d70b2')
left_frame.grid_propagate(0)
left_frame.grid(row=0, column=0)

below_frame = Frame(root, width=700, height=250, bg="blue")
below_frame.grid_propagate(0)
below_frame.grid(row=1, column=0)

right_frame = Frame(root, width=300, height=450, background='#0b172a')
right_frame.grid_propagate(0)
right_frame.grid(row=0, column=1, rowspan=2)


def input_database(name, price, url):
    """
    inputs and stores into the database called product
    """
    my_database = sqlite3.connect('my_database.db')  # creates a db
    c = my_database.cursor()  # creates a cursor to do stuff
    # creating a table and once we've created this we no longer need to run this and create another database
    # c.execute("""CREATE TABLE product(
    #             name_product text,
    #             price_product integer,
    #             url_product text
    #             )""")
    # insert into table
    c.execute("INSERT INTO product VALUES(:name_product,:price_product,:url_product)",
              {
                  'name_product': name,
                  'price_product': price,
                  'url_product': url
              })
    my_database.commit()  # saves the data
    my_database.close()  # closes the connection
    tree.delete(*tree.get_children())
    display_database()


def check_price(price, url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.find(id="productTitle").get_text()
    price = soup.find(id="priceblock_ourprice").get_text()
    convertedPrice = float(str.replace(price[2:], ",", ""))
    return convertedPrice


def check_prices():
    tree.delete(*tree.get_children())
    my_database = sqlite3.connect('my_database.db')  # creates a db
    c = my_database.cursor()  # creates a cursor to do stuff
    c.execute("SELECT *,oid FROM product")
    records = c.fetchall()

    i = 0
    for record in records:
        price = check_price(record[1], record[2])
        if price <= record[1]:
            send_mail(record[0], record[1], record[2], price)
            yes = "YES"
        else:
            yes = "NOT YET"
        i = i + 1
        tree.insert('', "end", text=str(i), values=(record[0], price, record[1], yes))

    my_database.commit()  # saves the data
    my_database.close()  # closes the connection


def display_database():
    """
    displays the contents of the database in the treeview
    """
    my_database = sqlite3.connect('my_database.db')  # creates a db
    c = my_database.cursor()  # creates a cursor to do stuff
    c.execute("SELECT *,oid FROM product")
    records = c.fetchall()

    i = 0
    for record in records:
        i = i + 1
        tree.insert('', "end", text=str(i), values=(record[0], ' ', record[1], ' '))

    my_database.commit()  # saves the data
    my_database.close()  # closes the connection


def send_mail(name, selling, url, buying):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('fordownloadsonly2019@gmail.com', 'jzygsmvpjosdbooc')

    subject = "PRICES FELL DOWN!! Your product : " + name.upper() + "\n is on sale now for ₹" + str(buying) + " dropped from ₹" + str(
        selling) + "\n HURRY UP!"
    body = "Check the link below :\n" + url
    msg = f"Subject: {subject}\n\n{body}"
    email = []
    for line in open('email.txt'):
        email.append(line)
    server.sendmail('fordownloadsonly2019@gmail.com',
                    email,
                    msg.encode("utf8"))
    server.quit()


def delete_database():
    """
    function to delete an entry
    """

    my_database = sqlite3.connect('my_database.db')  # creates a db
    c = my_database.cursor()  # creates a cursor to do stuff
    a = select_item()
    print(f"a:{a}")
    c.execute("DELETE from product WHERE oid=" + a)
    my_database.commit()  # saves the data
    my_database.close()  # closes the connection
    tree.delete(*tree.get_children())
    display_database()


def update_database():
    editor = Tk()
    editor.title("Update a record")
    editor.geometry("300x200")

    my_database = sqlite3.connect('my_database.db')  # creates a db
    c = my_database.cursor()  # creates a cursor to do stuff
    record_id = (select_item())
    print(record_id)
    print(type(record_id))
    c.execute("SELECT *FROM product WHERE Product Name=" + record_id)
    records = c.fetchall()

    entry_label_new = LabelFrame(editor, text='Edit an existing product', font=('calibri', 9, 'bold'), bg='#0b172a',
                             fg='white')
    entry_label_new.pack(expand='yes', fill='both')
    product_entry_new = Entry(entry_label, background='white', width=45)
    product_entry_new.grid(row=0, column=0, padx=10, pady=10)
    url_entry_new = Entry(entry_label, background='white', width=45)
    url_entry_new.grid(row=1, column=0, padx=10)
    price_entry_new = Entry(entry_label, background='white', width=45)
    price_entry_new.grid(row=2, column=0, padx=10, pady=10)

    for record in records:
        product_entry_new.insert(0, record[0])
        price_entry_new.insert(0, record[1])
        url_entry_new.insert(0, record[2])

    c.execute("""UPDATE product SET
        name_product = :name
        price_product = :price
        url_product = :url
        WHERE oid= :oid""",
              {
                  'name': product_entry_new.get(),
                  'price': price_entry_new.get(),
                  'url': url_entry_new.get()
              }
              )

    def destroy():
        editor.destroy()

    save_button = Button(entry_label, text="Save Record", width=20, command=destroy)
    save_button.grid(row=3, column=0, padx=10, pady=10)

    my_database.commit()  # saves the data
    my_database.close()  # closes the connection
    display_database()


def select_item():
    curr = tree.focus()
    return tree.item(curr)['values'][0]
    # return tree.item(curr)['text']


def set_email():
    window = Tk()
    window.title("SET EMAIL ID")
    window.geometry("400x300")
    info_label = Label(window, text="Once the price of the product on your watchlist gets below your wish price,\n"
                                    "we will send you a notification link to this email-id.\n"
                                    "You can change this email-id any time you want!")
    info_label.grid(row=0, column=0)
    myframe = Frame(window)
    email_label = Label(myframe, text="Email ID:")
    email_label.grid(row=0, column=0)
    email_entry = Entry(myframe, bg="white", width=20)
    email_entry.grid(row=0, column=1)
    myframe.grid(row=1, column=0)

    def destroy():
        with open('email.txt', mode='r+') as f:
            f.write(email_entry.get())
        window.destroy()

    submit_button = Button(myframe, text="Submit", width=20, command=destroy)
    submit_button.grid(row=2, columnspan=2)


tree = ttk.Treeview(left_frame, style="mystyle.Treeview",
                    columns=('S.no.', 'Product Name', 'Price of product', 'Price Set', 'Email sent'))
tree.heading("#0", text="S.no.")
tree.heading("#1", text="Product Name")
tree.heading("#2", text="Price (Product)")
tree.heading("#3", text="Price (Preferred)")
tree.heading("#4", text="Email sent")

tree.column('#0', width=46)
tree.column('#1', width=350)
tree.column('#2', width=100)
tree.column('#3', width=100)
tree.column('#4', width=100)
tree.bind('<Control-Button-1>', select_item)
tree.grid(row=0, column=0)
display_database()

space_label = Label(below_frame,
                    text='                                                                                                      ',
                    bg="blue")
space_label.grid(row=1, column=0)
delete_button = Button(below_frame, text='Delete Selected', width=20, pady=10, command=delete_database)
delete_button.grid(row=0, column=1)
space_label = Label(below_frame,
                    text='                                                   ',
                    bg="blue")
space_label.grid(row=1, column=1)
email_button = Button(below_frame, text='Set Email ID', width=20, pady=10, command=set_email)
email_button.grid(row=2, column=1)
space_label = Label(below_frame,
                    text='                                                   ',
                    bg="blue")
space_label.grid(row=3, column=1)
update_entry = Entry(below_frame, bg='white', width=24)
update_entry.insert(0, "Write the index to update")
update_entry.grid(row=4, column=1)
space_label = Label(below_frame,
                    text='                                                   ',
                    bg="blue")
space_label.grid(row=5, column=1)
update_button = Button(below_frame, text="Update", width=20, pady=10, command=update_database)
update_button.grid(row=6, column=1)


class MyDialog:
    """
    dialog box for telling that we've been successful
    """

    def __init__(self, parent):
        top = self.top = Toplevel(parent, bg='orange')
        top.geometry('500x70')
        self.myLabel = Label(top, bg='orange',
                             text='Your product has been kept on the watchlist.\n When the price on the site '
                                  'decreases below your preffered price, we will send you an email')
        self.myLabel.pack()
        self.mySubmitButton = Button(top, text='Okay', command=self.send)
        self.mySubmitButton.pack()

    def send(self):
        self.top.destroy()


class NoInput:
    """
    dialog box to tell that there is no input or the input is wrong
    """

    def __init__(self, parent):
        top = self.top = Toplevel(parent, bg='orange')
        top.geometry('500x70')
        self.myLabel = Label(top, bg='orange',
                             text='You have not input anything, please check.')
        self.myLabel.pack()
        self.mySubmitButton = Button(top, text='Okay', command=self.send)
        self.mySubmitButton.pack()

    def send(self):
        self.top.destroy()


class Product:
    """
    class to keep the products
    """

    def __init__(self, name, url, price):
        self.name = name
        self.url = url
        self.price = price


def set_product():
    if len(price_entry.get()) == 0 or len(product_entry.get()) == 0 or len(url_entry.get()) == 0:
        inputDialog = NoInput(root)
        root.wait_window(inputDialog.top)
        product_entry.insert(0, 'Enter the Product name')
        url_entry.insert(0, 'Enter the product url')
        price_entry.insert(0, 'Buy Price (₹)')

    else:
        name_product = product_entry.get()
        url_product = url_entry.get()
        price_product = price_entry.get()
        new_prod = Product(name_product, url_product, price_product)
        product_entry.delete(0, 'end')
        price_entry.delete(0, 'end')
        url_entry.delete(0, 'end')
        input_database(name_product, price_product, url_product)
        inputDialog = MyDialog(root)
        root.wait_window(inputDialog.top)
        product_entry.insert(0, 'Enter the Product name')
        url_entry.insert(0, 'Enter the product url')
        price_entry.insert(0, 'Buy Price (₹)')


main_label = Label(right_frame, text='PRODUCT WATCHLIST', bg='#0b172a', font=('calibre', 10, 'bold'), fg='white')
main_label.grid(row=0, column=0)
main_label = Label(right_frame, text='                       ', bg='#0b172a', font=('calibre', 10, 'bold'), fg='white')
main_label.grid(row=1, column=0)
main_label = Label(right_frame, text='                       ', bg='#0b172a', font=('calibre', 10, 'bold'), fg='white')
main_label.grid(row=2, column=0)
main_label = Label(right_frame, text='                       ', bg='#0b172a', font=('calibre', 10, 'bold'), fg='white')
main_label.grid(row=3, column=0)
main_label = Label(right_frame, text='                       ', bg='#0b172a', font=('calibre', 10, 'bold'), fg='white')
main_label.grid(row=4, column=0)

entry_frame = Frame(right_frame, background='#0b172a')
entry_label = LabelFrame(entry_frame, text='Set a new product', font=('calibri', 9, 'bold'), bg='#0b172a', fg='white')
entry_label.pack(expand='yes', fill='both')
product_entry = Entry(entry_label, background='white', width=45)
product_entry.insert(0, 'Enter the Product name')
product_entry.grid(row=0, column=0, padx=10, pady=10)
url_entry = Entry(entry_label, background='white', width=45)
url_entry.insert(0, 'Enter the product url')
url_entry.grid(row=1, column=0, padx=10)
price_entry = Entry(entry_label, background='white', width=45)
price_entry.insert(0, 'Buy Price (₹)')
price_entry.grid(row=2, column=0, padx=10, pady=10)
entry_frame.grid(row=5, column=0)

main_label = Label(right_frame, text='                       ', bg='#0b172a', font=('calibre', 10, 'bold'), fg='white')
main_label.grid(row=6, column=0)
main_label = Label(right_frame, text='                       ', bg='#0b172a', font=('calibre', 10, 'bold'), fg='white')
main_label.grid(row=7, column=0)

grid_frame = Frame(right_frame, background='#0b172a')
product_button = Button(grid_frame, text="Set Product", width=25, height=2, command=set_product)
product_button.grid(row=0, column=0, padx=60, pady=5)
check_button = Button(grid_frame, text="Check Prices", width=25, height=2, command=check_prices)
check_button.grid(row=1, column=0, padx=60, pady=5)
grid_frame.grid(row=8, column=0)

root.mainloop()
