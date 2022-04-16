import sqlite3
import shutil
import hashlib
from datetime import datetime

block = {
    'symbols': [],
    'texts': []
}

def block_check(text):
    if len(block['symbols'])+len(block['texts']) >= 1:
        for i in block['symbols']:
            if i in text:
                return False
                break
            else:
                for i in block['texts']:
                    if i in text:
                        return False
                        break
                    else:
                        return True
    else:
        return True

class DB():
    def __init__(self,db_name):
        self.db_name = db_name
        self.db = sqlite3.connect(db_name,check_same_thread=False)
        self.cur = self.db.cursor()
        self.hash = hashlib.md5

    def log(self,_type,execute):
        add_log = (datetime.now(),_type,execute)
        self.cur.execute(f'INSERT INTO log (time,type,execute) VALUES (?,?,?)',add_log)
        self.db.commit()

    def new_id(self,_type=1):
        if _type == 1:
            chall=self.cur.execute('SELECT id FROM user').fetchall()
        elif _type == 2:
            chall=self.cur.execute('SELECT id FROM post').fetchall()
        if chall == []:
            return 0
        else:
            return chall[len(chall)-1][0]+1

    def add_user(self,username,login,password,session):
        if block_check(login):
            if block_check(password):
                password_utf = password.encode(encoding='UTF-8', errors='strict')
                password_hash = self.hash(password_utf).hexdigest()
                chall=self.cur.execute('SELECT login FROM user WHERE login=?',(login,)).fetchall()
                if chall == []:
                    _id = self.new_id()
                    self.cur.execute('INSERT INTO user (id,login,password,username,regtime) VALUES (?,?,?,?,?)',(_id,login,str(password_hash),str(username),str(datetime.now())))
                    self.db.commit()
                    session['username'] = username
                    session['id'] = _id
                    return True
                else:
                    return 'Логин уже существует'
            else:
                return 'Запрещённый пороль'
        else:
            return 'Запрещённый логин'

    def check_user(self,login,password,session):
        if block_check(login):
            if block_check(password):
                password_utf = password.encode(encoding='UTF-8', errors='strict')
                password_hash = self.hash(password_utf).hexdigest()
                chall=self.cur.execute('SELECT id,password,username FROM user WHERE login=?',(login,)).fetchall()
                if chall == []:
                    return 'Не правельный логин или пороль'
                else:
                    db_id = chall[0][0]
                    db_password = chall[0][1]
                    db_username = chall[0][2]
                    if password_hash == db_password:
                        session['username'] = db_username
                        session['id'] = db_id
                        return True
                    else:
                        return 'Не правельный пороль'
            else:
                return 'Запрещённый пороль'
        else:
            return 'Запрещённый логин'

    def get_post_autor(self, postid):
        return self.cur.execute('SELECT autorid FROM post WHERE id=?',(postid,)).fetchall()[0][0]


    def add_post(self,autorid,name,body):
        if block_check(name):
            if block_check(body):
                chall=self.cur.execute('SELECT name FROM post WHERE autorid=? and name=?',(autorid,name)).fetchall()
                if chall != []:
                    return 'У вас уже есть пост с данным названием'
                else:
                    self.cur.execute('INSERT INTO post (id,autorid,name,body,createtime) VALUES (?,?,?,?,?)',(self.new_id(2),autorid,name,body,datetime.now()))
                    self.db.commit()
                    return True
            else:
                return 'Запрещённое содержание'
        else:
            return 'Запрещённое имя'

    def edit_post(self,postid,name,body):
        if block_check(name):
            if block_check(body):
                output=self.view_post(postid)
                if output[0] == True:
                    self.cur.execute('UPDATE post SET name = ? WHERE id = ?',(name,postid))
                    self.cur.execute('UPDATE post SET body = ? WHERE id = ?',(body,postid))
                    self.db.commit()
                    return True
                else:
                    return output
            else:
                return 'Запрещённое содержание'
        else:
            return 'Запрещённое имя'

    def view_post(self,postid):
        chall=self.cur.execute('SELECT name,body,views FROM post WHERE id=?',(postid,)).fetchall()
        if chall == []:
            return ['Такого поста не существует']
        else:
            return [True,[chall[0][0],chall[0][1],chall[0][2]]]

    def add_view(self,userid,postid):
        chall=self.cur.execute('SELECT * FROM view_debug WHERE userid=? AND postid=?',(userid,postid)).fetchall()
        if chall == []:
            views=self.cur.execute('SELECT views FROM post WHERE id=?',(postid,)).fetchall()[0][0]
            views+=1
            self.cur.execute('INSERT INTO view_debug (userid,postid) VALUES (?,?)', (userid,postid))
            self.cur.execute('UPDATE post SET views=?', (views,))
            self.db.commit()

    def get_all_post(self):
        return self.cur.execute('SELECT id,name FROM post').fetchall()