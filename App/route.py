import select

from . import app, db
from . import urls
import os
url = urls.url
from flask import render_template, session, request, redirect, url_for, flash

def _login(session):
    session['logined'] = True

def check_login(session):
    logined = session.get('logined')
    if logined != None:
        if logined == True:
            return True
    else:
        return False

@app.route(url['index'][0])
def index():
    logined = check_login(session)
    return render_template('home.html',title=None,logined=logined,session=session,username=session.get('username'),photo=session.get('photo'))

@app.route(url['login'],methods=['POST','GET'])
def login():
    login = request.args.get('login')
    if login != None:
        password = request.args.get('password')
        if password != None:
            outpud = db.check_user(login,password,session)
            if outpud == True:
                session['logined'] = True
                flash('Вы вошли в аккаунт',category='success')
                return redirect('/')
            else:
                flash(outpud,category='error')
                return render_template('accounts/login.html',title='Логин')
        else:
            return render_template('accounts/login.html',title='Логин')
    else:
        return render_template('accounts/login.html',title='Логин')
@app.route(url['logout'])
def logout():
    if session.get('logined') != True:
        flash('Вы не залогинены',category='error')
    else:
        flash('Вы вышли из аккаунта',category='success')
    session['logined'] = False
    return redirect('/')

@app.route(url['registr'],methods=['POST','GET'])
def registr():
    login = str(request.args.get('login'))
    username = str(request.args.get('username'))
    if login != 'None' or username != 'None':
        password = str(request.args.get('password'))
        if password != 'None':
            outpud = db.add_user(username,login,password,session)
            if outpud == True:
                _next = request.args.get('next')
                if _next != None:
                    session['logined'] = True
                    return redirect(_next)
                else:
                    session['logined'] = True
                    flash('Вы зарегестрированны',category='success')
                    return redirect('/')
            else:
                flash(outpud,category='error')
                return render_template('accounts/registr.html',title='Регистрация')
        else:
            return render_template('accounts/registr.html',title='Регистрация')
    else:
        return render_template('accounts/registr.html',title='Регистрация')

@app.route('/user/<username>')
def user(username):
    logined = check_login(session)
    return render_template('accounts/user.html',title=username,user=username,username=session.get('username'),logined=check_login(session))

@app.route(url['forum']['index'])
def forum():
    logined = check_login(session)
    posts = db.get_all_post()
    link = '/forum/post/'
    return render_template('forum/forum.html',title='Форум',logined=logined,session=session,
                           username=session.get('username'),posts=posts,link=link)

@app.route(url['forum']['post'])
def post(postid):
    logined = check_login(session)
    output = db.view_post(postid)
    if output[0] == True:
        if db.get_post_autor(postid) == session.get('id'):
            autor = True
        else:
            autor = False
        if check_login(session) == True:
            db.add_view(session['id'],postid)
        post = output[1]
        link = f'/forum/edit/{postid}/'
        return render_template('forum/forum_post.html',title='Форум',name=post[0],body=post[1],views=post[2],
                               logined=logined,session=session,username=session.get('username'),autor=autor,link=link)
    else:
        flash(output[0],category='error')
        return redirect(url['forum']['index'])

@app.route(url['forum']['create'],methods=['GET','POST'])
def create_post():
    logined = check_login(session)
    if session.get('logined') == True:
        if str(request.args.get('name')) != 'None':
            if str(request.args.get('body')) != 'None':
                _id = session.get('id')
                output = db.add_post(_id,request.args['name'],request.args['body'])
                if output == True:
                    link = f'{urls.host}forum/post/{_id}/'
                    flash(f'Пост создан по ссылке {link}',category='success')
                else:
                    flash(output,category='error')
        return render_template('forum/add_post.html', title='Создание поста',name_value='',body_value='',
                               logined=logined,session=session,username=session.get('username'),use='/forum/create/')
    else:
        flash('Вы не залогинены',category='error')
        return redirect(url['login'])

@app.route(url['forum']['edit'],methods=['GET','POST'])
def edit_post(postid):
    logined = check_login(session)
    if session.get('logined') == True:
        if db.get_post_autor(postid) == session.get('id'):
            output = db.view_post(postid)
            if output[0] == True:
                if output[1][0] != request.args.get('name') != None or output[1][1] != request.args.get('body') != None:
                    output = db.edit_post(postid,request.args.get('name'),request.args.get('body'))
                    if output == True:
                        flash('Пост отредактирован',category='success')
                    else:
                        flash(output,category='error')
                    link = f'{urls.host}forum/post/{postid}/'
                    return redirect(link)
                name_value = output[1][0]
                body_value = output[1][1]
                return render_template('forum/add_post.html', title='Редактирование поста',use=f'/forum/edit/{postid}/',
                                       name_value=name_value,body_value=body_value,logined=logined,session=session,username=session.get('username'))
            else:
                flash(output[0], category='error')
                return redirect(url['forum']['index'])
        else:
            flash('Вы не являетесь создателем поста',category='error')
            return redirect('/')
    else:
        flash('Вы не залогинены',category='error')
        return redirect(url['login'])

@app.route('/test/',methods=['POST','GET'])
def test():
    return render_template('test.html')