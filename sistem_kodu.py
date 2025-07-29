import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

ARKA_PLAN = '#111111'  # Siyah
BUTON_RENK = '#1a237e'  # Lacivert-mavi
BUTON_AKTIF = '#3949ab' # Açık mavi
YAZI_RENK = '#ffffff'   # Beyaz
CIKIS_RENK = '#b71c1c'  # Kırmızı
CIKIS_AKTIF = '#7f1313' # Koyu kırmızı
DB_PATH = 'kayitlar.db'

class OgrenciKayitSistemi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Öğrenci Kayıt Sistemi')
        self.geometry('1100x700')
        self.configure(bg=ARKA_PLAN)
        self.bind('<Escape>', lambda e: self.destroy())  # ESC ile çıkış
        self._veritabani_olustur()
        self._build_main_menu()

    def _veritabani_olustur(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        # Tabloyu oluştur
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Ogrenciler (
            tc INTEGER PRIMARY KEY,
            ad TEXT,
            soyad TEXT,
            geldiği_okul TEXT,
            adres TEXT,
            telefon_numarası INTEGER,
            doğum_tarihi INTEGER
        )''')
        self.conn.commit()
        # lgs_puan sütunu yoksa ekle
        self.cursor.execute("PRAGMA table_info(Ogrenciler)")
        kolonlar = [row[1] for row in self.cursor.fetchall()]
        if 'lgs_puan' not in kolonlar:
            self.cursor.execute('ALTER TABLE Ogrenciler ADD COLUMN lgs_puan INTEGER')
            self.conn.commit()
        if 'foto_yolu' not in kolonlar:
            self.cursor.execute('ALTER TABLE Ogrenciler ADD COLUMN foto_yolu TEXT')
            self.conn.commit()

    def _build_main_menu(self):
        for widget in self.winfo_children():
            widget.destroy()
        frame = tk.Frame(self, bg=ARKA_PLAN)
        frame.place(relx=0.5, rely=0.5, anchor='center')

        baslik = tk.Label(frame, text='ÖĞRENCİ KAYIT SİSTEMİNE HOŞGELDİNİZ', font=('Arial', 26, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK)
        baslik.grid(row=0, column=0, columnspan=2, pady=(0, 40))

        buton_isimleri = [
            ('Öğrenci Kaydet', self.ogrenci_kaydet_ekrani_ac),
            ('Öğrenci Sil', self.ogrenci_silme_ekrani_ac),
            ('Kayıtlı Öğrencileri Listele', self.ogrenci_listele_ekrani_ac),
            ('Öğrenci Kayıt Düzenle', self.ogrenci_duzenle_ekrani_ac)
        ]

        for i, (isim, komut) in enumerate(buton_isimleri):
            btn = tk.Button(
                frame,
                text=isim,
                font=('Arial', 15, 'bold'),
                width=20,
                height=1,
                bg=BUTON_RENK,
                fg=YAZI_RENK,
                activebackground=BUTON_AKTIF,
                activeforeground=YAZI_RENK,
                bd=0,
                cursor='hand2',
                command=komut
            )
            btn.grid(row=1 + i // 2, column=i % 2, padx=30, pady=18, sticky='ew')

        # Sağ alta Kaydet ve Çık butonu
        cikis_btn = tk.Button(
            self,
            text='Kaydet ve Çık',
            font=('Arial', 14, 'bold'),
            width=11,
            height=1,
            bg=CIKIS_RENK,
            fg=YAZI_RENK,
            activebackground=CIKIS_AKTIF,
            activeforeground=YAZI_RENK,
            bd=0,
            cursor='hand2',
            command=self.kaydet_ve_cik
        )
        cikis_btn.place(relx=1.0, rely=1.0, anchor='se', x=-40, y=-30)

    def kaydet_ve_cik(self):
        cevap = messagebox.askyesno('Çıkış', 'Kaydedip çıkmak istediğinizden emin misiniz?')
        if cevap:
            self.conn.close()
            self.destroy()

    def _create_scrollable_frame(self, parent):
        canvas = tk.Canvas(parent, bg=ARKA_PLAN, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        scrollable_frame = tk.Frame(canvas, bg=ARKA_PLAN)
        window = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            # Frame'in genişliğini canvas ile eşitle
            canvas.itemconfig(window, width=canvas.winfo_width())

        scrollable_frame.bind('<Configure>', on_frame_configure)

        def on_canvas_configure(event):
            # Frame'in genişliğini canvas ile eşitle
            canvas.itemconfig(window, width=event.width)

        canvas.bind('<Configure>', on_canvas_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
        canvas.bind_all('<MouseWheel>', _on_mousewheel)
        return scrollable_frame

    def ogrenci_formu_goster(self, kayit_mi=True, ogrenci_veri=None, tc_duzenle=None):
        for widget in self.winfo_children():
            widget.destroy()
        ana_frame = tk.Frame(self, bg=ARKA_PLAN)
        ana_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=1, relheight=1)
        # Başlık en üstte sabit
        baslik_text = 'Öğrenci Kayıt' if kayit_mi else 'Öğrenci Bilgilerini Düzenle'
        baslik = tk.Label(ana_frame, text=baslik_text, font=('Arial', 22, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK)
        baslik.pack(pady=(10, 5))
        # Alanları iki sütuna böl
        sol_alanlar = [
            ('TC Kimlik No', 'tc'),
            ('Ad', 'ad'),
            ('Soyad', 'soyad'),
            ('Geldiği Okul', 'geldiği_okul'),
            ('Adres', 'adres'),
            ('Telefon Numarası', 'telefon_numarası'),
        ]
        sag_alanlar = [
            ('LGS Puanı', 'lgs_puan'),
            ('Doğum Tarihi', 'doğum_tarihi'),
            ('Fotoğraf', 'foto_yolu'),
            ('En Sevdiği Ders', 'sevdigi_ders'),
            ('Sevmediği Ders', 'sevmedigi_ders'),
            ('Kulüp', 'kulup'),
        ]
        aciklama_alan = ('Açıklama', 'aciklama')
        for widget in ana_frame.winfo_children():
            if isinstance(widget, tk.Label):
                continue  # başlık kalsın
            widget.destroy()
        self.kayit_girdiler = {}
        form_frame = tk.Frame(ana_frame, bg=ARKA_PLAN)
        form_frame.pack(expand=True, fill='both')
        for col in range(4):
            form_frame.grid_columnconfigure(col, weight=1)
        total_rows = max(len(sol_alanlar), len(sag_alanlar)) + 2  # açıklama ve buton satırı dahil
        for row in range(total_rows):
            form_frame.grid_rowconfigure(row, weight=1, minsize=40)
        # Sol sütun
        for i, (label, key) in enumerate(sol_alanlar):
            l = tk.Label(form_frame, text=label, font=('Arial', 16), bg=ARKA_PLAN, fg=YAZI_RENK)
            l.grid(row=i, column=0, sticky='w', padx=(20, 8), pady=10)
            e = tk.Entry(form_frame, font=('Arial', 16), bg='#222a36', fg=YAZI_RENK, insertbackground=YAZI_RENK, width=22, bd=1, relief='flat', justify='center')
            e.grid(row=i, column=1, pady=10, sticky='w', padx=(0, 10))
            if ogrenci_veri is not None and ogrenci_veri[i] is not None:
                e.insert(0, ogrenci_veri[i])
            self.kayit_girdiler[key] = e
        # Sağ sütun
        for i, (label, key) in enumerate(sag_alanlar):
            l = tk.Label(form_frame, text=label, font=('Arial', 16), bg=ARKA_PLAN, fg=YAZI_RENK)
            l.grid(row=i, column=2, sticky='e', padx=(10, 8), pady=10)
            if key == 'foto_yolu':
                foto_frame = tk.Frame(form_frame, bg=ARKA_PLAN)
                foto_frame.grid(row=i, column=3, pady=10, sticky='w', padx=(0, 40))
                self.foto_dosya_adi = tk.StringVar(value='Seçilmedi')
                self.foto_dosya_yolu = None
                if ogrenci_veri is not None and len(ogrenci_veri) > 8 and ogrenci_veri[8]:
                    self.foto_dosya_adi.set(ogrenci_veri[8])
                    self.foto_dosya_yolu = ogrenci_veri[8]
                foto_sec_btn = tk.Button(foto_frame, text='Fotoğraf Seç', font=('Arial', 14), bg=BUTON_RENK, fg=YAZI_RENK, activebackground=BUTON_AKTIF, activeforeground=YAZI_RENK, bd=0, cursor='hand2', command=self.fotograf_sec, width=10, height=1)
                foto_sec_btn.pack(side='left', padx=8)
                foto_adi_label = tk.Label(foto_frame, textvariable=self.foto_dosya_adi, font=('Arial', 14), bg=ARKA_PLAN, fg=YAZI_RENK)
                foto_adi_label.pack(side='left')
                self.kayit_girdiler[key] = self.foto_dosya_adi
            elif key == 'kulup':
                self.kulup_var = tk.StringVar(value='Kulüp Seçiniz')
                if ogrenci_veri is not None and len(ogrenci_veri) > 12 and ogrenci_veri[12]:
                    self.kulup_var.set(ogrenci_veri[12])
                kulup_entry = tk.Entry(form_frame, font=('Arial', 16), bg='#222a36', fg=YAZI_RENK, insertbackground=YAZI_RENK, textvariable=self.kulup_var, state='readonly', width=22, bd=1, relief='flat', cursor='hand2', justify='center', readonlybackground='#222a36')
                kulup_entry.grid(row=i, column=3, pady=10, sticky='w', padx=(0, 40))
                self.kayit_girdiler[key] = self.kulup_var
                def kulup_sec():
                    popup = tk.Toplevel(self)
                    popup.title('Kulüp Seç')
                    popup.geometry('300x300')
                    popup.configure(bg=ARKA_PLAN)
                    kulup_listesi = ['BİLİŞİM', 'SANAT', 'SOSYAL FAALİYETLER', 'KÜTÜPHANE', 'KİŞİSEL GELİŞİM']
                    for kulup in kulup_listesi:
                        btn = tk.Button(popup, text=kulup, font=('Arial', 14), width=22, bg=BUTON_RENK, fg=YAZI_RENK, activebackground=BUTON_AKTIF, activeforeground=YAZI_RENK, bd=0, cursor='hand2', command=lambda k=kulup: [self.kulup_var.set(k), popup.destroy()])
                        btn.pack(pady=8)
                kulup_entry.bind('<Button-1>', lambda e: kulup_sec())
            else:
                idx = i + len(sol_alanlar)
                e = tk.Entry(form_frame, font=('Arial', 16), bg='#222a36', fg=YAZI_RENK, insertbackground=YAZI_RENK, width=22, bd=1, relief='flat', justify='center')
                e.grid(row=i, column=3, pady=10, sticky='w', padx=(0, 40))
                if ogrenci_veri is not None and ogrenci_veri[idx] is not None:
                    e.insert(0, ogrenci_veri[idx])
                self.kayit_girdiler[key] = e
        # Açıklama alanı (iki sütun birleşik)
        l = tk.Label(form_frame, text=aciklama_alan[0], font=('Arial', 12), bg=ARKA_PLAN, fg=YAZI_RENK)
        l.grid(row=max(len(sol_alanlar), len(sag_alanlar)), column=0, sticky='w', padx=(20, 8), pady=6)
        aciklama_entry = tk.Entry(form_frame, font=('Arial', 12), bg='#222a36', fg=YAZI_RENK, insertbackground=YAZI_RENK, width=20, bd=1, relief='flat', justify='center')
        aciklama_entry.grid(row=max(len(sol_alanlar), len(sag_alanlar)), column=1, pady=6, sticky='w')
        # Boş label ile hizalama koru
        tk.Label(form_frame, text='', bg=ARKA_PLAN).grid(row=max(len(sol_alanlar), len(sag_alanlar)), column=2)
        tk.Label(form_frame, text='', bg=ARKA_PLAN).grid(row=max(len(sol_alanlar), len(sag_alanlar)), column=3)
        if ogrenci_veri is not None and ogrenci_veri[-1] is not None:
            aciklama_entry.insert(0, ogrenci_veri[-1])
        self.kayit_girdiler[aciklama_alan[1]] = aciklama_entry
        # Butonlar
        btn_row = max(len(sol_alanlar), len(sag_alanlar)) + 1
        ortak_buton_opts = {
            'font': ('Arial', 14, 'bold'),
            'width': 11,
            'height': 1,
            'bg': BUTON_RENK,
            'fg': YAZI_RENK,
            'activebackground': BUTON_AKTIF,
            'activeforeground': YAZI_RENK,
            'bd': 0,
            'cursor': 'hand2',
            'pady': 0,
            'padx': 0
        }
        if kayit_mi:
            btn_kaydet = tk.Button(
                form_frame,
                text='Kaydet',
                command=self.ogrenci_kaydet,
                **ortak_buton_opts
            )
        else:
            btn_kaydet = tk.Button(
                form_frame,
                text='Kaydet',
                command=lambda: self.ogrenci_duzenle_kaydet_onay(tc_duzenle),
                **ortak_buton_opts
            )
        btn_kaydet.grid(row=btn_row, column=1, pady=18, sticky='w', padx=8)
        btn_geri = tk.Button(
            form_frame,
            text='Geri Dön',
            command=self._build_main_menu if kayit_mi else self.ogrenci_duzenle_ekrani_ac,
            **ortak_buton_opts
        )
        btn_geri.grid(row=btn_row, column=2, pady=18, sticky='w', padx=8)
        # Buton satırının yüksekliğini artır
        form_frame.grid_rowconfigure(btn_row, weight=1, minsize=60)
        # Sağ alta Çıkış butonu (yükseklik=1, diğerleriyle aynı)
        cikis_btn = tk.Button(
            ana_frame,
            text='Çık',
            font=ortak_buton_opts['font'],
            width=ortak_buton_opts['width'],
            height=ortak_buton_opts['height'],
            bg=CIKIS_RENK,
            fg=YAZI_RENK,
            activebackground=CIKIS_AKTIF,
            activeforeground=YAZI_RENK,
            bd=0,
            cursor='hand2',
            command=self.destroy
        )
        cikis_btn.place(relx=1.0, rely=1.0, anchor='se', x=-120, y=-30)

    def ogrenci_kaydet_ekrani_ac(self):
        self.ogrenci_formu_goster(kayit_mi=True)

    def fotograf_sec(self):
        dosya = filedialog.askopenfilename(title='Fotoğraf Seç', filetypes=[('Resim Dosyaları', '*.jpg *.jpeg *.png *.bmp')])
        if dosya:
            self.foto_dosya_adi.set(dosya.split('/')[-1])
            self.foto_dosya_yolu = dosya
        else:
            self.foto_dosya_adi.set('Seçilmedi')
            self.foto_dosya_yolu = None

    def ogrenci_kaydet(self):
        try:
            tc = int(self.kayit_girdiler['tc'].get())
            ad = self.kayit_girdiler['ad'].get()
            soyad = self.kayit_girdiler['soyad'].get()
            okul = self.kayit_girdiler['geldiği_okul'].get()
            adres = self.kayit_girdiler['adres'].get()
            telefon = self.kayit_girdiler['telefon_numarası'].get()
            lgs = int(self.kayit_girdiler['lgs_puan'].get())
            dogum = int(self.kayit_girdiler['doğum_tarihi'].get())
            sevdigi_ders = self.kayit_girdiler['sevdigi_ders'].get()
            sevmedigi_ders = self.kayit_girdiler['sevmedigi_ders'].get()
            kulup = self.kayit_girdiler['kulup'].get()
            aciklama = self.kayit_girdiler['aciklama'].get()
            foto_yolu = self.foto_dosya_yolu if self.foto_dosya_yolu else ''
        except Exception as e:
            messagebox.showerror('Hata', 'Lütfen tüm alanları doğru doldurun!')
            return
        try:
            self.cursor.execute('''INSERT INTO Ogrenciler (tc, ad, soyad, geldiği_okul, adres, telefon_numarası, lgs_puan, doğum_tarihi, foto_yolu, sevdigi_ders, sevmedigi_ders, kulup, aciklama) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (tc, ad, soyad, okul, adres, telefon, lgs, dogum, foto_yolu, sevdigi_ders, sevmedigi_ders, kulup, aciklama))
            self.conn.commit()
            messagebox.showinfo('Başarılı', 'Öğrenci kaydedildi!')
            self._build_main_menu()
        except sqlite3.IntegrityError:
            messagebox.showerror('Hata', 'Bu TC ile zaten bir öğrenci kayıtlı!')
        except Exception as e:
            messagebox.showerror('Hata', f'Kayıt sırasında hata oluştu: {e}')

    def ogrenci_listele_ekrani_ac(self):
        for widget in self.winfo_children():
            widget.destroy()
        frame = tk.Frame(self, bg=ARKA_PLAN)
        frame.pack(fill='both', expand=True)
        baslik = tk.Label(frame, text='Kayıtlı Öğrenciler', font=('Arial', 22, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK)
        baslik.pack(pady=(20, 10))
        # Veritabanından öğrencileri çek
        self.cursor.execute('SELECT ad, soyad, foto_yolu FROM Ogrenciler')
        ogrenciler = self.cursor.fetchall()
        kayitlar_frame = tk.Frame(frame, bg=ARKA_PLAN)
        kayitlar_frame.pack(pady=10, fill='both', expand=True)
        self.foto_imgler = []  # Fotoğraflar referans için
        for ad, soyad, foto in ogrenciler:
            satir = tk.Frame(kayitlar_frame, bg=ARKA_PLAN)
            satir.pack(fill='x', pady=8, padx=40)
            # Fotoğraf
            if foto and os.path.exists(foto):
                try:
                    img = Image.open(foto)
                except:
                    img = Image.new('RGB', (80, 100), color='#3949ab')
            else:
                img = Image.new('RGB', (80, 100), color='#3949ab')
            img = img.resize((80, 100))
            img_tk = ImageTk.PhotoImage(img)
            self.foto_imgler.append(img_tk)
            foto_label = tk.Label(satir, image=img_tk, bg=ARKA_PLAN)
            foto_label.pack(side='left')
            isim_label = tk.Label(satir, text=f"{ad} {soyad}", font=('Arial', 15, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK, anchor='w', width=25)
            isim_label.pack(side='left', padx=(20, 0))
        btn_geri = tk.Button(
            frame,
            text='Geri Dön',
            font=('Arial', 13),
            width=12,
            height=1,
            bg='#444',
            fg=YAZI_RENK,
            activebackground='#222',
            activeforeground=YAZI_RENK,
            bd=0,
            cursor='hand2',
            command=self._build_main_menu
        )
        btn_geri.pack(pady=20)

    def ogrenci_silme_ekrani_ac(self):
        for widget in self.winfo_children():
            widget.destroy()
        frame = tk.Frame(self, bg=ARKA_PLAN)
        frame.pack(fill='both', expand=True)
        baslik = tk.Label(frame, text='Öğrenci Sil', font=('Arial', 22, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK)
        baslik.pack(pady=(20, 10))
        self.cursor.execute('SELECT tc, ad, soyad, foto_yolu FROM Ogrenciler')
        ogrenciler = self.cursor.fetchall()
        kayitlar_frame = tk.Frame(frame, bg=ARKA_PLAN)
        kayitlar_frame.pack(pady=10, fill='both', expand=True)
        self.foto_imgler = []
        for tc, ad, soyad, foto in ogrenciler:
            satir = tk.Frame(kayitlar_frame, bg=ARKA_PLAN)
            satir.pack(fill='x', pady=8, padx=40)
            isim_label = tk.Label(satir, text=f"{ad} {soyad}", font=('Arial', 15, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK, anchor='w', width=25)
            isim_label.pack(side='left', padx=(0, 20))
            if foto and os.path.exists(foto):
                try:
                    img = Image.open(foto)
                except:
                    img = Image.new('RGB', (80, 100), color='#3949ab')
            else:
                img = Image.new('RGB', (80, 100), color='#3949ab')
            img = img.resize((80, 100))
            img_tk = ImageTk.PhotoImage(img)
            self.foto_imgler.append(img_tk)
            foto_label = tk.Label(satir, image=img_tk, bg=ARKA_PLAN)
            foto_label.pack(side='right')
            satir.bind('<Button-1>', lambda e, tc=tc, ad=ad, soyad=soyad: self.ogrenci_sil_onay(tc, ad, soyad))
            isim_label.bind('<Button-1>', lambda e, tc=tc, ad=ad, soyad=soyad: self.ogrenci_sil_onay(tc, ad, soyad))
            foto_label.bind('<Button-1>', lambda e, tc=tc, ad=ad, soyad=soyad: self.ogrenci_sil_onay(tc, ad, soyad))
        btn_geri = tk.Button(
            frame,
            text='Geri Dön',
            font=('Arial', 13),
            width=12,
            height=1,
            bg='#444',
            fg=YAZI_RENK,
            activebackground='#222',
            activeforeground=YAZI_RENK,
            bd=0,
            cursor='hand2',
            command=self._build_main_menu
        )
        btn_geri.pack(pady=20)

    def ogrenci_sil_onay(self, tc, ad, soyad):
        pencere = tk.Toplevel(self)
        pencere.title('Silme Onayı')
        pencere.geometry('400x200')
        pencere.configure(bg=ARKA_PLAN)
        label = tk.Label(pencere, text=f"{ad} {soyad} öğrencisini kalıcı olarak silmek istiyor musunuz?", font=('Arial', 13, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK, wraplength=380)
        label.pack(pady=30)
        butonlar = tk.Frame(pencere, bg=ARKA_PLAN)
        butonlar.pack(pady=10)
        btn_sil = tk.Button(butonlar, text='Sil', font=('Arial', 13, 'bold'), width=10, bg=CIKIS_RENK, fg=YAZI_RENK, activebackground=CIKIS_AKTIF, activeforeground=YAZI_RENK, bd=0, cursor='hand2', command=lambda: self.ogrenci_sil(tc, pencere))
        btn_sil.pack(side='left', padx=15)
        btn_iptal = tk.Button(butonlar, text='Silme', font=('Arial', 13, 'bold'), width=10, bg=BUTON_RENK, fg=YAZI_RENK, activebackground=BUTON_AKTIF, activeforeground=YAZI_RENK, bd=0, cursor='hand2', command=pencere.destroy)
        btn_iptal.pack(side='left', padx=15)

    def ogrenci_sil(self, tc, pencere):
        self.cursor.execute('DELETE FROM Ogrenciler WHERE tc=?', (tc,))
        self.conn.commit()
        pencere.destroy()
        messagebox.showinfo('Başarılı', 'Öğrenci silindi!')
        self.ogrenci_silme_ekrani_ac()

    def ogrenci_duzenle_ekrani_ac(self):
        for widget in self.winfo_children():
            widget.destroy()
        frame = tk.Frame(self, bg=ARKA_PLAN)
        frame.pack(fill='both', expand=True)
        baslik = tk.Label(frame, text='Öğrenci Kayıt Düzenle', font=('Arial', 22, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK)
        baslik.pack(pady=(20, 10))
        self.cursor.execute('SELECT tc, ad, soyad, foto_yolu FROM Ogrenciler')
        ogrenciler = self.cursor.fetchall()
        kayitlar_frame = tk.Frame(frame, bg=ARKA_PLAN)
        kayitlar_frame.pack(pady=10, fill='both', expand=True)
        self.foto_imgler = []
        for tc, ad, soyad, foto in ogrenciler:
            satir = tk.Frame(kayitlar_frame, bg=ARKA_PLAN)
            satir.pack(fill='x', pady=8, padx=40)
            # Fotoğraf
            if foto and os.path.exists(foto):
                try:
                    img = Image.open(foto)
                except:
                    img = Image.new('RGB', (80, 100), color='#3949ab')
            else:
                img = Image.new('RGB', (80, 100), color='#3949ab')
            img = img.resize((80, 100))
            img_tk = ImageTk.PhotoImage(img)
            self.foto_imgler.append(img_tk)
            foto_label = tk.Label(satir, image=img_tk, bg=ARKA_PLAN)
            foto_label.pack(side='left')
            isim_label = tk.Label(satir, text=f"{ad} {soyad}", font=('Arial', 15, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK, anchor='w', width=25)
            isim_label.pack(side='left', padx=(20, 0))
            satir.bind('<Button-1>', lambda e, tc=tc: self.ogrenci_duzenle_onay(tc))
            isim_label.bind('<Button-1>', lambda e, tc=tc: self.ogrenci_duzenle_onay(tc))
            foto_label.bind('<Button-1>', lambda e, tc=tc: self.ogrenci_duzenle_onay(tc))
        btn_geri = tk.Button(
            frame,
            text='Geri Dön',
            font=('Arial', 13),
            width=12,
            height=1,
            bg='#444',
            fg=YAZI_RENK,
            activebackground='#222',
            activeforeground=YAZI_RENK,
            bd=0,
            cursor='hand2',
            command=self._build_main_menu
        )
        btn_geri.pack(pady=20)

    def ogrenci_duzenle_onay(self, tc):
        pencere = tk.Toplevel(self)
        pencere.title('Düzenleme Onayı')
        pencere.geometry('400x200')
        pencere.configure(bg=ARKA_PLAN)
        self.cursor.execute('SELECT ad, soyad FROM Ogrenciler WHERE tc=?', (tc,))
        ad, soyad = self.cursor.fetchone()
        label = tk.Label(pencere, text=f"{ad} {soyad} öğrencisinin bilgilerini değiştirmek istiyor musunuz?", font=('Arial', 13, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK, wraplength=380)
        label.pack(pady=30)
        butonlar = tk.Frame(pencere, bg=ARKA_PLAN)
        butonlar.pack(pady=10)
        btn_evet = tk.Button(butonlar, text='Evet', font=('Arial', 13, 'bold'), width=10, bg=BUTON_RENK, fg=YAZI_RENK, activebackground=BUTON_AKTIF, activeforeground=YAZI_RENK, bd=0, cursor='hand2', command=lambda: [pencere.destroy(), self.ogrenci_duzenle_form(tc)])
        btn_evet.pack(side='left', padx=15)
        btn_hayir = tk.Button(butonlar, text='Hayır', font=('Arial', 13, 'bold'), width=10, bg=CIKIS_RENK, fg=YAZI_RENK, activebackground=CIKIS_AKTIF, activeforeground=YAZI_RENK, bd=0, cursor='hand2', command=pencere.destroy)
        btn_hayir.pack(side='left', padx=15)

    def ogrenci_duzenle_form(self, tc):
        self.cursor.execute('SELECT tc, ad, soyad, geldiği_okul, adres, telefon_numarası, lgs_puan, doğum_tarihi, sevdigi_ders, sevmedigi_ders, kulup, aciklama, foto_yolu FROM Ogrenciler WHERE tc=?', (tc,))
        ogr = self.cursor.fetchone()
        if ogr:
            ogr_liste = list(ogr)
            # foto_yolu'nu 13. sıradan (index 12) alıp 9. sıraya (index 8) koy
            foto_yolu = ogr_liste.pop(12)
            ogr_liste.insert(8, foto_yolu)
            # Fotoğraf alanı için sadece dosya adı göster
            if ogr_liste[8]:
                ogr_liste[8] = os.path.basename(ogr_liste[8])
            else:
                ogr_liste[8] = 'Seçilmedi'
            self.ogrenci_formu_goster(kayit_mi=False, ogrenci_veri=ogr_liste, tc_duzenle=tc)
        else:
            messagebox.showerror('Hata', 'Öğrenci bulunamadı!')

    def ogrenci_duzenle_kaydet_onay(self, tc):
        pencere = tk.Toplevel(self)
        pencere.title('Değişiklik Onayı')
        pencere.geometry('400x200')
        pencere.configure(bg=ARKA_PLAN)
        label = tk.Label(pencere, text='Değişiklikleri kaydetmek istiyor musunuz?\nEski bilgiler kalıcı olarak silinecek.', font=('Arial', 13, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK, wraplength=380)
        label.pack(pady=30)
        butonlar = tk.Frame(pencere, bg=ARKA_PLAN)
        butonlar.pack(pady=10)
        btn_devam = tk.Button(butonlar, text='Devam Et', font=('Arial', 13, 'bold'), width=10, bg=BUTON_RENK, fg=YAZI_RENK, activebackground=BUTON_AKTIF, activeforeground=YAZI_RENK, bd=0, cursor='hand2', command=lambda: self.ogrenci_duzenle_kaydet(tc, pencere))
        btn_devam.pack(side='left', padx=15)
        btn_geri = tk.Button(butonlar, text='Geri', font=('Arial', 13, 'bold'), width=10, bg=CIKIS_RENK, fg=YAZI_RENK, activebackground=CIKIS_AKTIF, activeforeground=YAZI_RENK, bd=0, cursor='hand2', command=pencere.destroy)
        btn_geri.pack(side='left', padx=15)

    def ogrenci_duzenle_kaydet(self, tc, pencere):
        try:
            ad = self.kayit_girdiler['ad'].get()
            soyad = self.kayit_girdiler['soyad'].get()
            okul = self.kayit_girdiler['geldiği_okul'].get()
            adres = self.kayit_girdiler['adres'].get()
            telefon = self.kayit_girdiler['telefon_numarası'].get()
            lgs = int(self.kayit_girdiler['lgs_puan'].get())
            dogum = int(self.kayit_girdiler['doğum_tarihi'].get())
            sevdigi_ders = self.kayit_girdiler['sevdigi_ders'].get()
            sevmedigi_ders = self.kayit_girdiler['sevmedigi_ders'].get()
            kulup = self.kayit_girdiler['kulup'].get()
            aciklama = self.kayit_girdiler['aciklama'].get()
            foto_yolu = self.foto_dosya_yolu if self.foto_dosya_yolu else ''
        except Exception as e:
            messagebox.showerror('Hata', 'Lütfen tüm alanları doğru doldurun!')
            return
        try:
            self.cursor.execute('''UPDATE Ogrenciler SET ad=?, soyad=?, geldiği_okul=?, adres=?, telefon_numarası=?, lgs_puan=?, doğum_tarihi=?, foto_yolu=?, sevdigi_ders=?, sevmedigi_ders=?, kulup=?, aciklama=? WHERE tc=?''',
                (ad, soyad, okul, adres, telefon, lgs, dogum, foto_yolu, sevdigi_ders, sevmedigi_ders, kulup, aciklama, tc))
            self.conn.commit()
            pencere.destroy()
            messagebox.showinfo('Başarılı', 'Öğrenci bilgileri güncellendi!')
            self._build_main_menu()
        except Exception as e:
            messagebox.showerror('Hata', f'Güncelleme sırasında hata oluştu: {e}')

if __name__ == '__main__':
    app = OgrenciKayitSistemi()
    app.mainloop()
    