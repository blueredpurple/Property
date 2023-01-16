# import sqlite3 as sq
import sqlite3 as sq
import PySimpleGUI as sg
import pandas as pd
from datetime import datetime
con = sq.connect('PROJECT_DATABASE_UPDATED.db')
cur = con.cursor()
window = ''
def Main():
    choices = ('Customer', 'Owner', 'Admin')
    layout = [[sg.Text('Welcome! Please proceed with your role.')],
              [sg.Combo(choices, size=(15, len(choices)), key='chosen_role')],
              [sg.Button('OK')]]
    return sg.Window('Main Window', layout)
def Button_ChooseRole(values):
    global window
    if  not values['chosen_role']:
        sg.popup('Please choose a role in order to proceed with the service.')
    if values['chosen_role']=='Customer':
        window.close()
        window = customer_login()
    if values['chosen_role']=='Admin':
        window.close()
        window = admin_login()
    if values['chosen_role']=='Owner':
        window.close()
        window = owner_login()

# Customer

# Initialize important variables

PID = ''
Name = ''
SSN = ''
tfrom = ''
tto = ''
coupon = ''
price = ''
From = ''
To = ''
EPID = ''
AID = ''
code = ''
BookID = ''

# Windows

def customer_login():
    layout = [[sg.Text('Please enter your information below')],
              [sg.Text('ID', size =(10,1)), sg.Input(size = (10,1), key='id')],
              [sg.Text('Password', size =(10,1)), sg.Input(size = (10,1), key='password')],
              [sg.Button('Login'), sg.Button('Return to Main Page')]]
    return sg.Window('Login Window', layout)

def list_properties():
    global Name
    properties = []
    for row in cur.execute('''SELECT PID, Pname, City, Address, Ptype
                          FROM Property'''):
        properties.append(row)
    cities = []
    for row in cur.execute('SELECT DISTINCT City FROM Property'):
        cities.append(row[0])
    types = []
    for row in cur.execute('SELECT DISTINCT Ptype FROM Property'):
        types.append(row[0])
    layout = [[sg.Text(f'Welcome {Name}! Below are the properties with their name, city, address, type and the interval when they are available respectively')],
              [sg.Text('Select City:')], 
              [sg.Combo(cities, size=(25,7), key='city')],
              [sg.Text('Select Property type:')], 
              [sg.Combo(types, size=(25,7), key='type')],
              [sg.Button('List Properties')],
              [sg.Listbox(properties, size=(100,10), key='property')],
              [sg.Button('Continue'), sg.Button('Check Rating and Reviews'), sg.Button('Rate your previous books')],
              [sg.Button('Log Out')]]
    return sg.Window('Main page', layout) 

def comments():  #check comments and the rating of the property
    global EPID
    rating = []
    for row in cur.execute('''SELECT Rating FROM Property WHERE PID=?''',(EPID,)):
        rating.append(row[0])
    rating = rating[0]
    comments = []
    for row in cur.execute('''SELECT Comment FROM Evaluation
                              WHERE PID=?''',(EPID,)):
        comments.append(row[0])
    layout = [[sg.Text(f'The chosen property has a rating of {rating}!')],
              [sg.Text('Check the reviews about this property below')],
              [sg.Listbox(comments, size=(50,10))],
              [sg.Text('Add a comment:'), sg.Input(size = (10,1), key='comment'), sg.Button('Enter')],
              [sg.Button('Go to previous page')]]
    return sg.Window('Reviews', layout)

def rate():
    global SSN
    global EPID
    books = []
    for row in cur.execute('''SELECT B.BookID, B.dfrom, B.dto, B.tprice, P.Pname 
                              FROM Books B, Property P 
                              WHERE B.Customer_ID=? AND P.PID=B.PID AND P.PID=? 
                              ''',(SSN,EPID)):
        books.append(row)
    todaysDate = datetime.today().strftime('%Y-%m-%d')
    tdy = todaysDate.split('-')
    today = datetime(int(tdy[0]),int(tdy[1]),int(tdy[2]))
    i = 0
    b = []
    while i<len(books):
        dt = books[i][2].split('-')
        dto = datetime(int(dt[0]),int(dt[1]),int(dt[2]))
        diff = (today-dto).days
        if diff>0:
            b.append(books[i])
        i += 1
    ratings = (1,2,3,4,5)
    layout = [[sg.Text('Choose the previous book you want to rate:')],
              [sg.Listbox(b, size=(50,10), key='book')],
              [sg.Combo(ratings, size=(25,7), key='rating'), sg.Button('Give Rating')],
              [sg.Button('Go to previous page')]]
    return sg.Window('Rating', layout)
  
    
