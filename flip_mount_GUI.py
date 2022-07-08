import tkinter as tk
from flip_mount import FlipMountController


# カラーパレット
BG = '#FDFDEB'
LASER = '#F9CE00'
EQUIP1 = '#00818A'
EQUIP2 = '#09194F'


def quit_me(root_window):
    root_window.quit()
    root_window.destroy()


class FMCWindow(tk.Frame):
    def __init__(self, master=None, sn_list: list = None):
        super().__init__(master)
        self.master = master
        self.master.title('Flip Mount Controller')
        self.create_widgets()

        self.stats = {'laser-source': {'on': 1, 'fg': EQUIP1, 'bg': BG},
                      'laser-source-text': {'fg': BG, 'bg': EQUIP1},
                      'ArHg': {'on': -1, 'fg': EQUIP1, 'bg': BG},
                      'ArHg-text': {'fg': BG, 'bg': EQUIP1},
                      'defocus': {'on': -1, 'changed': False, 'fg': EQUIP2, 'bg': BG},
                      'mirror-1': {'on': -1, 'changed': False, 'fg': EQUIP2, 'bg': BG},
                      'mirror-2': {'on': -1, 'changed': False, 'fg': EQUIP2, 'bg': BG}}

        self.fm_names = ['defocus', 'mirror-1', 'mirror-2']
        self.sn_list = sn_list
        self.fmc_dict = {}

    def create_widgets(self):
        self.button_initialize = tk.Button(master=self.master, text='Initialize', command=self.initialize_flip_mount,
                                           width=10, height=1, font=('Helvetica', 20))
        self.msg = tk.StringVar(value='Need Initialization.')
        self.label_initialize = tk.Label(master=self.master, textvariable=self.msg, fg='red',
                                         width=20, height=1, font=('Helvetica', 15))
        self.button_close = tk.Button(master=self.master, text='QUIT', fg='white', bg='red', command=self.close_flip_mount,
                                      width=10, height=1, font=('Helvetica', 20))

        self.button_initialize.grid(row=0, column=0)
        self.label_initialize.grid(row=0, column=1)
        self.button_close.grid(row=0, column=2)

        width = 600
        height = 600
        self.canvas = tk.Canvas(master=self.master, width=width, height=height, background=BG)
        self.canvas.grid(row=1, column=0, columnspan=3)

        # Fianium製Super Continuum Laser
        self.canvas.create_rectangle(0.05 * width, 0.45 * height, 0.2 * width, 0.55 * height,
                                     tags='laser-source', fill=EQUIP1, outline='', state=tk.NORMAL)
        self.canvas.create_text(0.12 * width, 0.47 * height, tags='laser-source-text', text='SCLaser', fill=BG, font=('Helvetica', 12))
        self.canvas.tag_bind('laser-source', '<ButtonPress>', self.switch)
        # デフォーカスレンズ
        self.canvas.create_rectangle(0.29 * width, 0.45 * height, 0.31 * width, 0.55 * height,
                                     dash=(4, 4), tags='defocus', fill=BG, outline=EQUIP2, state=tk.NORMAL)
        self.canvas.tag_bind('defocus', '<ButtonPress>', self.switch)
        # Ar/Hgランプ
        self.canvas.create_rectangle(0.6 * width, 0.6 * height, 0.7 * width, 0.7 * height,
                                     dash=(4, 4), tags='ArHg', fill=BG, outline=EQUIP1, state=tk.NORMAL)
        self.canvas.create_text(0.65 * width, 0.62 * height, tags='ArHg-text', text='Ar Hg', fill=EQUIP1, font=('Helvetica', 12))
        self.canvas.tag_bind('ArHg', '<ButtonPress>', self.switch)
        # CCD Camera/Monoの切り替えミラー
        self.canvas.create_polygon(0.46 * width, 0.44 * height, 0.56 * width, 0.54 * height, 0.54 * width, 0.56 * height, 0.44 * width, 0.46 * height,
                                   dash=(4, 4), tags='mirror-1', fill=BG, outline=EQUIP2, state=tk.NORMAL)
        self.canvas.tag_bind('mirror-1', '<ButtonPress>', self.switch)
        # Ar/Hgランプの切り替えミラー
        self.canvas.create_polygon(0.44 * width, 0.69 * height, 0.54 * width, 0.59 * height, 0.56 * width, 0.61 * height, 0.46 * width, 0.71 * height,
                                   dash=(4, 4), tags='mirror-2', fill=BG, outline=EQUIP2, state=tk.NORMAL)
        self.canvas.tag_bind('mirror-2', '<ButtonPress>', self.switch)
        # QImaging製CCD Camera
        self.canvas.create_rectangle(0.6 * width, 0.1 * height, 0.7 * width, 0.3 * height,
                                     tags='Camera', fill=EQUIP1, outline='', state=tk.DISABLED)
        self.canvas.create_text(0.65 * width, 0.12 * height, text='Camera', fill=BG, font=('Helvetica', 12))
        # HORIBA製iHR320
        self.canvas.create_rectangle(0.7 * width, 0.75 * height, 0.95 * width, 0.95 * height,
                                     tags='Mono', fill=EQUIP1, outline='', state=tk.DISABLED)
        self.canvas.create_text(0.8 * width, 0.77 * height, text='Monochromator', fill=BG, font=('Helvetica', 12))
        # レーザーの光路
        self.canvas.create_line(0.2 * width, 0.5 * height, 0.5 * width, 0.5 * height,
                                width=5, tags='laser-1', fill=LASER, state=tk.DISABLED)
        self.canvas.create_line(0.5 * width, 0.5 * height, 0.65 * width, 0.5 * height, 0.65 * width, 0.3 * height,
                                width=5, tags='laser-2', fill=LASER, state=tk.DISABLED)
        self.canvas.create_line(0.5 * width, 0.5 * height, 0.5 * width, 0.85 * height, 0.7 * width, 0.85 * height,
                                width=5, dash=(4, 4), tags='laser-3', fill=LASER, state=tk.DISABLED)
        self.canvas.create_line(0.6 * width, 0.65 * height, 0.5 * width, 0.65 * height, 0.5 * width, 0.85 * height, 0.7 * width, 0.85 * height,
                                width=5, dash=(4, 4), tags='laser-ArHg', fill='lightblue', state=tk.DISABLED)

    def switch(self, event):
        """
        クリックしたウィジェットの見た目を変える．
        update_lines関数を呼び出し，光路の見た目を更新．
        電動フリップマウントを動かす．
        （レーザー・ArHgランプも切れるようにしたい）
        Args:
            event: https://daeudaeu.com/tkinter_event/#Tkinter

        Returns:

        """
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        clicked_tags = [self.canvas.itemcget(obj, 'tags') for obj in self.canvas.find_overlapping(x, y, x, y)]
        try:
            tag = clicked_tags[0].replace(' current', '')  # 最前面のwidgetは[tag] currentというstrが入る
        except IndexError:
            print('クリックされたオブジェクトが見つかりません（エッジがクリックされました）．特に問題はありません．')
            return
        self.stats[tag]['on'] *= -1
        if self.stats[tag]['on'] == 1:
            self.canvas.itemconfig(tag, fill=self.stats[tag]['fg'], outline='')
        elif self.stats[tag]['on'] == -1:
            self.canvas.itemconfig(tag, fill=self.stats[tag]['bg'], outline=self.stats[tag]['fg'], dash=(4, 4))

        self.update_lines()

        # SCLaserとArHgのテキスト色の変更
        if tag in ['laser-source', 'ArHg']:
            tag_text = tag + '-text'
            if self.stats[tag]['on'] == 1:
                self.canvas.itemconfig(tag_text, fill=self.stats[tag_text]['fg'])
            elif self.stats[tag]['on'] == -1:
                self.canvas.itemconfig(tag_text, fill=self.stats[tag_text]['bg'])

        # 選択したオブジェクトがフリップマウントを表すものであれば動かす処理を入れる
        if tag in self.fm_names:
            for name in self.fm_names:
                if name == tag:
                    self.stats[name]['changed'] = True
                else:
                    self.stats[name]['changed'] = False
            self.move_flip_mount()

    def update_lines(self):
        """
        状態に応じてself.canvasのlineオブジェクトの太さ，破線をupdateする
        Returns:

        """
        # 全ての光路をリセット
        self.canvas.itemconfig('laser-1', dash=(4, 4))
        self.canvas.itemconfig('laser-2', dash=(4, 4))
        self.canvas.itemconfig('laser-3', dash=(4, 4))

        if self.stats['laser-source']['on'] == 1:
            self.canvas.itemconfig('laser-1', dash=())
            # デフォーカスを入れると太くなる
            if self.stats['defocus']['on'] == 1:
                self.canvas.itemconfig('laser-1', width=8)
                self.canvas.itemconfig('laser-2', width=8)
                self.canvas.itemconfig('laser-3', width=8)
            else:
                self.canvas.itemconfig('laser-1', width=5)
                self.canvas.itemconfig('laser-2', width=5)
                self.canvas.itemconfig('laser-3', width=5)

            # mirror-1に関する処理
            if self.stats['mirror-1']['on'] == 1:
                self.canvas.itemconfig('laser-3', dash=())
            else:
                self.canvas.itemconfig('laser-2', dash=())
            if self.stats['mirror-2']['on'] == 1:
                self.canvas.itemconfig('laser-3', dash=(4, 4))

        # ArHgランプの光路
        if self.stats['ArHg']['on'] == 1 and self.stats['mirror-2']['on'] == 1:
            self.canvas.itemconfig('laser-ArHg', dash=())
        else:
            self.canvas.itemconfig('laser-ArHg', dash=(4, 4))

    def initialize_flip_mount(self):
        """
        電動フリップマウントのコントローラーオブジェクトの初期化
        Returns:

        """
        if len(self.sn_list) != 3:
            raise ValueError('Need 3 serial numbers.')
        for name, sn in zip(self.fm_names, self.sn_list):
            fmc = FlipMountController(sn=sn)
            fmc.move(2)
            self.fmc_dict[name] = fmc

        self.msg.set('Initialized')
        self.label_initialize.config(fg='green')

    def close_flip_mount(self):
        for fmc in self.fmc_dict.values():
            fmc.close()

        quit_me(self.master)

    def move_flip_mount(self):
        """
        状態に応じて電動フリップマウントを動かす．
        Returns:

        """
        for name, fmc in self.fmc_dict.items():
            # 状態が変わっているもののみ動かす
            print(self.stats)
            if self.stats[name]['changed']:
                if self.stats[name]['on'] == 1:
                    fmc.move(1)
                else:
                    fmc.move(2)


def main():
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', lambda: quit_me(root))
    app = FMCWindow(master=root, sn_list=['37005139', '37858078', '37005169'])
    app.mainloop()


if __name__ == '__main__':
    main()
