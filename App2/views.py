from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import *
import random
from django.contrib.auth import logout


 
import random
import smtplib
from email.message import EmailMessage
otp_list=[]

 

def register(request):
    course = Course.objects.all()
    return render(request,'register.html',{'course':course})

def home(request):
    itms = Course.objects.all()
    return render(request, 'ind1.html',{'itms':itms})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def msg(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        msg = request.POST.get('msg')
        m=Contact_data(fullname=name,email=email,msg=msg)
        m.save()
        return redirect('/login/')
    return render(request,'contact.html',{'msg':"Email already Exists!",})

def usrpage(request):
    usercourse = cart.objects.all()
    dbcourse = Course.objects.all()
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        mail = request.POST.get('gmail')
        mobile = request.POST.get('mobile')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        edu = request.POST.get('edu')
        course_data = request.POST.get('course')
        usr = request.POST.get('usrname')
        pswd = request.POST.get('password')
        en = usrData(fname=fname, lname=lname,email=mail,mobile=mobile,gender=gender,address=address,edu=edu,cors=course_data,usr=usr,pswd=pswd)
        en.save()
        return redirect('/login/')
    pass
    return render(request,'ind1.html')

def login(request):
    usrs = usrData.objects.all()
    usr=request.POST.get('username')
    pswd=request.POST.get('pswd')
 
    try:
        usr = usrData.objects.get(usr=request.POST.get('username'),pswd=request.POST.get('pswd'))
        request.session['usr']=usr.usr   

        return redirect('/otp/')
    except Exception as e:
        pass
    return render(request,'login.html',{'msg1':"Login Failed"})



def uotp(request):
    usr = request.session['usr']
    r = usrData.objects.get(usr=usr)
    otp_list.clear()
    otp = random.randint(10000,99999)
    otp_list.append(otp)
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login('bashamasthan31@gmail.com','dygq eorh yspf jhbx')  # Change the details...
    msg = EmailMessage()
    msg['From'] = 'EDU Pro Solutions'
    msg['Subject'] = 'Registration OTP Code'
    msg.set_content(f"Your One Time Password is: {otp} \n Thank you for Choosing Our Platform to Improve Your Knowledge")
    msg['To'] = r.email
    server.send_message(msg) 

    print(otp)
    return render(request,'log_auth.html') 

def Auth_otp(request):
    otp=otp_list[0]
    
    if request.method=="POST":
        otp_entered = request.POST.get('uotp')
        if int(otp_entered)==int(otp):                          
            return redirect('/usrp')
        else:
            return render(request,'log_auth.html',{'msg2':"Invalid OTP"})
    return redirect('/login/')


def usrp(request):
    user = request.session['usr']
    usrs = usrData.objects.get(usr=user)
    r=Course.objects.get(name=usrs.cors)
    return render(request,'usrp.html',{'user':usrs,'course': r})


def usredit(request):
    users = usrData.objects.all()


    # if request.method == 'POST':
        # user = request.POST.get('user')
        # fname = request.POST.get('fname')
        # lname = request.POST.get('lname')
        # mail = request.POST.get('gmail')
        # mobile = request.POST.get('mobile')
        # gender = request.POST.get('gender')
        # address = request.POST.get('address')
        # edu = request.POST.get('edu')
        # pswd = request.POST.get('password')

        # try:
        #     usr = usrData.objects.get(email=mail)
        # except usrData.DoesNotExist:
        #     return redirect('/usredit/')
        # usr.fname = fname
        # usr.lname = lname
        # usr.email = mail
        # usr.mobile = mobile
        # usr.gender = gender
        # usr.address = address
        # usr.edu = edu
        # usr.pswd = pswd
        # usr.update()
        # return redirect('/usrp/')


    return render(request,'usredit.html')



def usr_cart(request):
    # cart = cart.objects.get(usrid=request.POST.get('usrid'))
    itms = Course.objects.all()
    if request.method == 'POST':
        usrid = request.POST.get('user_id')
        usr = usrData.objects.get(email=usrid)
        return render(request,'usrcart.html',{'user':usr,'itms': itms,'cart':cart})

    return render(request,'usrp.html')


def usrcart_add(request):
    itms = Course.objects.all()
    usrs = usrData.objects.all()
    carts = cart.objects.all()
    if request.method == 'POST':
        usrid = request.POST.get('usrid')
        course = request.POST.get('cname')
        r= Course.objects.get(name=course)
        k=usrData.objects.get(id=usrid)
        d= cart(usrid=k.id,course=course)
        d.save()
        return HttpResponse("Course Added")
    return redirect('/cart/')
    
def logout_1(request):
    # logout(request)
    return redirect('/login/') 

def payment(request):
    user = request.session['usr']
    usrs = usrData.objects.get(usr=user)
    r=Course.objects.get(name=usrs.cors)
    rr = r.name
    return render(request,'payment.html',{'course':rr})


def usrgd(request):
    user = request.session['usr']
    usrs = usrData.objects.get(usr=user)
    r=Course.objects.get(name=usrs.cors)
    rr = r.name
    return render(request,'usrgd.html',{'user':usrs,'course': r})

def delcard(request):
    carts = cart.objects.get(course=request.POST.get('cname'))

    carts.delete()
    return HttpResponse("Card Deleted")

def adminpage(request):
    users = usrData.objects.all()
    courses = Course.objects.all()

    
    return render(request,'admin/dashboard.html',{'users': users,'course': courses,'k':0})

def mb_course(request):
    users = usrData.objects.all()
    courses = Course.objects.all()
    return render(request,'admin/mb_course.html',{'users': users,'course': courses})


def mb_users(request):
    users = usrData.objects.all()
    courses = Course.objects.all()
    return render(request,'admin/mb_user.html',{'users': users,'course': courses})


def modify(request):
    operation=request.GET['operation']
    name=request.GET['name']
    username=request.GET['username']
    password=request.GET['password']
    gender=request.GET['gender']
    mobile=request.GET['mobile']
    email=request.GET['email']
    desig=request.GET['desig']
    course=request.GET['course']
    graduation=request.GET['graduation']
    address=request.GET['address']
    pincode=request.GET['pincode']
    r=usrData.objects.get(email=email)
    if operation=="update":
        r.name=name
        r.username=username
        r.password=password
        r.gender=gender
        r.mobile=mobile
        r.email=email
        r.desig=desig
        r.course=course
        r.graduation=graduation
        r.address=address
        r.pincode=pincode
        r.save()
    else:
        usrData.delete(r)
    users=usrData.objects.all()
    return render(request,'admin/mb_user.html',{"users":users})

def viewusers(request):
    users=usrData.objects.all()
    return render(request,'admin/mb_user.html',{"users":users})

def msgs(request):
    ms = Contact_data.objects.all()
    return render(request,'admin/usr_msg.html',{'msgs': ms})

