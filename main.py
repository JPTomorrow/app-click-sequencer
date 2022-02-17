# main execution file
# Author: Justin Morrow
# Only to be edited by Justin Morrow

from click.termui import style
import source.test.tests as t
import wx

debug = True

class ParentFrame(wx.Frame):
	def __init__(self, parent, title='MAGNET APP'):
		super(ParentFrame, self).__init__(parent, size=(800, 600))
		self.init_ui()
		self.SetTitle(title)
		self.Center()

	def init_ui(self):
		# set background stuff
		bg_color = (25,25,25)
		self.SetBackgroundColour(bg_color)
		
		# make menu bar and give it a quit button
		menubar = wx.MenuBar()
		file_menu = wx.Menu()

		quit_img = wx.ArtProvider.GetBitmap(wx.ART_QUIT)
		menu_item = wx.MenuItem(file_menu, wx.ID_EXIT, 'Quit', 'Quit application')
		menu_item.SetBitmap(quit_img)
		file_menu.Append(menu_item)

		menubar.Append(file_menu, '&File')
		self.SetMenuBar(menubar)
		self.Bind(wx.EVT_MENU, self.on_quit, menu_item)

		# make grid bag sizer
		gs = wx.GridBagSizer(3, 6)

		# make and add button to grid
		title_txt = wx.StaticText(self, style=wx.TE_CENTER, label='LOGIN')
		title_txt.SetForegroundColour((255,255,255))
		user_txt =  wx.TextCtrl(self, style=wx.TE_LEFT, value='username')
		password_txt = wx.TextCtrl(self, style=wx.TE_LEFT, value='password')
		send_button = wx.Button(self, label='Send')

		pad = 200

		widget_arr = [
			(title_txt, (1,0), (1,1), wx.EXPAND | wx.LEFT | wx.TOP, pad),
			(user_txt, (2,0), (1,3), wx.EXPAND | wx.LEFT | wx.RIGHT, pad),
			(password_txt, (3,0), (1,3), wx.EXPAND | wx.LEFT | wx.RIGHT, pad),
			(send_button, (4,2), (1,1), wx.EXPAND | wx.RIGHT, pad)
		]

		gs.AddMany(widget_arr)
		gs.AddGrowableCol(1)

		self.SetSizer(gs)


	def on_quit(self, e):
		self.Close()


if __name__ == "__main__":
	if debug: t.test_all()
	else:
		app = wx.App()
		frame = ParentFrame(None)
		frame.Show(True)
		app.MainLoop()