def time_slots():
    global PID
    time_slots = []
    for row in cur.execute('''SELECT afrom, ato, AID
                              FROM HasAvailability H
                              WHERE marks=? AND PID=?''' ,('available',PID)):
        time_slots.append(row)
    layout = [[sg.Text('Choose the time slot you want to choose a duration from:')],
              [sg.Listbox(time_slots, size=(50,10), key='slot')],
              [sg.Button('continue'), sg.Button('Choose another property'), sg.Button('Log Out')]]
    return sg.Window('Time Slots', layout)

def book():
    global price
    global tfrom
    global tto
    global coupon
    global PID
    price = []
    for row in cur.execute("SELECT Nprice FROM Property WHERE PID=?", (PID,)):
        price.append(row[0])
    price = price[0]
    datelist = pd.date_range(tfrom, tto)
    List = []
    for i in datelist:
        List.append(i.strftime('%Y-%m-%d'))
    coupon = []
    for row in cur.execute("SELECT Coupon FROM Customer WHERE SSN=?",(SSN,)):
        coupon.append(row[0])
    coupon = coupon[0]
    layout = [[sg.Text(f'The price per night for this property is ${price}. The coupon provides %10 decrease in the price!')],
              [sg.Text('Enter the coupon code here:'), sg.Input(size=(10,1), key='code')],
              [sg.Text('Enter the period you want to rent in the following format yyyy-mm-dd:')],
              [sg.Text('From:'), sg.Combo(List,size=(10,1), key='dfrom'), sg.Text('To:'), sg.Combo(List, size=(10,1), key='dto')],
              [sg.Button('Proceed to payment'), sg.Button('Choose another property')]]
    return sg.Window('Booking',layout)

def payment():
    global price
    global From
    global To
    price = difference*price
    layout = [[sg.Text(f"You have chosen to book this property from the day {From} to the day {To} for a price of ${price}")],
             [sg.Text('Do you want to rent this property?')],
             [sg.Button('Yes'),sg.Button('Cancel')]]
    return sg.Window('Payment', layout)



# Buttons

def Button_customer_login(values): 
    global window
    global Name
    global SSN
    L = []
    for row in cur.execute('SELECT U.SSN FROM User U, Customer C WHERE U.SSN=C.SSN'):
        L.append(str(row[0]))
    if values['id'] and values['password']:
        if values['id'] in L:
            p = []
            for row in cur.execute('SELECT Password FROM User WHERE SSN=?', (values['id'],)):
                p.append(row[0])
            password = p[0]
            if values['password'] != password:
                sg.popup('Wrong ID or Password!')
            if values['password'] == password:
                for row in cur.execute('SELECT Name FROM User WHERE SSN=?',(values['id'],)):
                    Name = row[0]
                SSN = values['id']
                window.close()
                window = list_properties()
        if values['id'] not in L:
            sg.popup('You have to create an account first!') 
    else:
        sg.popup('ID or Password cannot be empty!')

def Button_list_properties(values):
    global window
    City = values['city']
    Type = values['type']
    properties = []
    if City == '' and Type:
        for row in cur.execute('''SELECT PID, Pname, City, Address, Ptype
                              FROM Property 
                              WHERE Ptype=?''',(Type,)):
            properties.append(row)
    elif City and Type == '':
        for row in cur.execute('''SELECT PID, Pname, City, Address, Ptype
                              FROM Property 
                              WHERE City=?''',(City,)):
            properties.append(row)
    elif City and Type:
        for row in cur.execute('''SELECT PID, Pname, City, Address, Ptype
                              FROM Property 
                              WHERE Ptype=? AND City=?''',(Type,City)):
            properties.append(row)   
    elif City == '' and Type == '':
        for row in cur.execute('''SELECT PID, Pname, City, Address, Ptype
                              FROM Property '''):
            properties.append(row)
    window.Element('property').Update(values=properties)
    
def Button_check_reviews(values):
    global window
    global EPID
    if not values['property']:
        sg.popup('Please choose a property to see the reviews.')
    else:
        EPID = values['property'][0][0]
        window.close()
        window = comments()
    
