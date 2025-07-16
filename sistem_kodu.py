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
            width=16,
            height=1,
            bg=CIKIS_RENK,
            fg=YAZI_RENK,
            activebackground=CIKIS_AKTIF,
            activeforeground=YAZI_RENK,
            bd=0,
            cursor='hand2',
            command=self.kaydet_ve_cik
        )
        cikis_btn.place(relx=1.0, rely=1.0, anchor='se', x=-30, y=-30)

    def kaydet_ve_cik(self):
        cevap = messagebox.askyesno('Çıkış', 'Kaydedip çıkmak istediğinizden emin misiniz?')
        if cevap:
            self.conn.close()
            self.destroy()

    def ogrenci_kaydet_ekrani_ac(self):
        for widget in self.winfo_children():
            widget.destroy()
        frame = tk.Frame(self, bg=ARKA_PLAN)
        frame.place(relx=0.5, rely=0.5, anchor='center')
        baslik = tk.Label(frame, text='Öğrenci Kayıt', font=('Arial', 22, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK)
        baslik.pack(pady=(0, 20))
        alanlar = [
            ('TC Kimlik No', 'tc'),
            ('Ad', 'ad'),
            ('Soyad', 'soyad'),
            ('Geldiği Okul', 'okul'),
            ('Adres', 'adres'),
            ('Telefon Numarası', 'telefon'),
            ('LGS Puanı', 'lgs'),
            ('Doğum Tarihi', 'dogum')
        ]
        self.kayit_girdiler = {}
        for label, key in alanlar:
            l = tk.Label(frame, text=label, font=('Arial', 14), bg=ARKA_PLAN, fg=YAZI_RENK)
            l.pack(anchor='w', pady=(8, 0))
            e = tk.Entry(frame, font=('Arial', 14), bg='#222a36', fg=YAZI_RENK, insertbackground=YAZI_RENK, width=32, bd=1, relief='flat')
            e.pack(pady=(0, 8), fill='x')
            self.kayit_girdiler[key] = e
        # Fotoğraf ekleme alanı
        foto_frame = tk.Frame(frame, bg=ARKA_PLAN)
        foto_frame.pack(pady=(10, 0), fill='x')
        foto_label = tk.Label(foto_frame, text='Öğrenci Fotoğrafı:', font=('Arial', 14), bg=ARKA_PLAN, fg=YAZI_RENK)
        foto_label.pack(side='left')
        self.foto_dosya_adi = tk.StringVar(value='Seçilmedi')
        self.foto_dosya_yolu = None
        foto_sec_btn = tk.Button(foto_frame, text='Fotoğraf Seç', font=('Arial', 12), bg=BUTON_RENK, fg=YAZI_RENK, activebackground=BUTON_AKTIF, activeforeground=YAZI_RENK, bd=0, cursor='hand2', command=self.fotograf_sec)
        foto_sec_btn.pack(side='left', padx=10)
        foto_adi_label = tk.Label(foto_frame, textvariable=self.foto_dosya_adi, font=('Arial', 12), bg=ARKA_PLAN, fg=YAZI_RENK)
        foto_adi_label.pack(side='left')
        btn_kaydet = tk.Button(
            frame,
            text='Kaydet',
            font=('Arial', 15, 'bold'),
            width=16,
            height=1,
            bg=BUTON_RENK,
            fg=YAZI_RENK,
            activebackground=BUTON_AKTIF,
            activeforeground=YAZI_RENK,
            bd=0,
            cursor='hand2',
            command=self.ogrenci_kaydet
        )
        btn_kaydet.pack(pady=18)
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
        btn_geri.pack()

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
            okul = self.kayit_girdiler['okul'].get()
            adres = self.kayit_girdiler['adres'].get()
            telefon = self.kayit_girdiler['telefon'].get()
            lgs = int(self.kayit_girdiler['lgs'].get())
            dogum = int(self.kayit_girdiler['dogum'].get())
            foto_yolu = self.foto_dosya_yolu if self.foto_dosya_yolu else ''
        except Exception as e:
            messagebox.showerror('Hata', 'Lütfen tüm alanları doğru doldurun!')
            return
        try:
            self.cursor.execute('''INSERT INTO Ogrenciler (tc, ad, soyad, geldiği_okul, adres, telefon_numarası, lgs_puan, doğum_tarihi, foto_yolu) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (tc, ad, soyad, okul, adres, telefon, lgs, dogum, foto_yolu))
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
            isim_label = tk.Label(satir, text=f"{ad} {soyad}", font=('Arial', 15, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK, anchor='w', width=25)
            isim_label.pack(side='left', padx=(0, 20))
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
            foto_label.pack(side='right')
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
        for widget in self.winfo_children():
            widget.destroy()
        frame = tk.Frame(self, bg=ARKA_PLAN)
        frame.place(relx=0.5, rely=0.5, anchor='center')
        baslik = tk.Label(frame, text='Öğrenci Bilgilerini Düzenle', font=('Arial', 22, 'bold'), bg=ARKA_PLAN, fg=YAZI_RENK)
        baslik.pack(pady=(0, 20))
        self.cursor.execute('SELECT tc, ad, soyad, geldiği_okul, adres, telefon_numarası, lgs_puan, doğum_tarihi, foto_yolu FROM Ogrenciler WHERE tc=?', (tc,))
        ogr = self.cursor.fetchone()
        alanlar = [
            ('TC Kimlik No', 'tc'),
            ('Ad', 'ad'),
            ('Soyad', 'soyad'),
            ('Geldiği Okul', 'okul'),
            ('Adres', 'adres'),
            ('Telefon Numarası', 'telefon'),
            ('LGS Puanı', 'lgs'),
            ('Doğum Tarihi', 'dogum')
        ]
        self.kayit_girdiler = {}
        for i, (label, key) in enumerate(alanlar):
            l = tk.Label(frame, text=label, font=('Arial', 14), bg=ARKA_PLAN, fg=YAZI_RENK)
            l.pack(anchor='w', pady=(8, 0))
            e = tk.Entry(frame, font=('Arial', 14), bg='#222a36', fg=YAZI_RENK, insertbackground=YAZI_RENK, width=32, bd=1, relief='flat')
            e.pack(pady=(0, 8), fill='x')
            e.insert(0, ogr[i])
            self.kayit_girdiler[key] = e
        # Fotoğraf ekleme alanı
        foto_frame = tk.Frame(frame, bg=ARKA_PLAN)
        foto_frame.pack(pady=(10, 0), fill='x')
        foto_label = tk.Label(foto_frame, text='Öğrenci Fotoğrafı:', font=('Arial', 14), bg=ARKA_PLAN, fg=YAZI_RENK)
        foto_label.pack(side='left')
        self.foto_dosya_adi = tk.StringVar(value=os.path.basename(ogr[8]) if ogr[8] else 'Seçilmedi')
        self.foto_dosya_yolu = ogr[8]
        foto_sec_btn = tk.Button(foto_frame, text='Fotoğraf Seç', font=('Arial', 12), bg=BUTON_RENK, fg=YAZI_RENK, activebackground=BUTON_AKTIF, activeforeground=YAZI_RENK, bd=0, cursor='hand2', command=self.fotograf_sec)
        foto_sec_btn.pack(side='left', padx=10)
        foto_adi_label = tk.Label(foto_frame, textvariable=self.foto_dosya_adi, font=('Arial', 12), bg=ARKA_PLAN, fg=YAZI_RENK)
        foto_adi_label.pack(side='left')
        btn_kaydet = tk.Button(
            frame,
            text='Kaydet',
            font=('Arial', 15, 'bold'),
            width=16,
            height=1,
            bg=BUTON_RENK,
            fg=YAZI_RENK,
            activebackground=BUTON_AKTIF,
            activeforeground=YAZI_RENK,
            bd=0,
            cursor='hand2',
            command=lambda: self.ogrenci_duzenle_kaydet_onay(tc)
        )
        btn_kaydet.pack(pady=18)
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
            command=self.ogrenci_duzenle_ekrani_ac
        )
        btn_geri.pack()

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
            okul = self.kayit_girdiler['okul'].get()
            adres = self.kayit_girdiler['adres'].get()
            telefon = self.kayit_girdiler['telefon'].get()
            lgs = int(self.kayit_girdiler['lgs'].get())
            dogum = int(self.kayit_girdiler['dogum'].get())
            foto_yolu = self.foto_dosya_yolu if self.foto_dosya_yolu else ''
        except Exception as e:
            messagebox.showerror('Hata', 'Lütfen tüm alanları doğru doldurun!')
            return
        try:
            self.cursor.execute('''UPDATE Ogrenciler SET ad=?, soyad=?, geldiği_okul=?, adres=?, telefon_numarası=?, lgs_puan=?, doğum_tarihi=?, foto_yolu=? WHERE tc=?''',
                (ad, soyad, okul, adres, telefon, lgs, dogum, foto_yolu, tc))
            self.conn.commit()
            pencere.destroy()
            messagebox.showinfo('Başarılı', 'Öğrenci bilgileri güncellendi!')
            self._build_main_menu()
        except Exception as e:
            messagebox.showerror('Hata', f'Güncelleme sırasında hata oluştu: {e}')

if __name__ == '__main__':
    app = OgrenciKayitSistemi()
    app.mainloop()
    