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
uix = "\n#:import chex kivy.utils.get_color_from_hex\n#:import webopen webbrowser.open\n\n#:set ig_author '@'+app.ig_author\n#:set url_ig_author 'https://www.instagram.com/'+app.ig_author\n\n<WdPopup>:\n        title: 'WD '+app.symbol+'OGE'\n        size_hint: 0.9,0.5\n        BoxLayout:\n                orientation: 'vertical'\n                padding: 30\n                spacing: 30\n                BoxLayout:\n                        size_hint_y: 0.8\n                        orientation: 'vertical'\n                        spacing: 20\n                        Label:\n                                size_hint_y: 0.4\n                                text: '[size=45][b]Peringatan:[/b][/size] pastikan alamat '+root.addr3ss+' berasal dari [u][ref=faucetpay.io]faucetpay.io[/ref][/u] jika tidak ingin kehilangan saldo'\n                                markup: True\n                                text_size: self.size\n                                valign: 'center'\n                                halign: 'left'\n                                on_ref_press: \n                                        webopen('https://faucetpay.io/?r=3364476')\n                                        \n                        BoxLayout:\n                                size_hint_y: 0.2\n                                spacing: 10\n                                Label:\n                                        size_hint_x: 0.3\n                                        text: 'Jumlah:'\n                                Slider:\n                                        id: wd_balance\n                                        size_hint_x: 0.7\n                                        min: root.min_wd\n                        Label:\n                                size_hint_y: 0.2\n                                markup: True\n                                outline_width: 4\n                                outline_color: chex('#00FF00')\n                                text: app.symbol + ' : {:.12f}'.format(wd_balance.value)\n                BoxLayout:\n                        size_hint_y: 0.18\n                        spacing: 10\n                        Button:\n                                id: otomatis_wd\n                                text: 'Otomatis Wd (OFF)'\n                                on_release:\n                                    root.dismiss()\n                    root.otomatis_wd(wd_balance.value)\n                        Button:\n                                text: 'Withdraw'\n                                on_release: \n                                        root.dismiss()\n                                        root.wd(wd_balance.value)\n                        \n<Miner>:\n        BoxLayout:\n                orientation: 'vertical'\n                spacing: 20\n                padding: 20\n                BoxLayout:\n                        orientation: 'vertical'\n                        size_hint_y: 0.1\n                        Label:\n                                text: app.symbol+'oge address dari ([u][ref=faucetpay.io]faucetpay.io[/ref][/u])'\n                                size_hint_y: 0.06\n                                markup: True\n                                on_ref_press: \n                                        webopen('https://faucetpay.io/?r=3364476')\n                                        \n                        TextInput:\n                                id: doge_address\n                                size_hint_y: 0.05\n                                multiline: False\n                                focus: True\n                                cursor_width: 7\n                                hint_text: app.mywallet\n                                \n                BoxLayout:\n                        size_hint_y: 0.1\n                        Label:\n                                size_hint_x: 0.03\n                                text: 'delay: ' + str(delay.value) + ' dtk'\n                        Slider:\n                                id: delay\n                                size_hint_x: 0.07\n                                value: 2\n                                min: 2\n                                max: 12\n                                step: 2\n                BoxLayout:\n                        size_hint_y: 0.05\n                        spacing: 10\n                        Button:\n                                id: btn_miner\n                                text: 'Start Miner'\n                                on_release: root._start()\n                        Button:\n                                id: btn_stop_miner\n                                text: 'Stop Miner'\n                                disabled: not(btn_miner.disabled)\n                                on_release: root._stop()\n                                \n                BoxLayout:\n                        orientation: 'vertical'\n                        size_hint_y: 0.95\n                        BoxLayout:\n                                size_hint_y: 0.008\n                                padding: 0,0,0,50\n                                Label:\n                                        text: '[b]'+app.symbol+'[/b] Balance:'\n                                        color: chex('#FFD700')\n                                        size_hint_x: 0.02\n                                        halign: 'left'\n                                        valign: 'center'\n                                        text_size: self.size\n                                        markup: True\n                                Label:\n                                        id: balance\n                                        text: '0'\n                                        halign: 'left'\n                                        valign: 'center'\n                                        text_size: self.size\n                                        size_hint_x: 0.06\n                                Button:\n                                        id: wd\n                                        text: 'WD'\n                                        size_hint_x: 0.02\n                                        disabled: True\n                                        on_release: root.wd_popup.open()\n\n                        BoxLayout:\n                                orientation: 'vertical'\n                                size_hint_y: 0.08\n                                canvas.before:\n                                        Color:\n                                        rgb: chex('#07000B')\n                                        Rectangle:\n                                        size: self.size\n                                        pos: self.pos\n                                Label:\n                                        text: ' LOGS: '\n                                        valign: 'center'\n                                        halign: 'left'\n                                        text_size: self.size\n                                        size_hint_y: 0.05\n                                ScrollView:\n                                    do_scroll_x: False\n                                    do_scroll_y: True\n                                    bar_width: 20\n                                    Label:\n                                        id: log\n                                        size_hint_y: None\n                                        height: self.texture_size[1]\n                                        text_size: self.width, None\n                                        padding: 10, 10\n                                        markup: True\n                        BoxLayout:\n                                size_hint_y: 0.01       \n                                Label:\n                                        text: 'by [ref='+ig_author+'][u]'+ig_author+'[/u][/ref]'                                        \n                                        markup: True\n                                        on_ref_press: webopen(url_ig_author)\n"
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
    min_wd = 5e-08
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
        self.user_agent = 'Mozilla/5.0 (Linux; Android 12; SM-M236B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36'
        self.url = 'https://fpminer.com/'
        self.headers = headers = {'Authority': 'fpminer.com', 'Accept': 'text/html, application/xhtml+xml', 'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7', 'Content-Type': 'application/json', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin', 'User-Agent': self.user_agent, 'X-Livewire': 'true'}
        self.alog(f'berjalan di {plyer.devicename.device_name}')

    @cekjr
    def set_gdata(self, url, call, *args):

        def jalankan(req, res):
            self.gdata = _gData(res)
            self.cookies = req.resp_headers['set-cookie']
            Clock.schedule_once(partial(call, *args))
        UrlRequest(url, on_success=jalankan, req_headers=self.headers)

    def get_balance(self):
        return self.balance or 0

    def otomatis_wd(self, jumlah_wd):
        if self.otomatis_wdy == True:
            self.otomatis_wdy = False
            self.wd_popup.ids.otomatis_wd.text = 'Otomatis Wd (OFF)'
            self.alog('otomatis wd di nonaktifkan')
        else:
            self.wd_popup.ids.otomatis_wd.text = 'Otomatis Wd (ON)'
            self.otomatis_wdy = True
            self.otomatis_jumlah_wd = jumlah_wd
            self.alog(f'otomatis wd di aktifkan jika saldo sudah mencapai {jumlah_wd:.12f}')

    @cekjr
    def wd(self, jumlah_wd, *args):
        data = self.gdata.get_livewire_data('withdrawal')
        if not data:
            self.set_gdata(self.data_login['effects']['redirect'], self.wd, jumlah_wd)
            return
        data.update({'updates': [{'type': 'syncInput', 'payload': {'id': self.gdata.get_b36(), 'name': 'amount', 'value': str(jumlah_wd)}}, {'type': 'callMethod', 'payload': {'id': self.gdata.get_b36(), 'method': 'calcFees', 'params': []}}, {'type': 'callMethod', 'payload': {'id': self.gdata.get_b36(), 'method': 'withdrawal', 'params': []}}]})
        self.alog(f'prosess wd {jumlah_wd:.10f} DOGE ke wallet [u]faucetpay.io[/u]..')
        UrlRequest(urllib.parse.urljoin(self.url, 'livewire/message/withdrawal'), req_headers=self.headers | {'Content-Type': 'application/json', 'X-CSRF-Token': self.csrf_token}, cookies=self.cookies, on_success=self.wd_success, req_body=json.dumps(data))

    def wd_success(self, req, res):
        if isinstance(res, dict):
            wd_mount = res['serverMemo']['data']['final_amount']
            if not self.otomatis_wdy:
                plyer.notification.notify(title='SUKSES WD', message=f'suksess withdraw {wd_mount:.10f} DOGE', ticker=f'suksess withdraw {wd_mount:.10f} DOGE', timeout=5)
            self.alog(f'suksess wd [b][color=FFD700]{wd_mount:.10f}[/color][/b] DOGE')

    @cekjr
    def _start(self, *args):
        self.btn_dsbl(True)
        self.ids.btn_stop_miner.disabled = True
        self.delay = self.ids.delay.value
        addr3ss = self.ids.doge_address.text
        if addr3ss != self.addr3ss and (not self.gdata):
            self.alog('checking server...')
            self.addr3ss = addr3ss
            self.csrf_token = None
            self.set_gdata(self.url, self._start)
            return
        elif self.addr3ss == addr3ss and self.csrf_token:
            self.alog('start claim')
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
                self.alog('silahkan on/off kan mode pesawat untuk mereset IP')
                self.btn_dsbl(False)
                return
            self.cookies = req.resp_headers['set-cookie']
            self.alog(f"checksum -> {res['serverMemo']['checksum']}")
            self.alog(f'start claim dengan delay {self.delay} dtk.')
            self.ids.btn_stop_miner.disabled = False
            self.wd_popup = WdPopup(otomatis_wd=self.otomatis_wd, get_balance=self.get_balance, wd=self.wd, addr3ss=self.addr3ss)
            self.mining = Clock.schedule_interval(self.claim, self.delay)

    @cekjr
    def eror_login(self, req, res):
        if self.addr3ss_lama and self.addr3ss_lama != self.addr3ss and self.data_login and self.csrf_token:
            self.alog('eror, mencoba login ulang...', True)
            self.addr3ss_lama = None
            UrlRequest(urllib.parse.urljoin(self.url, 'logout'), req_headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'same-origin', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'User-Agent': self.user_agent, 'Referer': self.data_login['effects']['redirect'], 'X-CSRF-Token': self.csrf_token, 'Referrer-Policy': 'strict-origin-when-cross-origin'}, on_redirect=self._start, cookies=self.cookies)
            self.cookies = None
            self.csrf_token = None
        else:
            self.alog('eror, silahkan on/offkan mode pesawat anda', True)
            self._reset()

    @cekjr
    def claim(self, *args):
        if self.data_login and 'redirect' in self.data_login['effects']:
            UrlRequest(self.data_login['effects']['redirect'], req_headers=self.headers, on_success=self.success_claim, on_error=self.eror_claim, on_failure=self.eror_claim, on_redirect=self.eror_login, cookies=self.cookies, timeout=60)

    def success_claim(self, req, res):
        blnc = re.search('(?<=balance_value\\s\\=\\s)([.\\d]+)', res)
        if blnc:
            balance = float(blnc.group())
            self.ids.balance.text = '{:.10f}'.format(balance)
            if self.balance:
                self.alog(f'claim doge {abs(self.balance - balance):.10f} DOGE ')
            self.balance = balance
            self.wd_popup.ids.wd_balance.max = balance
            if balance > self.wd_popup.min_wd:
                self.ids.wd.disabled = False
                if self.otomatis_wdy:
                    if balance > self.otomatis_jumlah_wd:
                        self.wd(self.otomatis_jumlah_wd)

    def eror_claim(self, req, res):
        self.alog('eror claim', True)

    def alog(self, text, eror=False):

        def set_log(*x):
            color = '#FF0000' if eror else '#00FF00'
            self.ids.log.text += strftime(f'[color={color}]%H:%M:%S -> {text} [/color]\n')
        Clock.schedule_once(set_log, 0)

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
        self.alog('stop claim..')

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
        return root
if __name__ == '__main__':
    app = MainApp()
    app.run()