def Button_previous_books(values):
    global window 
    global EPID
    global SSN
    if not values['property']:
        sg.popup('Please choose a property to rate the previous books!')
    else:
        EPID = values['property'][0][0]
        b = []
        for row in cur.execute('''SELECT Customer_ID FROM Books 
                                  WHERE PID=?''',(EPID,)):
            b.append(row[0])
        con = 0
        for i in b:
            if int(SSN)==int(i):
                con = 1
        if con==1:
            todaysDate = datetime.today().strftime('%Y-%m-%d')
            tdy = todaysDate.split('-')
            today = datetime(int(tdy[0]),int(tdy[1]),int(tdy[2]))
            l = []
            for row in cur.execute('''SELECT dto FROM Books WHERE Customer_ID=?''',(SSN,)):
                l.append(row[0])
            condition = 0
            D = 0
            for i in l:
                d = i.split('-')
                dto = datetime(int(d[0]),int(d[1]),int(d[2]))
                diff = (dto-today).days
                if diff<0:
                    D += 1
            if D>0:
                window.close()
                window = rate()
            if D==0:
                sg.popup('You cannot rate a service until the service is finished!')
        else:
            sg.popup('You have not booked this property before!')

            
            
def Button_Continue(values):
    global window
    global PID
    if not values['property']:
        sg.popup('Please choose a property to continue with the process!')
    else:
        av = []
        for row in cur.execute("SELECT PID FROM HasAvailability WHERE marks=?",('available',)):
            av.append(row[0])
        PID = values['property'][0][0]
        if PID in av:
            window.close()
            window = time_slots()
        else:
            sg.popup('This property is not available')
            
def Button_continue(values):
    global window
    global tfrom
    global tto
    global AID
    if not values['slot']:
        sg.popup('Please choose a time slot!')
    else:
        tfrom = values['slot'][0][0]
        tto = values['slot'][0][1]
        AID = values['slot'][0][2]
        window.close()
        window = book()

def Button_proceed_to_payment(values):
    global window
    global price
    global difference
    global code
    global From
    global To
    global code
    From = values['dfrom']
    To = values['dto']
    code = values['code']
    dfrom = values['dfrom'].split('-')
    dto = values['dto'].split('-')
    if not values['dfrom'] or not values['dto']:
        sg.popup('Please choose the duration between two dates!')
    else:
        df = datetime(int(dfrom[0]),int(dfrom[1]),int(dfrom[2]))
        dt = datetime(int(dto[0]),int(dto[1]),int(dto[2]))
        difference = (dt-df).days
        if difference<=0:
            sg.popup('Please choose a propert date!')
        else:
            if not coupon:
                if code:
                    sg.popup('You do not have a coupon, leave this box empty.')
                if not code:
                    window.close()
                    window = payment()
            if coupon:
                if code==coupon:
                    price -= price*0.1
                    window.close()
                    window = payment()
                if not code:
                    window.close()
                    window = payment()
                if code and code!=coupon:
                    sg.popup('Enter the correct coupon code or leave it empty if you do not want to use it')
    
def Button_complete():
    global window
    global SSN
    global PID
    global AID
    global From
    global To
    global tfrom
    global tto
    global code
    global price
    global coupon
    global BookID
    BookID = []
    for row in cur.execute('SELECT MAX(BookID) FROM Books'):
        BookID.append(row[0])
    BookID = BookID[0]+1
    new_book = (BookID, PID, SSN, From, To, price, code)
    new_book0 = (BookID, PID, SSN, From, To, price)
    if code!='':
        cur.execute('''INSERT INTO Books (BookID,PID,Customer_ID,dfrom,dto,tprice,dcode) 
                    values(?,?,?,?,?,?,?)''',new_book)
    if code=='':
        cur.execute('''INSERT INTO Books (BookID,PID,Customer_ID,dfrom,dto,tprice) 
                    values(?,?,?,?,?,?)''',new_book0)
    if code==coupon:
        cur.execute('UPDATE Customer SET Coupon=? WHERE SSN=?',('',SSN,))
    new_AID = []   
    for row in cur.execute('SELECT MAX(AID) FROM HasAvailability'):
        new_AID.append(row[0])
    new_AID = new_AID[0]+1
    cur.execute('DELETE FROM HasAvailability WHERE AID=?',(AID,))
    AID1 = 0
    AID2 = 0
    if From==tfrom and To!=tto:
        AID1 = new_AID
        new_availability = (AID1, PID, To, tto, 'available') 
        cur.execute('INSERT INTO HasAvailability VALUES(?,?,?,?,?)',new_availability)
    if From!=tfrom and To==tto:
        AID1 = new_AID
        new_availability = (AID1, PID, tfrom, To, 'available')
        cur.execute('INSERT INTO HasAvailability values(?,?,?,?,?)',new_availability)
    if From!=tfrom and To!=tto:
        AID1 = new_AID
        AID2 = new_AID+1
        new_availability1 = (AID1, PID, tfrom, From, 'available')
        new_availability2 = (AID2, PID, To, tto, 'available')
        cur.execute('INSERT INTO HasAvailability values(?,?,?,?,?)',new_availability1)
        cur.execute('INSERT INTO HasAvailability values(?,?,?,?,?)',new_availability2)
    window.close()
    sg.popup('Thanks for choosing us!')
    window = list_properties()
        

