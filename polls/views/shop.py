from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from qypt.models import shop
from qypt.models import shopimg
from qypt.models import shop_type1
from qypt.models import shop_type2
from qypt.models import shop_type3
from PIL import Image
import time
import os
import random
import urllib.request
import urllib.parse
import ssl


def shopList(request):
    if not isLogin(request):
        return redirect('/qypt/login')
    session = request.session
    admintel = session['tel']
    list = shop.objects.filter(admintel=admintel)
    # item = shopitem.objects.filter(id=itemid).first()
    # lists = shop.Student.objects.filter(teacher__name='李老师')
    return render(request, 'Xadmin/shop-list.html', {"list": list})


# 添加店面
def shopAdd(request):
    if not isLogin(request):
        return redirect('/qypt/login')
    session = request.session
    if isLogin(request):
        admintel = session['tel']
        # shopType1 = shop_type1.objects.all()
        shopType2 = shop_type2.objects.all()
        shopType2Len = shopType2.__len__()
        print(shopType2Len)
        shopType3 = shop_type3.objects.all()
        for i in shopType3:
            print(i.name + str(i.shop_type2_id))
        param1 = {"adminName": session['name'], "admintel": admintel, "shopType2": shopType2, 'shopType3': shopType3,"shopType2Len": shopType2Len}
        templateUrl = 'Xadmin/shop-add.html'

        return render(request, templateUrl, param1)
    else:
        return render(request, 'Xadmin/login.html')


# 处理添加店面信息
def shopAddOK(request):
    if request.method == 'GET':
        return HttpResponse("参数非法")
    admintel = request.POST.get('admintel')
    if request.method == 'GET':
        return HttpResponse("no files for upload!")
    randomFileName = getRandomFileName() + '.jpg'
    name = request.POST.get('name')
    info = request.POST.get('info')
    addr = request.POST.get('addr')
    tel1 = request.POST.get('tel1')
    tel2 = request.POST.get('tel2')
    tel3 = request.POST.get('tel3')
    lng = request.POST.get('lng')
    lat = request.POST.get('lat')
    shop_type1_obj = shop_type1.objects.get(id=1)
    shop_type2_id = request.POST.get('shop_type2')
    shop_type2_obj = shop_type2.objects.get(id=shop_type2_id)
    shop_type3_id = request.POST.get('shop_type3')
    shop_type3_obj = shop_type3.objects.get(id=shop_type3_id)
    headimg = request.FILES.get("headimg", None)
    # print(name, info, addr, tel1, tel2, tel3, lng, lat, shop_type2_id, shop_type3_id)
    # 存入headimg
    fullName = "/home/rcproject/qypt/static/upload/shopimg/logo/"+randomFileName
    destination = open(os.path.join("/home/rcproject/qypt/static/upload/shopimg/logo/", randomFileName),
                       'wb+')  # 打开特定的文件进行二进制的写操作

    for chunk in headimg.chunks():
        destination.write(chunk)
    destination.close()
    imgurl = "logo/" + randomFileName
    newshopimg = shopimg(imgurl=imgurl)
    newshopimg.save()
    headimgid = newshopimg.id
    print(11223)
    newshop = shop(name=name, admintel=admintel, info=info, addr=addr, tel1=tel1, tel2=tel2, tel3=tel3,
                   headimg=headimgid,
                   lng=lng, lat=lat, shop_type1=shop_type1_obj, shop_type2=shop_type2_obj, shop_type3=shop_type3_obj, is_active=1)
    newshop.save()
    currentShopImg = shopimg.objects.get(id=headimgid)
    currentShopImg.shop = newshop
    currentShopImg.save()

    fnCompressPic("", fullName)
    # image_url = models.URLField()
    # return render(request, 'Xadmin/shop-list.html')
    return redirect('/qypt/closeSavePage')


def shopEdit(request):
    session = request.session
    admintel = session['tel']
    shopid = request.GET.get('shopid')
    shopobj = shop.objects.get(id=shopid)
    print(shopobj.headimg)
    headimgid = shopobj.headimg
    headimgUrl = shopimg.objects.get(id=headimgid).imgurl
    shopType2 = shop_type2.objects.all()
    shopType3 = shop_type3.objects.all()
    return render(request, 'Xadmin/shop-edit.html',
                  {"shopid": shopid, "shopobj": shopobj, "shopType2": shopType2, 'shopType3': shopType3,
                   'admintel': admintel, 'headimgUrl': headimgUrl})


