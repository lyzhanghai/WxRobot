from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from wxpy import *
from threading import Thread, Event
from wxRobot import consumers
import os
import base64
import json
import time
from initialize import helper
from helper.channels_manager import cm
from helper.bot_manager import robot_management as rm
from helper.debug import debug
# from homepage.helper import aom
from databases import models
# 机器人线程


class BotThread(Thread):
    '''
        作用：用于生成一个机器人实例
        e_qrcode：二维码的标志位
        e_login：登录状态的标志位
    '''

    def __init__(self, e_qrcode, request):
        super().__init__()
        self.e_qrcode = e_qrcode
        self.qrcode = None
        self.bot_status = True
        self.bot = None  # 默认为True
        # self.username = username
        self.e_bot = Event()  # 获取标志位
        self.request = request
        # self.bot = None

    def run(self):
        # 构建机器人对象
        # self.bot = Bot(qr_callback=self.qr_callback,login_callback=self.login_callback)
        try:
            # 实例化一个机器人
            self.bot = Bot(qr_callback=self.qr_callback,
                           login_callback=self.login_callback, logout_callback=self.logout_callback)
            # 开启puid缓存
            self.bot.enable_puid('wxpy_puid.pkl')
            self.e_bot.set()
            username = self.request.session.get('username')
            print("用户名为：", username)

            # 获取初始化的微信头像和名称以及puid
            data, puid = self.bot_puid(self.bot)
            # 添加到登录成功字典里
            rm.add_bot(puid,self.bot,username)
            
        except KeyError as e:
            username = self.request.session['user'].get('username')
            cm.reply_channel_send(username,{
                    'init_status': False,
                    'error': '该微信账号已被限制登录网页微信，请更换微信号后再试',
                })
            print("error:", e)
            debug.print_l('该微信账号已被限制登录网页微信，请更换微信号后再试')
            # self.bot_status = False

    # 二维码获取成功后的回调函数
    def qr_callback(self, uuid, status, qrcode):
        # debug.print_l('二维码刷新成功')
        # print("ic.channels",ic.channels)
        # bytest格式的二维码数据流
        self.qrcode = qrcode
        self.uuid = uuid
        # set二维码标志位
        self.e_qrcode.set()
        # try:
        #     channel = ic.get_channels(self.username)
        #     channel.reply_channel.send({
        #         'text': json.dumps({
        #             'qrcode': base64.b64encode(qrcode).decode()
        #         })
        #     })
        # except:
        #     pass

    # 微信在退出时调用

    def logout_callback(self):
        pass
        # puid = self.bot.puid
        # print(puid)
        # if puid:
        #     wechat_id = models.WechatId.objects.filter(puid=puid).all()
        #     if len(list(wechat_id)):
        #         print('将%s从数据清理成功' % puid)
        #         wechat_id.delete()
        #         return
        # print('将%s从数据清理失败' % puid)

    def bot_puid(self, bot):
        user_details = bot.user_details(bot.self)
        data = {
            # 微信名称
            'user_name': user_details.name,
            # 微信头像
            'avatar_bytes': base64.b64encode(
                user_details.get_avatar()).decode()
        }
        # 获取puid身份标识符
        puid = bot.user_details(bot.self).puid
        return data, puid

    #  登录成功后的回调函数
    def login_callback(self, **kwargs):
        self.e_bot.clear()
       
        def go_to_mainpage():
            # 等待bot被创建
            self.e_bot.wait()
            username = self.request.session.get('username')
            print("用户名为：", username)

            # 获取初始化的微信头像和名称以及puid
            data, puid = self.bot_puid(self.bot)
            # 添加到登录成功字典里
            rm.add_bot(puid,self.bot,username)
            # time.sleep(3)
            # 查找当前帐号下所绑定的微信号
            user = models.UserInfo.objects.filter(
                username = username
                ).first()
            # wechats = user.wechatid_set.all()

            wechat = user.wechatid_set.filter(puid = puid).first()
            # 帐号还没有绑定任何微信号，则绑定初始化成功的微信
            if not wechat:
                models.WechatId.objects.create(
                    puid = puid,
                    isActive = True,
                    user_info_id = user.id
                    )
                print('为%s添加微信：%s' %(username,puid))
            # 如果当前微信已经存在于数据库中，则检查其登录状态是否为在线
            else:
                # 设置为在线状态
                wechat.isActive = True
                wechat.save()
                print('%s的微信已经存在'%username)
            # print("puid",puid)
            cm.reply_channel_send(username,{
                'puid': puid,
                'init_status': True,
                'info': '登录成功，正在跳转......'
               }
            )
        t = Thread(target=go_to_mainpage)
        t.start()


def check_landing(fun):
    """
        用于检测是否登陆成功
    """
    def function(request, *args, **kwargs):
        print(request.path)
        v = request.session.get('username')
        print("用户名：", v)
        if not v:
            print('用户未登录')
            return redirect('/login/')
       
        return fun(request, *args, **kwargs)
    return function




# 用户输入的url为空时，则将其跳转到主页
def main_index(request):
    return HttpResponseRedirect('/wx_init/')


@check_landing
def wx_init(request):
    try:
        # 获取用信息
        username = request.session.get('username')
        print("request.session['username']",request.session['username'])
        user_info = models.UserInfo.objects.get(username=username)
        wechat = user_info.wechatid_set.filter(isActive=True).first()  # 获取用户地一个初始化的微信
        # 如果已经存在登录成功的微信
        if wechat:
            puid = wechat.puid
            bot = rm.get_bot(puid)
            print(bot)
            # if bot:
            request.session['puid'] = wechat.puid
            print("＂%s＂ 已经初始化了微信，他的信息：%s"%(username,wechat))
            return HttpResponseRedirect('/mainpage/')
            # else:
            #     print('登陆失败')
            #     request.session['puid'] = None
            #     user = models.UserInfo.objects.filter(
            #         username=username
            #     ).first()
            #     if user:
            #         wechat = user.wechatid_set.filter(puid=puid).first()
            #         wechat.isActive = False
            #         wechat.save()
        # # 如果没有登陆登陆了微信号
        # else:
        # 如果没有绑定任何帐号，或者绑定的帐号都是离线状态则条状到初始化微信页面
        # global e_qrcode,e_login
        e_qrcode = Event()  # 二维码标志位
        # 清除维码标志位
        e_qrcode.clear()
        # 创建机器人对象
        # --------------------------------------------------
        robot = BotThread(e_qrcode, request)
        # --------------------------------------------------
        robot.start()
        # 将创建的线程对象赋给自己
        robot.rbt=robot
        # 等待二维码标志位被set
        e_qrcode.wait()


        # 对图片数据进行base64编码，然后在转换为普通字符串格式
        qrcode = base64.b64encode(robot.qrcode).decode()

        # # 用户的唯一标识符
        uuid = robot.uuid

        # 获取二维码请求
        print('初始化微信')
        return render(request, 'initialize/InitializeWeChat.html', {'qrcode': qrcode, 'uuid': uuid, 'username':username})
    except Exception as e:
        print('未获取到用户名',e)
        return HttpResponseRedirect('/login/')



def init(request):
    return render(request,'initialize/init.html')