def Button_leave_comment(values):
    global window
    global EPID
    if not values['comment']:
        sg.popup('You cannot leave an empty comment!')
    if values['comment']:
        new = []
        for row in cur.execute('SELECT MAX(EID) FROM Evaluation'):
            new.append(row)
        new = new[0][0]+1
        cnew = str(new)
        anon = 'anon_'+cnew
        cur.execute('INSERT INTO Evaluation VALUES(?,?,?,?)',(new, EPID, anon, values['comment']))
        sg.popup('Thanks for the comment!')
    
def Button_give_rating(values):
    global window
    global EPID
    rating = values['rating']
    book = values['book'][0]
    if not book and rating!='':
        sg.popup('Pleas choose a previous book to rate!')
    elif book and rating=='':
        sg.popup('Please choose a rating!')
    elif not book and rating=='':
        sg.popup('Please choose a previous book and the rating you want to give!')
    else:
        cur.execute('UPDATE Books SET Srating=? WHERE BookID=?',(rating,book[0]))
        prating = []
        for row in cur.execute('SELECT AVG(Srating) FROM Books WHERE PID=?', (EPID,)):
            prating.append(row[0])
        prating = prating[0]
        cur.execute('UPDATE Property SET Rating=? WHERE PID=?', (prating, EPID))
        sg.popup('Thanks for your rating')
        
# Admin

# Initialize important variables
admin_id = []
for row in cur.execute('SELECT Admin_id FROM Admin'):
    admin_id.append(row)
admin_id = admin_id[0][0]
admin_name = []
for row in cur.execute('SELECT Admin_name FROM Admin'):
    admin_name.append(row)
admin_name = admin_name[0][0]
admin_password = []
for row in cur.execute('SELECT Admin_password FROM Admin'):
    admin_password.append(row)
admin_password = admin_password[0][0]
PID = ''
Pname = ''

# Windows

def admin_login():
    layout = [[sg.Text('Please enter your information below')],
              [sg.Text('ID:', size =(10,1)), sg.Input(size = (10,1), key='id')],
              [sg.Text('Password:', size =(10,1)), sg.Input(size = (10,1), key='password')],
              [sg.Button('login'), sg.Button('Return to Main Page')]]
    return sg.Window('Admin Window', layout)

def admin_main():
    global admin_name
    properties = []
    for row in cur.execute('''SELECT PID, Pname, City, Address, Ptype, Rating
                          FROM Property'''):
        properties.append(row)    
    customers = []
    for row in cur.execute('''SELECT U.SSN, U.Name FROM Customer C, User U WHERE C.SSN=U.SSN'''):
        customers.append(row)
    owners = []
    for row in cur.execute('''SELECT U.SSN, U.Name FROM Owner O, User U WHERE O.SSN=U.SSN'''):
        owners.append(row)
    layout = [[sg.Text(f'Welcome {admin_name}!')],
              [sg.Text('Below are lists of all properties, owners and customers respectively.')],
              [sg.Text('Please choose a property to update its information.')],
              [sg.Listbox(properties, size=(50,10), key='property'),
               sg.Listbox(owners, size=(20,10), key='owner'),
               sg.Listbox(customers, size=(20,10), key='customer')],
              [sg.Button('Check Availability'), sg.Button('Update Comments'), sg.Button('Change Rating')],
              [sg.Button('Return to Main Page')]]
    return sg.Window('Main Page', layout)