def shopEditOK(request):
    if request.method == 'GET':
        return HttpResponse("参数非法")
    admintel = request.POST.get('admintel')
    shopid = request.POST.get('shopid')
    # 如果isImgChanged=0，则代表店铺头图没有变化
    isImgChanged = request.POST.get('isImgChanged')
    if request.method == 'GET':
        return HttpResponse("no files for upload!")
    name = request.POST.get('name')
    info = request.POST.get('info')
    addr = request.POST.get('addr')
    tel1 = request.POST.get('tel1')
    tel2 = request.POST.get('tel2')
    tel3 = request.POST.get('tel3')
    lat = request.POST.get('lat')
    lng = request.POST.get('lng')
    shop_type1_obj = shop_type1.objects.get(id=1)
    shop_type2_id = request.POST.get('shop_type2')
    shop_type2_obj = shop_type2.objects.get(id=shop_type2_id)
    shop_type3_id = request.POST.get('shop_type3')
    shop_type3_obj = shop_type3.objects.get(id=shop_type3_id)
    headimg = request.FILES.get("headimg", None)
    #如果头图有变化则更新图片
    if int(isImgChanged) > 0:
        # 存入headimg
        filePath = "/home/rcproject/qypt/static/upload/shopimg/logo/"
        randomFileName = getRandomFileName() + '.jpg'
        destination = open(os.path.join(filePath, randomFileName), 'wb+')  # 打开特定的文件进行二进制的写操作
        for chunk in headimg.chunks():
            destination.write(chunk)
        destination.close()
        imgurl = "logo/" + randomFileName
        newshopimg = shopimg(imgurl=imgurl)
        newshopimg.save()
        headimg = newshopimg.id
        # 存入完成
        shop.objects.filter(id=shopid).update(name=name, admintel=admintel, info=info, addr=addr, tel1=tel1, tel2=tel2,
                                              tel3=tel3, headimg=headimg,
                                              lng=lng, lat=lat, shop_type1=shop_type1_obj, shop_type2=shop_type2_obj,
                                              shop_type3=shop_type3_obj)
        fnCompressPic(filePath, randomFileName)
    #否则不更新头图
    else:
        shop.objects.filter(id=shopid).update(name=name, admintel=admintel, info=info, addr=addr, tel1=tel1, tel2=tel2,
                                              tel3=tel3,
                                              lng=lng, lat=lat, shop_type1=shop_type1_obj, shop_type2=shop_type2_obj,
                                              shop_type3=shop_type3_obj)
    return redirect('/qypt/closeUpdatePage')


#保存成功
def closeSavePage(request):
    if not isLogin(request):
        return redirect('/qypt/login')
    return render(request, 'Xadmin/closeSavePage.html')


#更新成功
def closeUpdatePage(request):
    if not isLogin(request):
        return redirect('/qypt/login')
    return render(request, 'Xadmin/closeUpdatePage.html')



def getShopAddr(request):
    lat = request.POST.get('lat')
    lng = request.POST.get('lng')
    return HttpResponse(getAddr(lat, lng))

# 判断是否登陆函数,templateUrl:要渲染的模板url
def isLoginpre(request, templateUrl, param1={}):
    # 拿到cookie对应的随机码，来查找session里的is_login字段是否True，如果通过则表示通过
    if request.session.get('is_login', None):
        return render(request, templateUrl, param1)
    else:
        return render(request, 'Xadmin/login.html')


def reverseShopStatus(request):
    shopid = request.POST.get('id')
    shopobj = shop.objects.get(id=shopid)
    flag = shopobj.is_active
    if flag == 1:
        val = 0
    else:
        val = 1
    # val = 0 if (flag == 1) else 1
    shopobj.is_active = val
    shopobj.save()
    return HttpResponse(1)

def isLogin(request):
    # 拿到cookie对应的随机码，来查找session里的is_login字段是否True，如果通过则表示通过
    if request.session.get('is_login', None):
        return True
    else:
        return False
        # return render(request, 'Xadmin/login.html')


# 生成随机的文件名
def getRandomFileName():
    timeNow = time.strftime("%Y%m%d%H%M%S", time.localtime())
    # timeNow = str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
    randomFileName = ''.join(random.sample(
        ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e',
         'd', 'c', 'b', 'a'], 8))
    return timeNow + randomFileName


# 生成随机的多个文件名
# 待完成
def getRandomFileNames(files):
    tmpList = [];
    timeNow = time.strftime("%Y%m%d%H%M%S", time.localtime())
    # timeNow = str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
    randomFileName = ''.join(random.sample(
        ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e',
         'd', 'c', 'b', 'a'], 8))
    return timeNow + randomFileName



#图片压缩函数
def fnCompressPic(fpath,fName):
    fpath = fpath
    file = fpath + fName
    img = Image.open(file)
    print(img.size[0])
    # return
    if img.size[0] > 800:
        basewidth = 800
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        img.save(file)


#反向获取地址商户(经纬度换取地址)
def getAddr(lat,lng):
    url = "https://apis.map.qq.com/ws/geocoder/v1/?location={},{}&key=6VBBZ-S2OW4-KJQU3-DXLV7-FV64J-75BDP&get_poi=1".format(lat,lng)
    # url = 'https://apis.map.qq.com/ws/geocoder/v1/?location=39.984154,116.307490&key=6VBBZ-S2OW4-KJQU3-DXLV7-FV64J-75BDP&get_poi=1'
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(url, context=context) as response:
        return response.read()
