
import re,urllib,html,json,random,math,string,socket,functools

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
	title: 'WD '+app.symbol+'OGE'
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
				text: '[size=45][b]Peringatan:[/b][/size] pastikan alamat '+root.addr3ss+' berasal dari [u][ref=faucetpay.io]faucetpay.io[/ref][/u] jika tidak ingin kehilangan saldo'
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
					text: 'Jumlah:'
				Slider:
					id: wd_balance
					size_hint_x: 0.7
					min: root.min_wd
			Label:
				size_hint_y: 0.2
				markup: True
				outline_width: 4
				outline_color: chex('#00FF00')
				text: app.symbol + ' : {:.12f}'.format(wd_balance.value)
		BoxLayout:
			size_hint_y: 0.18
			spacing: 10
			Button:
				id: otomatis_wd
				text: 'Otomatis Wd (OFF)'
				on_release:
				    root.dismiss()
                    root.otomatis_wd(wd_balance.value)
			Button:
				text: 'Withdraw'
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
				text: app.symbol+'oge address dari ([u][ref=faucetpay.io]faucetpay.io[/ref][/u])'
				size_hint_y: 0.06
				markup: True
				on_ref_press: 
					webopen('https://faucetpay.io/?r=3364476')
					
			TextInput:
				id: doge_address
				size_hint_y: 0.05
				multiline: False
				focus: True
				cursor_width: 7
				hint_text: app.mywallet
				
		BoxLayout:
			size_hint_y: 0.1
			Label:
				size_hint_x: 0.03
				text: 'delay: ' + str(delay.value) + ' dtk'
			Slider:
				id: delay
				size_hint_x: 0.07
				value: 2
				min: 2
				max: 12
				step: 2
		BoxLayout:
			size_hint_y: 0.05
			spacing: 10
			Button:
				id: btn_miner
				text: 'Start Miner'
				on_release: root._start()
			Button:
				id: btn_stop_miner
				text: 'Stop Miner'
				disabled: not(btn_miner.disabled)
				on_release: root._stop()
				
		BoxLayout:
			orientation: 'vertical'
			size_hint_y: 0.95
			BoxLayout:
				size_hint_y: 0.008
				padding: 0,0,0,50
				Label:
					text: '[b]'+app.symbol+'[/b] Balance:'
					color: chex('#FFD700')
					size_hint_x: 0.02
					halign: 'left'
					valign: 'center'
					text_size: self.size
					markup: True
				Label:
					id: balance
					text: '0'
					halign: 'left'
					valign: 'center'
					text_size: self.size
					size_hint_x: 0.06
				Button:
					id: wd
					text: 'WD'
					size_hint_x: 0.02
					disabled: True
					on_release: root.wd_popup.open()

			BoxLayout:
				orientation: 'vertical'
				size_hint_y: 0.08
				canvas.before:
					Color:
				    	rgb: chex('#07000B')
					Rectangle:
				        size: self.size
				        pos: self.pos
				Label:
					text: ' LOGS: '
					valign: 'center'
					halign: 'left'
					text_size: self.size
					size_hint_y: 0.05
				ScrollView:
				    do_scroll_x: False
				    do_scroll_y: True
				    bar_width: 20
				    Label:
				        id: log
				        size_hint_y: None
				        height: self.texture_size[1]
				        text_size: self.width, None
				        padding: 10, 10
				        markup: True
			BoxLayout:
				size_hint_y: 0.01	
				Label:
					text: 'by [ref='+ig_author+'][u]'+ig_author+'[/u][/ref]'					
					markup: True
					on_ref_press: webopen(url_ig_author)