def admin_availability():
    global PID
    global Pname
    time_slots = []
    for row in cur.execute('''SELECT afrom, ato
                              FROM HasAvailability 
                              WHERE marks=? AND PID=?''' ,('available',PID)):
        time_slots.append(row)
    layout = [[sg.Text(f'Below are the time slots where the chosen property {Pname} is available')],
              [sg.Listbox(time_slots, size=(50,10), key='slot')],
              [sg.Button('Back')]]
    return sg.Window('Time Slots', layout)

def admin_update_comments():
    global PID
    global Pname
    comments = []
    for row in cur.execute('''SELECT EID, Comment FROM Evaluation
                          WHERE PID=?''',(PID,)):
        comments.append(row)
    layout = [[sg.Text(f'Below are the comments on the property {Pname}.')],
              [sg.Text(f'You can delete any of the written comments.')],
              [sg.Listbox(comments, size=(100,10), key='comment')],
              [sg.Button('Delete Comment'), sg.Button('Back')]]
    return sg.Window('Comments', layout)

def admin_update_rating():
    global PID
    global Pname
    layout = [[sg.Text(f'Below you can enter a new rating for the property {Pname} such that it isbetween 1 and 5 inclusive)')],
              [sg.Text('Enter rating:'), sg.Input(size=(10,1), key='rating'), sg.Button('Enter Rating')],
              [sg.Button('Back')]]
    return sg.Window('Rating Change', layout)

# Buttons 

def button_admin_login(values):
    global window
    global admin_id
    global admin_password
    if values['id'] and values['password']:
        if values['id']==admin_id and values['password']==admin_password:
            window.close()
            window = admin_main()
        if values['id']!=admin_id or values['password']!=admin_password:
            sg.popup('Wrong ID or Password!')
    else:
        sg.popup('ID or Password cannot be empty!')
        
def button_admin_availability(values):
    global window
    global PID
    global Pname
    if not values['property']:
        sg.popup('Please choose the property you want to check availability for!')
    else:
        prop = values['property'][0]
        PID = prop[0]
        Pname = prop[1]
        window.close()
        window = admin_availability()
    
def button_admin_update_comments(values):
    global window
    global PID
    global Pname
    if not values['property']:
        sg.popup('Please choose the property you want to update comments for!')
    else:
        prop = values['property'][0]
        PID = prop[0]
        Pname = prop[1]
        window.close()
        window = admin_update_comments()

def button_admin_delete_comment(values):
    global window
    if not values['comment']:
        sg.popup('Please choose the comment you want to delete!')
    else:
        comment = values['comment'][0]
        EID = comment[0]
        cmnt = comment[1]
        cur.execute('DELETE FROM Evaluation WHERE EID=?', (EID,))
        sg.popup(f'The comment ({cmnt}) has been deleted!')
        
def button_admin_update_rating(values):
    global window
    global PID
    global Pname
    if not values['property']:
        sg.popup('Please choose the property you want to change rating for!')
    else:
        prop = values['property'][0]
        PID = prop[0]
        Pname = prop[1]
        window.close()
        window = admin_update_rating()
    
def button_admin_enter_rating(values):
    global window
    global PID
    if not values['rating']:
        sg.popup('Please enter the new rating for this property!')
    else:
        rating = values['rating']
        try:
            rating = float(rating)
            if rating>=1 and rating<=5:
                cur.execute('UPDATE Property SET Rating=? WHERE PID=?', (rating, PID))
                sg.popup(f'The rating of this property has been updated to {rating}')
            else:
                sg.popup('The rating must be betwee 1 and 5 inclusive!')
        except:
            sg.popup('The rating must be numeric!')
            

# Owner

# Initialize important variables
Name = ''
SSN = ''
PID = ''
#  Windows
def owner_login():
    layout = [[sg.Text('Please enter your information below')],
              [sg.Text('ID:', size =(10,1)), sg.Input(size = (10,1), key='id')],
              [sg.Text('Password', size =(10,1)), sg.Input(size = (10,1), key='password')],
              [sg.Button('Log in'), sg.Button('Return to Main Page')]]
    return sg.Window('Owner Window', layout)

