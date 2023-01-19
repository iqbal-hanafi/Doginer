#: by @ikbal.rdmc__

import re, urllib, html, json, random, math, string, socket, functools
from functools import partial
from time import strftime
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
from kivy.lang.builder import Builder

scm = ScreenManager()

uix = """
#:import chex kivy.utils.get_color_from_hex
#:import webopen webbrowser.open

#:set ig_author '@'+app.ig_author
#:set url_ig_author 'https://www.instagram.com/'+app.ig_author

<WdPopup>:
        title: 'Penarikan '+app.symbol+'OGE'
        size_hint: 0.9,0.5
        BoxLayout:
                orientation: 'vertical'
                padding: 30
                spacing: 30
                BoxLayout:
                        size_hint_y: 0.8
                        orientation: 'vertical'
                        spacing: 20
                        Label:
                                size_hint_y: 0.4
                                text: '[size=45][b]Peringatan:[/b][/size] pastikan alamat '+root.addr3ss+' berasal dari akun [u][ref=faucetpay.io]faucetpay.io[/ref][/u] anda jika tidak ingin kehilangan saldo, minimal penarikan '+'{:.8f}'.format(root.min_wd)+' DOGE'
                                markup: True
                                text_size: self.size
                                valign: 'center'
                                halign: 'left'
                                on_ref_press:
                                        webopen('https://faucetpay.io/?r=3364476')

                        BoxLayout:
                                size_hint_y: 0.2
                                spacing: 10
                                Label:
                                        size_hint_x: 0.3
                                        text: 'Atur jumlah:'
                                Slider:
                                        id: wd_balance
                                        size_hint_x: 0.7
                                        min: root.min_wd
                        Label:
                                size_hint_y: 0.2
                                markup: True                       
                                color: chex('#00FF00')
                                text: app.symbol + ' : {:.12f}'.format(wd_balance.value)
                BoxLayout:
                        size_hint_y: 0.3
                        spacing: 20
                        orientation: 'vertical'
                        Button:
                                id: otomatis_wd
                                text: 'Otomatis penarikan (OFF)'
                                on_release:
                                        root.dismiss()
                                        root.otomatis_wd(wd_balance.value)
                        Button:
                                text: 'Penarikan'
                                on_release:
                                        root.dismiss()
                                        root.wd(wd_balance.value)

<Miner>:
        BoxLayout:
                orientation: 'vertical'
                spacing: 20
                padding: 20
                BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: 0.1
                        Label:
                                text: 'Masukkan alamat doge anda dari akun ([u][ref=faucetpay.io]faucetpay.io[/ref][/u])'
                                size_hint_y: 0.06
                                markup: True
                                on_ref_press:
                                        webopen('https://faucetpay.io/?r=3364476')

                        TextInput:
                                id: doge_address
                                size_hint_y: 0.05
                                multiline: False
                                cursor_width: 8
                                cursor_color: chex('#000000')
                                hint_text: 'contoh: '+app.mywallet
                                on_text:
                                        btn_miner.disabled = len(self.text.strip()) < 10

                BoxLayout:
                        size_hint_y: 0.1
                        Label:
                                size_hint_x: 0.04
                                text: 'Atur delay: ' + str(delay.value) + ' detik'
                        Slider:
                                id: delay
                                size_hint_x: 0.06
                                value: 2
                                min: 2
                                max: 12
                                step: 2
                BoxLayout:
                        size_hint_y: 0.05
                        spacing: 10
                        Button:
                                id: btn_miner
                                text: 'Mulai'
                                disabled: True
                                on_release: root._start()
                        Button:
                                id: btn_stop_miner
                                text: 'Berhenti'
                                disabled: True
                                on_release: root._stop()

                BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: 0.95
                        BoxLayout:
                                size_hint_y: 0.01
                                padding: 0,0,0,50
                                
                                Button:
                                        id: wd
                                        text: 'Tarik'
                                        size_hint_x: 0.02
                                        disabled: True
                                        on_release: root.wd_popup.open()

                                Label:
                                        id: balance
                                        color: chex('#FFD700')
                                        text: '0 [b]'+app.symbol+'[/b]'
                                        halign: 'right'
                                        valign: 'center'
                                        markup: True
                                        text_size: self.size
                                        size_hint_x: 0.08
                                        font_size: dp(19)
                                        padding_x: 20
                                
                        BoxLayout:
                                orientation: 'vertical'
                                size_hint_y: 0.05
                                spacing: 20     
                                ScrollView:
                                        do_scroll_x: False
                                        do_scroll_y: True
                                        scroll_type: ["bars"]
                                        bar_width: 40
                                        bar_margin: 10   
                                        canvas.before:
                                                Color:
                                                        rgb: chex('#0F0F00')
                                                RoundedRectangle:
                                                        size: self.size
                                                        pos: self.pos
                                                        radius: [10]                                           
                                        Label:
                                                id: log
                                                size_hint_y: None
                                                height: self.texture_size[1]
                                                text_size: self.width, None
                                                padding: 20, 20
                                                markup: True
                        BoxLayout:
                                size_hint_y: 0.06
                                orientation: 'vertical'
                                
                                Label:
                                        size_hint_y: 0.01
                                        text: 'Dibuat dengan Kivy (Python) by [ref='+ig_author+'][u]'+ig_author+'[/u][/ref]'
                                        markup: True
                                        font_size: dp(12)
                                        on_ref_press: webopen(url_ig_author)
                                Widget:
                                        size_hint_y: 0.09
"""