"""

import plyer

class _gData:
   def __init__(self, res):
      self._res = res

   def get_csrf_token(self):
      reg=re.search('(?<="csrf-token"\scontent\=")([^"]+)', self._res)
      if reg:
         return reg.group(0)

   def get_livewire_data(self, name):
      reg=re.findall('(?<=wire\:initial\-data\=")([^"]+)', self._res)
      return (list(filter(lambda x:x["fingerprint"]["name"]==name,map(lambda x: json.loads(html.unescape(x)), reg))) or [{}])[0]

   def get_b36(self):
      int2base = lambda a, b: ''.join(
          [(string.digits +
            string.ascii_lowercase +
            string.ascii_uppercase)[(a // b ** i) % b]
           for i in range(int(math.log(a, b)), -1, -1)]
      )

      return int2base(int(str(random.random()+1).split('.')[-1]), 36)[7:]

def cekjr(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('8.8.8.8', 53))
            return func(*args, **kwargs)
        except socket.error as ex:
            plyer.notification.notify(
    			    toast=True,
    			    message="koneksi internet bermasalah",
		     )
    return wrapper


class WdPopup(Popup):
	min_wd = 0.00000005
	addr3ss = StringProperty()
	wd = ObjectProperty()
	otomatis_wd = ObjectProperty()
	get_balance=ObjectProperty()


class Miner(Screen):
	def __init__(self, **kwargs):
		super(Miner, self).__init__( **kwargs)
		
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
		self.otomatis_jumlah_wd=None
		self.otomatis_wdy=False

		self.wd_popup = ObjectProperty()
		self.user_agent = 'Mozilla/5.0 (Linux; Android 12; SM-M236B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36'
		self.url = 'https://fpminer.com/'
		self.headers = headers = {
			  'Authority': 'fpminer.com',
			  'Accept': 'text/html, application/xhtml+xml',
			  'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
			  'Content-Type': 'application/json',
			  'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
			  'sec-ch-ua-mobile': '?1',
			  'sec-ch-ua-platform': '"Android"',
			  'sec-fetch-dest': 'document',
			  'sec-fetch-mode': 'cors',
			  'sec-fetch-site': 'same-origin',
			  'User-Agent': self.user_agent,
			  'X-Livewire': 'true'
		}
		
		self.alog(f'berjalan di {plyer.devicename.device_name}')
	
	@cekjr
	def set_gdata(self, url, call, *args):
		def jalankan(req, res):
			
			self.gdata = _gData(res)
			self.cookies = req.resp_headers['set-cookie']
			Clock.schedule_once(partial(call,*args))
			
		UrlRequest(url, on_success=jalankan,req_headers=self.headers)
    
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
		data=self.gdata.get_livewire_data('withdrawal')
		if not data:
			self.set_gdata(self.data_login['effects']['redirect'], self.wd, jumlah_wd)
			return
		data.update({"updates":[{"type": "syncInput", "payload": {"id": self.gdata.get_b36(),"name": "amount","value": str(jumlah_wd)}}, {"type":"callMethod","payload":{"id": self.gdata.get_b36(),"method":"calcFees","params":[]}},{"type":"callMethod","payload":{"id": self.gdata.get_b36(),"method":"withdrawal","params":[]}}]})
		self.alog(f'prosess wd {jumlah_wd:.10f} DOGE ke wallet [u]faucetpay.io[/u]..')
		UrlRequest(urllib.parse.urljoin(self.url,'livewire/message/withdrawal'),
			req_headers=(self.headers | {
				"Content-Type": "application/json",
	      	   "X-CSRF-Token": self.csrf_token}),
	    	cookies=self.cookies,
	    	on_success=self.wd_success,
	    	req_body=json.dumps(data))
		
		
	def wd_success(self, req, res):
		if isinstance(res, dict):
			wd_mount=res['serverMemo']['data']['final_amount']
			if not self.otomatis_wdy:
			    plyer.notification.notify(
    			    title='SUKSES WD', 
    			    message=f"suksess withdraw {wd_mount:.10f} DOGE",
    			    ticker=f"suksess withdraw {wd_mount:.10f} DOGE",
    			    timeout=5
			    )
			self.alog(f"suksess wd [b][color=FFD700]{wd_mount:.10f}[/color][/b] DOGE")
	
	@cekjr
	def _start(self, *args):
		self.btn_dsbl(True)
		self.ids.btn_stop_miner.disabled = True
		self.delay = self.ids.delay.value
		addr3ss = self.ids.doge_address.text
		if addr3ss != self.addr3ss and not self.gdata:
			self.alog('checking server...')
			self.addr3ss = addr3ss
			self.csrf_token = None
			self.set_gdata(self.url, self._start)
			return
		else:
			if self.addr3ss == addr3ss and self.csrf_token:
				self.alog('start claim')
				self.ids.btn_stop_miner.disabled = False
				self.mining = Clock.schedule_interval(self.claim, self.delay)
				self.btn_dsbl(True)
				return
			else:
				self.csrf_token=self.gdata.get_csrf_token()

		data=self.gdata.get_livewire_data('login')
		data.update({'updates': [{"type": "syncInput","payload": {"id": self.gdata.get_b36(),"name": "wallet","value": self.addr3ss}},{"type": "callMethod","payload": {"id": self.gdata.get_b36(),"method": "start","params": []}}]})
		UrlRequest(urllib.parse.urljoin(self.url,"livewire/message/login"), 
	    	req_headers=self.headers | {
           	  "Content-Type": "application/json",
         	    "X-CSRF-Token": self.csrf_token},
             on_success=self.success_login,
             on_error=self.eror_login,
             on_failure=self.eror_login,
             req_body=json.dumps(data),
             method="POST",
             cookies=self.cookies
        )

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
			self.alog(f"start claim dengan delay {self.delay} dtk.")
			self.ids.btn_stop_miner.disabled = False
			self.wd_popup = WdPopup(otomatis_wd=self.otomatis_wd,get_balance=self.get_balance,wd=self.wd,addr3ss=self.addr3ss)
			self.mining = Clock.schedule_interval(self.claim, self.delay)

	@cekjr
	def eror_login(self, req, res):
		if self.addr3ss_lama and self.addr3ss_lama != self.addr3ss and self.data_login and self.csrf_token:
			self.alog("eror, mencoba login ulang...", True)
			self.addr3ss_lama = None
			UrlRequest(urllib.parse.urljoin(self.url, 'logout'),
				req_headers={
				    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
				    "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
				    "sec-ch-ua": "\"Chromium\";v=\"107\", \"Not=A?Brand\";v=\"24\"",
				    "sec-ch-ua-mobile": "?1",
				    "sec-ch-ua-platform": "\"Android\"",
				    "sec-fetch-dest": "document",
				    "sec-fetch-mode": "navigate",
				    "sec-fetch-site": "same-origin",
				    "sec-fetch-user": "?1",
				    "upgrade-insecure-requests": "1",
				    "User-Agent": self.user_agent,
				    "Referer": self.data_login["effects"]["redirect"],
				    "X-CSRF-Token": self.csrf_token,
				    "Referrer-Policy": "strict-origin-when-cross-origin"
				},on_redirect=self._start, cookies=self.cookies)
			self.cookies = None
			self.csrf_token = None
		else:
			self.alog('eror, silahkan on/offkan mode pesawat anda', True)
			self._reset()

	@cekjr
	def claim(self,  *args):
		if self.data_login and "redirect" in self.data_login["effects"]:
			UrlRequest(self.data_login["effects"]["redirect"], 
				req_headers=self.headers, 
				on_success=self.success_claim,
				on_error=self.eror_claim,
				on_failure=self.eror_claim,
				on_redirect=self.eror_login,
				cookies=self.cookies,
				timeout=60
			)

	def success_claim(self, req, res):
	    blnc=re.search("(?<=balance_value\s\=\s)([.\d]+)", res)
	    if blnc:
	         balance = float(blnc.group())
	         self.ids.balance.text = '{:.10f}'.format(balance)
	         if self.balance:
	       	  self.alog(f"claim doge {abs(self.balance-balance):.10f} DOGE ")
	         self.balance = balance
	         self.wd_popup.ids.wd_balance.max = balance
	         if balance > self.wd_popup.min_wd:
	         	self.ids.wd.disabled = False
	         	if self.otomatis_wdy:
		         	if balance > self.otomatis_jumlah_wd:
		         		self.wd(self.otomatis_jumlah_wd)
	         	
	
	def eror_claim(self, req, res):
		self.alog("eror claim", True)
		
	def alog(self, text, eror=False):
		def set_log(*x):
			color = "#FF0000" if eror else "#00FF00" 
			self.ids.log.text += strftime(f"[color={color}]%H:%M:%S -> {text} [/color]\n")
	
		Clock.schedule_once(set_log,0)
		
	def btn_dsbl(self, x):
		self.ids.btn_miner.disabled = x
		self.ids.delay.disabled = x
		self.ids.doge_address.disabled = x
		self.ids.btn_stop_miner.disabled = not(x)
	
	def _reset(self, *args):
		if self.mining:
			self.mining.cancel()
			self.mining = None
		self.addr3ss_lama = self.addr3ss
		self.btn_dsbl(False)
		self.alog("stop claim..")

		
	def _stop(self):
		self._reset()

	def donate(self):
		pass
	
	
	
class MainApp(App):
	symbol = "Ð"
	mywallet = "D6mcwUx7QYguZNZRYA3hWwqsW6Lk1KMHH3"
	ig_author  = "ikbal.rdmc__"

	def on_pause(self):
	   return True

   def on_start(self):
		plyer.orientation.set_sensor(mode='portrait')

	def build(self):
		root = Builder.load_string(uix)
		scm.add_widget(Miner(name="Miner"))

		return root

if __name__ == "__main__":
	app = MainApp()
	app.run()