def owner_main():
    global Name 
    global SSN
    properties = []
    for row in cur.execute('''SELECT PID, Pname, City, Address, Ptype
                          FROM Property WHERE Owner_ID=?''',(SSN,)):
        properties.append(row)  
    layout = [[sg.Text(f'Welcome {Name}! Below are your properties with their necessary information.')],
              [sg.Listbox(properties, size=(50,10), key='property')],
              [sg.Text('Press Check to see the customers who booked this property with their relative duration.')],
              [sg.Button('Check')],
              [sg.Text('Press Add to add an a new property'), sg.Button('Add a Property')],
              [sg.Text('Press Delete to remove the chosen property!'), sg.Button('Delete')],
              [sg.Text('Press Update to update the information for the chosen property'), sg.Button('Update')],
              [sg.Button('Log Off')]]
    return sg.Window('Main Page', layout)

def owner_books():
    global PID
    books = []
    for row in cur.execute('''SELECT B.BookID, U.Name, B.dfrom, B.dto, B.tprice
                              FROM Books B, Property P, User U
                              WHERE U.SSN=B.Customer_ID AND P.PID=B.PID AND P.PID=?''',(PID,)):
        books.append(row)
    layout = [[sg.Text('Below are all the books with their duration and the name of the cutomer.')],
               [sg.Listbox(books, size=(50,10), key='book')],
               [sg.Button('back')]]
    return sg.Window('Books Page', layout)

def owner_add():
    types = ('Private', 'Shared')
    layout = [[sg.Text('Enter the below information to add a new property of your own.')],
              [sg.Text('Enter the Name of the property:'), sg.Input(size = (10,1), key='name')],
              [sg.Text('Enter a Description:'), sg.Input(size = (10,1), key='description')],
              [sg.Text('Enter the capacity:'), sg.Input(size = (10,1), key='capacity')],
              [sg.Text('Enter the price in $:'), sg.Input(size = (10,1), key='price')],
              [sg.Text('Enter the address:'), sg.Input(size = (10,1), key='address')],
              [sg.Text('Enter the city:'), sg.Input(size = (10,1), key='city')],
              [sg.Text('Enter the district:'), sg.Input(size = (10,1), key='district')],
              [sg.Text('Enter the type:'), sg.Combo(types, size=(15, 2), key='type')],
              [sg.Button('Add'), sg.Button('back')]]
    return sg.Window('New Property', layout)

def owner_update():
    global PID
    time_slots = []
    for row in cur.execute('''SELECT AID, afrom, ato, marks
                            FROM HasAvailability 
                            WHERE PID=?''' ,(PID,)):
        time_slots.append(row)
    marks = ('available', 'not available')
    layout = [[sg.Text('Choose the time slot and change its availability.')],
              [sg.Listbox(time_slots, size=(50,10), key='slot')],
              [sg.Combo(marks, size=(15, 2), key='mark'), sg.Button('Mark')],
              [sg.Button('back')]]
    return sg.Window('Update Information', layout)
    


# Buttons

def button_owner_login(values): 
    global window
    global Name
    global SSN
    L = []
    for row in cur.execute('SELECT U.SSN FROM User U, Owner O WHERE U.SSN=O.SSN'):
        L.append(str(row[0]))
    if values['id'] and values['password']:
        if values['id'] in L:
            p = []
            for row in cur.execute('SELECT Password FROM User WHERE SSN=?', (values['id'],)):
                p.append(row[0])
            password = p[0]
            if values['password'] != password:
                sg.popup('Wrong ID or Password!')
            if values['password'] == password:
                for row in cur.execute('SELECT Name FROM User WHERE SSN=?',(values['id'],)):
                    Name = row[0]
                SSN = values['id']
                window.close()
                window = owner_main()
        if values['id'] not in L:
            sg.popup('You have to create an account first!') 
    else:
        sg.popup('ID or Password cannot be empty!')


def button_owner_check(values):
    global window
    global PID
    if not values['property']:
        sg.popup('Please choose a property to check information for!')
    else:
        prop = values['property'][0]
        PID = prop[0]
        window.close()
        window = owner_books()