import plyer

class _gData:
    def __init__(self, res):
        self._res = res

    def get_csrf_token(self):
        reg = re.search('(?<="csrf-token"\\scontent\\=")([^"]+)', self._res)
        if reg:
            return reg.group(0)

    def get_livewire_data(self, name):
        reg = re.findall('(?<=wire\\:initial\\-data\\=")([^"]+)', self._res)
        return (list(filter(lambda x: x['fingerprint']['name'] == name, map(lambda x: json.loads(html.unescape(x)), reg))) or [{}])[0]

    def get_b36(self):
        int2base = lambda a, b: ''.join([(string.digits + string.ascii_lowercase + string.ascii_uppercase)[a // b ** i % b] for i in range(int(math.log(a, b)), -1, -1)])
        return int2base(int(str(random.random() + 1).split('.')[-1]), 36)[7:]

def cekjr(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('8.8.8.8', 53))
            return func(*args, **kwargs)
        except socket.error as ex:
            plyer.notification.notify(toast=True, message='koneksi internet bermasalah')
    return wrapper

class WdPopup(Popup):
    min_wd = 0.001
    addr3ss = StringProperty()
    wd = ObjectProperty()
    otomatis_wd = ObjectProperty()
    get_balance = ObjectProperty()

class Miner(Screen):

    def __init__(self, **kwargs):
        super(Miner, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.mining = None
        self.delay = None
        self.gdata = None
        self.cookies = None
        self.csrf_token = None
        self.addr3ss = None
        self.addr3ss_lama = None
        self.data_login = None
        self.balance = None
        self.otomatis_jumlah_wd = None
        self.otomatis_wdy = False
        self.wd_popup = ObjectProperty()
        self.user_agent = 'Mozilla/5.0', #'(Linux; Android 12; SM-M236B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36'
        self.url = 'https://fpminer.com/'
        self.headers = headers = {'Authority': 'fpminer.com', 'Accept': 'text/html, application/xhtml+xml', 'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7', 'Content-Type': 'application/json', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin', 'User-Agent': self.user_agent, 'X-Livewire': 'true'}
        self.alog(f'berjalan di perangkat {plyer.devicename.device_name}')
        self.get_harga_idr(lambda harga: self.alog(f'harga 1 DOGE sekarang {harga}'))
        
    @cekjr
    def set_gdata(self, url, call, *args):

        def jalankan(req, res):
            self.gdata = _gData(res)
            self.cookies = req.resp_headers['set-cookie']
            Clock.schedule_once(partial(call, *args))
        UrlRequest(url, on_success=jalankan, req_headers=self.headers)

    def get_balance(self):
        return self.balance or 0
    
    @cekjr
    def get_harga_idr(self, func):
        UrlRequest('https://www.coingecko.com/id/koin_koin/dogecoin/idr',on_success=lambda req, res: func(re.search('(?<=1\sDOGE\s\=\s)(Rp[0-9.]+)', res).group(0)))

    def otomatis_wd(self, jumlah_wd):
        if self.otomatis_wdy == True:
            self.otomatis_wdy = False
            self.wd_popup.ids.otomatis_wd.text = 'Otomatis Penarikan (OFF)'
            self.alog('otomatis penarikan di nonaktifkan')
        else:
            self.wd_popup.ids.otomatis_wd.text = 'Otomatis Penarikan (ON)'
            self.otomatis_wdy = True
            self.otomatis_jumlah_wd = jumlah_wd
            self.alog(f'otomatis penarikan di aktifkan jika saldo sudah mencapai {jumlah_wd:.12f}')

    @cekjr
    def wd(self, jumlah_wd, *args):
        data = self.gdata.get_livewire_data('withdrawal')
        if not data:
            self.set_gdata(self.data_login['effects']['redirect'], self.wd, jumlah_wd)
            return
        data.update({'updates': [{'type': 'syncInput', 'payload': {'id': self.gdata.get_b36(), 'name': 'amount', 'value': str(jumlah_wd)}}, {'type': 'callMethod', 'payload': {'id': self.gdata.get_b36(), 'method': 'calcFees', 'params': []}}, {'type': 'callMethod', 'payload': {'id': self.gdata.get_b36(), 'method': 'withdrawal', 'params': []}}]})
        self.alog(f'prosess penarikan {jumlah_wd:.10f} DOGE ke akun [u]faucetpay.io[/u]..')
        UrlRequest(urllib.parse.urljoin(self.url, 'livewire/message/withdrawal'), req_headers=self.headers | {'Content-Type': 'application/json', 'X-CSRF-Token': self.csrf_token}, cookies=self.cookies, on_success=self.wd_success, req_body=json.dumps(data))

    def wd_success(self, req, res):
        if isinstance(res, dict):
            wd_mount = res['serverMemo']['data']['final_amount']
            if not self.otomatis_wdy:
                plyer.notification.notify(title='SUKSES ', message=f'penarikan {wd_mount:.8f} DOGE', ticker=f'suksess penarikan {wd_mount:.10f} DOGE', timeout=5)
            self.alog(f'suksess penarikan [b][color=FFD700]{wd_mount:.10f}[/color][/b] DOGE')

    @cekjr
    def _start(self, *args):
        self.btn_dsbl(True)
        self.ids.btn_stop_miner.disabled = True
        self.delay = self.ids.delay.value
        addr3ss = self.ids.doge_address.text
        if addr3ss != self.addr3ss and (not self.gdata):
            self.alog('konfigurasi server...')
            self.addr3ss = addr3ss
            self.csrf_token = None
            self.set_gdata(self.url, self._start)
            return
        elif self.addr3ss == addr3ss and self.csrf_token:
            self.alog('dimulai mengklaim')
            self.ids.btn_stop_miner.disabled = False
            self.mining = Clock.schedule_interval(self.claim, self.delay)
            self.btn_dsbl(True)
            return
        else:
            self.csrf_token = self.gdata.get_csrf_token()
        data = self.gdata.get_livewire_data('login')
        data.update({'updates': [{'type': 'syncInput', 'payload': {'id': self.gdata.get_b36(), 'name': 'wallet', 'value': self.addr3ss}}, {'type': 'callMethod', 'payload': {'id': self.gdata.get_b36(), 'method': 'start', 'params': []}}]})
        UrlRequest(urllib.parse.urljoin(self.url, 'livewire/message/login'), req_headers=self.headers | {'Content-Type': 'application/json', 'X-CSRF-Token': self.csrf_token}, on_success=self.success_login, on_error=self.eror_login, on_failure=self.eror_login, req_body=json.dumps(data), method='POST', cookies=self.cookies)

    def success_login(self, req, res):
        self.delay = self.ids.delay.value
        if isinstance(res, dict):
            self.data_login = res
            if 'you cannot have more than one account' in str(res).lower():
                self.alog('kesalahan, silahkan on/off kan mode pesawat untuk mereset IP', True)
                self.btn_dsbl(False)
                return
            self.cookies = req.resp_headers['set-cookie']
            self.alog(f"checksum -> {res['serverMemo']['checksum']}")
            self.alog(f'mulai mengklaim dengan delay {self.delay} detik.')
            self.ids.btn_stop_miner.disabled = False
            self.wd_popup = WdPopup(otomatis_wd=self.otomatis_wd, get_balance=self.get_balance, wd=self.wd, addr3ss=self.addr3ss)
            self.alog(f'untuk menghindari pending minimal penarikan {self.wd_popup.min_wd:.3f} DOGE')
            self.mining = Clock.schedule_interval(self.claim, self.delay)

    @cekjr
    def eror_login(self, req, res):
        if self.addr3ss_lama and self.addr3ss_lama != self.addr3ss and self.data_login and self.csrf_token:
            self.alog('kesalahan, mengkonfigurasi ulang server...', True)
            self.addr3ss_lama = None
            UrlRequest(urllib.parse.urljoin(self.url, 'logout'), req_headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'same-origin', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'User-Agent': self.user_agent, 'Referer': self.data_login['effects']['redirect'], 'X-CSRF-Token': self.csrf_token, 'Referrer-Policy': 'strict-origin-when-cross-origin'}, on_redirect=self._start, cookies=self.cookies)
            self.cookies = None
            self.csrf_token = None
        else:
            self.alog('kesalahan, silahkan on/offkan mode pesawat untuk mereset IP', True)
            self._reset()

    @cekjr
    def claim(self, *args):
        if self.data_login and 'redirect' in self.data_login['effects']:
            UrlRequest(self.data_login['effects']['redirect'], req_headers=self.headers, on_success=self.success_claim, on_error=self.eror_claim, on_failure=self.eror_claim, on_redirect=self.eror_login, cookies=self.cookies, timeout=60)

    def success_claim(self, req, res):
        blnc = re.search('(?<=balance_value\\s\\=\\s)([.\\d]+)', res)
        if blnc:
            balance = float(blnc.group())
            self.ids.balance.text = f'{balance:.8f} [b]{self.app.symbol}[/b]'
            if self.balance:
                self.alog(f'sukses mengklaim {abs(self.balance - balance):.10f} {self.app.symbol}')
            self.balance = balance
            self.wd_popup.ids.wd_balance.max = balance
            if balance > self.wd_popup.min_wd:
                self.ids.wd.disabled = False
                if self.otomatis_wdy:
                    if balance > self.otomatis_jumlah_wd:
                        self.wd(self.otomatis_jumlah_wd)

    def eror_claim(self, req, res):
        self.alog('kesalahan saat mengklaim', True)

    def alog(self, text, eror=False):
         color = '#FF0000' if eror else '#00FF00'
         def set_log(*args):
                 self.ids.log.text += f'[color={color}]{text}[/color]\n'
         Clock.schedule_once(set_log,0)
#                 Clock.tick_draw()
#         for t in [*list(strftime('%H:%M:%S ~ ')),text+'\n']:
#                 Clock.schedule_once(partial(set_log,t), 0.3)
                
                 
    def btn_dsbl(self, x):
        self.ids.btn_miner.disabled = x
        self.ids.delay.disabled = x
        self.ids.doge_address.disabled = x
        self.ids.btn_stop_miner.disabled = not x

    def _reset(self, *args):
        if self.mining:
            self.mining.cancel()
            self.mining = None
        self.addr3ss_lama = self.addr3ss
        self.btn_dsbl(False)
        self.alog('berhenti mengklaim..')

    def _stop(self):
        self._reset()

    def donate(self):
        pass

class MainApp(App):
    symbol = 'Ð'
    mywallet = 'D6mcwUx7QYguZNZRYA3hWwqsW6Lk1KMHH3'
    ig_author = 'ikbal.rdmc__'

    def on_pause(self):
        return True

    def on_start(self):
        plyer.orientation.set_sensor(mode='portrait')
        
    def build(self):
        root = Builder.load_string(uix)
        scm.add_widget(Miner(name='Miner'))
        return scm
        
if __name__ == '__main__':
    app = MainApp()
    app.run()