def button_owner_add(values):
    global window 
    global SSN
    if not values['name'] or not values['capacity'] or not values['description'] or not values['price'] or not values['address'] or not values['city'] or not values['district'] or not values['type']:
        sg.popup('You have to fill every box with the necessary information!')
    else:
        if values['capacity'].isdigit() and values['price'].isnumeric():
            if float(values['capacity'])>=0 and float(values['price']):
                ID = []
                for row in cur.execute('SELECT MAX(PID) FROM Property'):
                    ID.append(row[0])
                ID = ID[0]+1
                new_property = (ID,values['name'],values['description'],int(values['capacity']),int(SSN),float(values['price']),values['address'],values['city'],values['district'],values['type'],)
                cur.execute('''INSERT INTO Property (PID,Pname,Description,Capacity,Owner_ID,Nprice,Address,City,District,Ptype)
                            VALUES(?,?,?,?,?,?,?,?,?,?)''',new_property)
                sg.popup('You have inserted a new property!')
            else:
                sg.popup('You have entered a non-acceptable value for the capacity or the price!')
        else:
            sg.popup('You have entered a non-acceptable value for the capacity or the price!')
            

def button_owner_delete(values):
    global window
    if not values['property']:
        sg.popup('Please choose a property to delete!')
    else:
        prop = values['property'][0]
        PID = prop[0]
        name = prop[1]
        cur.execute('DELETE FROM Property WHERE PID=?', (PID,))
        sg.popup(f'You have successfully deleted the property with the name {name}!')


def button_owner_update(values):
    global window
    global PID
    if not values['property']:
        sg.popup('Please choose a property to update information for!')
    else:
        prop = values['property'][0]
        PID = prop[0]
        window.close()
        window = owner_update()

def button_owner_mark(values):
    global window
    if not values['slot'] and values['mark']:
        sg.popup('Please choose a time slot you want to update its availability!')
    elif values['slot'] and not values['mark']:
        sg.popup('Please choose the availability status for the chosen time slot!')
    elif not values['slot'] and not values['mark']:
        sg.popup('Please choose a time slot and its new availability status!')
    else:
        slot = values['slot'][0]
        AID = slot[0]
        cur.execute('UPDATE HasAvailability SET marks=? WHERE AID=?', (values['mark'],AID))
        sg.popup('You have successfully update the availability status for this property!')
        
# Open the First Window
window = Main()
while True:
    event, values = window.read()
    if event=='OK':
        Button_ChooseRole(values)
    elif event=='Login':
        Button_customer_login(values)
    elif event == 'Return to Main Page':
        window.close()
        window = Main()
    elif event=='List Properties':
        Button_list_properties(values)
    elif event=='Continue':
        Button_Continue(values)
    elif event=='Check Rating and Reviews':
        Button_check_reviews(values)
    elif event=='Rate your previous books':
        Button_previous_books(values)
    elif event=='Give Rating':
        Button_give_rating(values)
    elif event=='Log Out':
        window.close()
        window = customer_login()
    elif event=='Enter':
        Button_leave_comment(values)
    elif event == 'Choose another property' or event == 'Go to previous page' or event == 'Cancel':
        window.close()
        window = list_properties()
    elif event == 'continue':
        Button_continue(values)
    elif event == 'Proceed to payment':
        Button_proceed_to_payment(values)
    elif event == 'Yes':
        Button_complete()
    elif event=='login':
        button_admin_login(values)
    elif event=='Return to Main Page':
        window.close()
        window = Main()
    elif event=='Check Availability':
        button_admin_availability(values)
    elif event=='Back':
        window.close()
        window = admin_main()
    elif event=='Update Comments':
        button_admin_update_comments(values)
    elif event=='Delete Comment':
        button_admin_delete_comment(values)
    elif event=='Change Rating':
        button_admin_update_rating(values)
    elif event=='Enter Rating':
        button_admin_enter_rating(values)
    elif event=='Log in':
        button_owner_login(values)
    elif event=='Return to Main Page':
        window.close()
        window = Main()
    elif event=='Check':
        button_owner_check(values)
    elif event=='Add a Property':
        window.close()
        window = owner_add()
    elif event=='Add':
        button_owner_add(values)
    elif event=='Delete':
        button_owner_delete(values)
    elif event=='Update':
        button_owner_update(values)
    elif event=='Mark':
        button_owner_mark(values)
    elif event=='back':
        window.close()
        window = owner_main()
    elif event=='Log Off':
        window.close()
        window = owner_login()
    elif event == sg.WIN_CLOSED:
        break

window.close()
con.commit()
con.close()


