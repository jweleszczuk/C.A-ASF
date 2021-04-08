# -*- coding: utf-8 -*-
"""
Plik powstał na rzecz pracy licencjackiej :
"Symulacja Afrykańskiego Pomoru Świń za pomocą automatów komórkowych".
Program służy generowaniu plików konfiguracyjnych, przeprowadzaniu bazującej 
na nich symulacji oraz analizie plików wynikowych.
Możliwe jest wykonywanie etapów wymienionych w manualu zarówno za pomocą
interfejsu graficznego, jak i ręcznego wprowadzania komend.
Autorem tego skryptu jest Jarosław Wełeszczuk.
"""



import random
from PIL import Image,ImageDraw
import multiprocessing  as mp
import imageio
import copy 
import os.path
from os import path
import wx
from wx.adv import Animation, AnimationCtrl
from datetime import datetime
import math


nazwa_wczytanego_słownika=""

słownik={
    #ogólne ustawienia dla planszy, oraz główne parametry symulacji
    "nazwa_pliku_z_generacjami":"Generacje_test.txt",
    "ilość_cykli":5040,
    "ile_k_pion":100,
    "ile_k_poziom":100,
    "szer_kom":8,
    "ile_alive":800, 
    "ile_inkub":2,
    "All_licznik":0,
    "Cell_live":99999, 
    "Cell_move_time":7,
    "Draw_move_time":False,
    "Cell_range_move_time":(4,10),
    "Draw_Cell_Live":False,
    "Draw_Cell_c_mortality_rate":False,
    
    "Cell_Alive_live":4300,
    "Draw_Cell_Alive_live":(3600,5040),# 10-14 lat
    "Cell_Alive_c_move":0.5,

    "Cell_Ill_Peracute_live":2,
    "Draw_Cell_Ill_Peracute_live":(1,3),
    "Cell_Ill_Peracute_c_poison":0.75,
    "Cell_Ill_Peracute_c_move":0.5,
    
    "Cell_Ill_Acute_live":10,
    "Draw_Cell_Ill_Acute_live":(6,13),
    "Cell_Ill_Acute_c_poison":0.6,
    "Cell_Ill_Acute_c_move":0.5,  
    "Draw_Cell_Ill_Acute_c_mortality_rate":(0.9,1.0),
    "Cell_Ill_Acute_c_mortality_rate":0.95,
    
    "Cell_Ill_Subacute_live":30,
    "Draw_Cell_Ill_Subacute_live":(15,45), 
    "Cell_Ill_Subacute_c_poison":0.45,
    "Cell_Ill_Subacute_c_move":0.5,
    "Draw_Cell_Ill_Subacute_c_mortality_rate":(0.3,0.7),
    "Cell_Ill_Subacute_c_mortality_rate":0.5,
    
    "Cell_Ill_Chronic_live":205, 
    "Draw_Cell_Ill_Chronic_live":(60,450),
    "Cell_Ill_Chronic_c_become_vector":0.013, 
    "Cell_Ill_Chronic_c_poison":0.15,
    "Cell_Ill_Chronic_c_move":0.5,
    "Draw_Cell_Ill_Chronic_c_mortality_rate":(0.1,0.3),
    "Cell_Ill_Chronic_c_mortality_rate":0.2,
    
    #faza inkubacji
    "Cell_Incubating_live":15,
    "Draw_Cell_Incubating_live":(4,19),
    "Cell_Incubating_c_move":0.5,

    # żywy zaraziciel
    
    "Cell_Cured_Infectious_live":4320,
    "Draw_Cell_Cured_Infectious_live":(3600,5040),
    "Cell_Cured_Infectious_c_move":0.5,
    "Cell_Cured_Infectious_c_poison":0.15,
    
    #wyzdrowiała
    
    "Cell_Cured_live":4300,
    "Draw_Cell_Cured_live":(3600,5040),
    "Cell_Cured_c_move":0.5,
    #2 rodzaje martwych osobnikow
    
    "Cell_Dead_live":294,
    "Draw_Cell_Dead_live":(210,378),
    
    "Cell_Dead_Ill_live":98,
    "Draw_Cell_Dead_Ill_live":(70,126),
    "Cell_Dead_Ill_c_poison":0.1,
    }
class Okno_glowne(wx.Frame):
    """
    Klasa głównego okna,stanowiąca trzon interfejsu programu.
    """
    def __init__(self, parent=None):
        """
        Konstruktor klasy Okno_glowne.
        """
        super(Okno_glowne, self).__init__(parent)
        self.InitUI()

    def InitUI(self): 
        """
        Metoda odpowiadająca za formę i widżety okna.
        """
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)
        panel=wx.Panel(self, wx.ID_ANY)
        fileMenu = wx.Menu()
        
        fileItem1 = fileMenu.Append(wx.ID_ANY, 'Stwórz losowe środowisko')
        fileItem2 = fileMenu.Append(wx.ID_ANY, 'Wczytaj środowisko')
        fileItem3 = fileMenu.Append(wx.ID_ANY, 'Zapisz środowisko')
        fileItem4 = fileMenu.Append(wx.ID_ANY, 'Zamknij program')
        menubar.Append(fileMenu, 'Środowisko symulacji')                       
        self.Bind(wx.EVT_MENU, self.wx_stwórz_losowe_środowisko, fileItem1)
        self.Bind(wx.EVT_MENU, self.wx_wczytaj_wczytaj_stan_początkowy, fileItem2)
        self.Bind(wx.EVT_MENU, self.wx_zapisz_stan_początkowy, fileItem3)
        self.Bind(wx.EVT_MENU, self.wx_zamknij, fileItem4)
        
        editMenu=wx.Menu()
        editItem1 = editMenu.Append(wx.ID_ANY," Wyświetl słownik" )
        editItem2 = editMenu.Append(wx.ID_ANY," Zapisz słownik" )
        editItem3 = editMenu.Append(wx.ID_ANY," Wczytaj słownik" )
        menubar.Append(editMenu, 'Parametry')
        self.Bind(wx.EVT_MENU, self.wx_wyświetl_słownik, editItem1)
        self.Bind(wx.EVT_MENU, self.wx_zapisz_słownik, editItem2)
        self.Bind(wx.EVT_MENU, self.wx_wczytaj_słownik, editItem3)
        
        
        self.Przycisk_1 = wx.Button(panel,-1,"Stwórz początkową planszę",pos=(10,20),size=(200,100)) 
        self.Przycisk_1.Bind(wx.EVT_BUTTON,self.wx_pokaż_początkową_planszę) 
        self.Przycisk_2 = wx.Button(panel,-1,"Uruchom symulację",pos=(10,140),size=(200,100)) 
        self.Przycisk_2.Bind(wx.EVT_BUTTON,self.wx_uruchom_symulację)
        self.Przycisk_3 = wx.Button(panel,-1,"Wyświetl animację",pos=(10,260),size=(200,100)) 
        self.Przycisk_3.Bind(wx.EVT_BUTTON,self.wx_wyświetl_animację)
        self.Przycisk_4 = wx.Button(panel,-1,"Uruchom analizę",pos=(10,380),size=(200,100)) 
        self.Przycisk_4.Bind(wx.EVT_BUTTON,self.wx_rozpocznij_analize)
        self.Przycisk_4 = wx.Button(panel,-1,"Okno dla wielkrotnych\n symulacji i analiz",pos=(300,190),size=(200,150)) 
        self.Przycisk_4.Bind(wx.EVT_BUTTON,self.wx_wyświetl_okno_wielkrotne)
        
        self.SetSize((600, 600))
        self.SetTitle('Symulator ASF')
        self.Centre()
        self.maxPercent = 100
        self.percent = 0

    def wx_wyświetl_okno_wielkrotne(self,evt):
        """
        Powoduję wywołania instacji klasy Okno_wielkokrotnej_analizy()
        
        Parameters:
        -------
        evt: Wywołanie poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Wyswietlenie okna.
        """
        ok4=Okno_wielokrotnej_analizy(Okno_glowne(self))
        ok4.Show()
    
    def wx_rozpocznij_analize(self,evt):
        """
        Pośredniczy pomiędzy użyciem widżetu, sprawdzeniem czy są spełnione 
        okreslone warunki przed rozpoczęciem analizy pliku. W przeciwnym razie 
        wyswietla stosowny komunikat.

        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.

        Wynik
        -------
        Rozpoczęcie procesu analizy.

        """
        war=self.wx_test_do_pokaż_początkową_planszę()
        if type(war)!=int:
             self.wx_analiza_pojedyńcza()
        else:
           self.wx_wyświetl_wiadomość(self.wx_kod_komunikatów(war),"error")
           

    def wx_zniszcz_pasek_postępu(self):
        """
        Zdalnie niszczy wywołane okno postepu.
        """
        self.progress.Destroy()

    def wx_uruchom_symulację(self,evt):
        """
        Pośredniczy pomiędzy użyciem widżetu, sprawdzeniem czy są spełnione okreslone warunki przed uruchomienim symulacji i wywołuje ją.
        W przypadku nie spełnionych wymagań, zamiast symulacji wywołuje okno z wiadomością o błędzie.

        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        """
        war=self.wx_test_do_pokaż_początkową_planszę()
        if type(war)!=int:
            self.wx_symulacja()
        else:
            self.wx_wyświetl_wiadomość(self.wx_kod_komunikatów(war),"error")
        
    def wx_symulacja(self):# wczytuje ze 
        """
        Poprzez wywołanie okna z paskiem postepu, obrazuje ono użytkownikowi
        postęp procesu, adekwatny do ilości przerobionej do zadanej. Wartości
        potrzebne dla symulacji pobierane są ze słownika. Metoda ta pobiera 
        nazwę pliku ze wskazanym środowiskiem a nastepnie dopisuję do niego 
        kolejne linie, gdzie każda z lini to następująca po sobie sytuacja na 
        planszy po ubiegu 1 jednostki czasu. Efektem końcowym jest plik z 
        symbolami instacji osobników dla każdego z cyklów i komunikat w okienku 
        informacyjnym o zakończeniu procesu. Sama symulcja odbywa się poprzez 
        losowy wybór obiektu, wywołaniu wspólnej funkcji decyzyjnej o indywidulanej
        dla każdej klasy meotdach i usunięciu jego współrzędnych z tego cyklu 
        by ujednolicićilość akcji wykonywanych przez wszystkie osobniki do 1.
        Każdy skończony cykl kończy się dopisaniem do pracującego pliku ciągu 
        znaków reprezentujących każdy z obiektów w jednej jednostce czasu.

        Wynik
        -------
        Plik *.txt z zapisem przebiegu symulacji.
        """
        self.progress = wx.ProgressDialog("Operacja w toku", "proszę czekać", maximum=self.maxPercent, parent=self, style=wx.PD_SMOOTH|wx.PD_AUTO_HIDE)
        il_cyklów=słownik["ilość_cykli"]
        taskPercent_upd=100/il_cyklów
        taskPercent = taskPercent_upd
        m=słownik["nazwa_pliku_z_generacjami"]
        lista=wczytaj_stan_początkowy(m)
        os.remove(m)
        with open(m,"w") as f:
            K_N=1
            warstwa_1=lista # podstawka
            ca2=znaki(warstwa_1)
            f.write(str(ca2)+"\n") # zapisz generacje
            współrzędne=[] 
            współrzędne2=[]
            for n in range(0,len(warstwa_1)):
                for z in range(0,len(warstwa_1[0])):
                    współrzędne.append([n,z])       
            while K_N< il_cyklów: # dopóty nie przjedzie cyklów
                warstwa_2=warstwa_1.copy()
                współrzędne2=współrzędne.copy()
                while len(współrzędne2)!=0:
                    qqq=random.choice((współrzędne2))
                    n=qqq[0]
                    z=qqq[1]
                    wsp_akt=warstwa_1[n][z].wybór(n,z,warstwa_1,warstwa_2) 
                    if wsp_akt[0] in współrzędne2:
                        współrzędne2.remove(wsp_akt[0])
                        warstwa_1[n][z].starzenie(wsp_akt[0][0],wsp_akt[0][1],warstwa_2)# wymagane w przypadku ruchu osobnika na pole z tura
                    else:
                        współrzędne2.remove(wsp_akt[1])
                        warstwa_1[n][z].starzenie(wsp_akt[1][0],wsp_akt[1][1],warstwa_2)# wymagane w przypadku ruchu osobnika na pole ktore mialo wczesniej wybor
                #skończyło całą listę
                ca2=znaki(warstwa_2)
                f.write(str(ca2)+"\n") # zapisz generacje
                warstwa_1=warstwa_2.copy()
                K_N+=1
                taskPercent +=taskPercent_upd
                self.progress.Update(taskPercent, ("{} / {}".format(K_N,il_cyklów) ))

                
        self.wx_zniszcz_pasek_postępu()
        self.wx_wyświetl_wiadomość("Ukończono symulację", "info")
       
    def wx_test_do_wyświetl_animację(self):
        """
        Sprawdza czy spełnione zostały wymogi do wyświetlenia animacji:
        Istnieje plik o nazwie wskazanej w słowniku;
        Zgadza się zadeklarowana iloć pól z ilocią obiektów we wspomnianym pliku.
        Istnieje czysta plansza w formacie BMP o wymiarach ze słownika
        W przypadku negatynwego wyniku zwraca kod błędu.
        
        Wynik
        -------
        Kod błędu.
        """
        if path.exists(słownik["nazwa_pliku_z_generacjami"]):
            if słownik["ile_k_pion"]*słownik["ile_k_poziom"]==len(znaki(wczytaj_stan_początkowy(słownik["nazwa_pliku_z_generacjami"]))): 
                if path.exists("Generacja_0.bmp"):
                    return True
                else:
                    return 3
            else:
                return 2
        else:
            return 1
    def wx_test_do_pokaż_początkową_planszę(self):
        """
        Sprawdza czy spełnione zostały wymogi, wspólne dla uruchomienia 
        symulacji i wyświetlenia planszy początkowej, ponieważ każde wywołanie 
        metody pokazującej planszę skutkuje każdorazym kolorowaniem mapy 
        wyjściowej "Generacja_0.bmp". W związku z tym sprawdzana czy:
        Istnieje plik o nazwie wskazanej w słowniku;
        Zgadza się zadeklarowana iloć pól z ilocią obiektów we wspomnianym pliku.
        W przypadku negatynwego wyniku zwraca kod błędu.

        Wynik
        -------
        Kod błędu.
        """
        if path.exists(słownik["nazwa_pliku_z_generacjami"]):
            if słownik["ile_k_pion"]*słownik["ile_k_poziom"]==len(znaki(wczytaj_stan_początkowy(słownik["nazwa_pliku_z_generacjami"]))):
                return True
            else:
                return 2
        else:
            return 1

    
    def wx_stwórz_gifa(self):
        """
        Za pomocą głównej pętli sterującej każda linia z wczytanego pliku,
        ze znakowym zapisaem stanu jednostki czasudanej symulacji, 
        jest rozdzielana za pomocą multiprocesingu na są procesy potomne w 
        postaci argumentu dla funkcji koloruj mapę. Każdy proces potomny 
        skutkuje wyprodukowaniem 1 mapy, która ilustruje zadany moment 
        symulacji. Mapy te są zostająpo zwórceniu ze wspomnianej funckji
        odrazu wstawiane w odpowiednie miejsce wcześniej spreparowanej lsity
        "wyniki", poprzez zamianę pustego elementu o indeksie odpowiadającym 
        numerowi stworzonemu procesu.

        Wynik
        -------
        Tworzy plik nazwie "movie_ASF.gif".
        """
        self.progress = wx.ProgressDialog("Operacja w toku", "proszę czekać", maximum=self.maxPercent, parent=self, style=wx.PD_SMOOTH|wx.PD_AUTO_HIDE)
        taskPercent_upd=1
        taskPercent = 0
        self.progress.Update(taskPercent, ("0"+"/"+"1" ))
        kolejka=mp.Queue()
        procesy=[]
        wyniki=stw_liste(słownik["ilość_cykli"])
        with open(słownik["nazwa_pliku_z_generacjami"]) as f: # jest tylko 1  otawrcie pliku zmiast każdrazowego przy wywołaniu funkcji
            for x in range(0,słownik["ilość_cykli"]):
                f.seek((słownik["ile_k_poziom"]*słownik["ile_k_pion"]+2)*x)# +2 ze względu na "\n" na końcu lini
                txt_generacji=f.readline().replace('\n', '')
                p=mp.Process(target=koloruj_mapę,args=("Generacja_0.bmp",txt_generacji,str(x),słownik["szer_kom"],słownik["ile_k_poziom"],kolejka,))
                p.start()
                procesy.append(p)
        for i in range(0,len(procesy)):
            a=kolejka.get()
            wyniki[int(a[1])]=a[0] #### zmiana
        for x in procesy:
            x.join() 
        taskPercent +=taskPercent_upd
        self.wx_zniszcz_pasek_postępu()
        self.wx_wyświetl_wiadomość("Ukończono animację", "info")
        z_gifa(wyniki) 

    def wx_wyświetl_animację(self,evt):
        """
        Wywołe metodę sprawdzającą wx_test_do_wyświetl_animację.
        W przypadku negatynwego wyniku wyświetlna wiadmość w oknie dialogowym.
        Pozytywny rezultat powoduje sprawdzenie czy istnieje już plik z animacją.
        Użytkownik zostaje zapytany czy chce stworzyć nową animację i tym samym
        nadpisać istniejącą, zobaczyć aktualną. Natępuje wywołanie klasy 
        Okno_animacji i wyświetenie na obiekcie.
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        """
        war=self.wx_test_do_wyświetl_animację()
        if type(war)!=int:
            if path.exists("movie_ASF.gif"):
                dialog = wx.MessageDialog(self,"Tak = Stwórz nową i nadpisz aktualną\nNie= wyświetl istniejącą.","Istnieje już plik animacji", style = wx.YES_NO)
                if dialog.ShowModal() == wx.ID_YES:
                    self.wx_stwórz_gifa()
            else:
                self.wx_stwórz_gifa()
            ok3=Okno_animacji()
            ok3.Show()
        else:
            self.wx_wyświetl_wiadomość(self.wx_kod_komunikatów(war),"error")
        
    def wx_zamknij(self,evt):
        """
        Metoda zamykająca Obiekt Okno_glowne i tym samym wszystkie instancje
        obiektów potomnych.

        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.

        Wynik
        -------
        Zamyka program.
        """
        dialog = wx.MessageDialog(self,"Czy na pewno?","Kończymy pracę", style = wx.OK|wx.CANCEL)
        x = dialog.ShowModal()
        if x == wx.ID_OK:
            self.Close()
    
    def wx_stwórz_losowe_środowisko(self,evt):
        """
        Pobiera wartości ze słownika, wywołuje globalną funkcję stw_macierz_losowa
        i zapisuje wygenerowane środowisko pod nazwą ustaloną nazwą w słowniku.

        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.

        Wynik
        -------
        Zapisuje przechowywane w pamięci środowisko.
        """
        macierz=stw_macierz_losowa(słownik["ile_k_poziom"],słownik["ile_k_pion"],słownik["ile_alive"], słownik["ile_inkub"]) #tworzy podstawową macierz z osobnikami
        zapisz_stan_poczatkowy(macierz,słownik["nazwa_pliku_z_generacjami"])

        
    def wx_wczytaj_wczytaj_stan_początkowy(self,evt):
        """
        Wyświetla okno wyboru pliku. Po jego wybraniu aktualizuje w słowniku 
        pozycję "nazwa_pliku_z_generacjami" na wskazany przez użytkownika.
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.

        Wynik
        -------
        Zmienia aktualne parametry słownika.
        """
        dialog=wx.FileDialog(self,message='Wybierz plik generacji',defaultFile='',wildcard='*.TXT',style=wx.FD_OPEN, pos=(10,10))
        if dialog.ShowModal() == wx.ID_OK:
            sciezka = dialog.GetPaths()
            global słownik
            słownik["nazwa_pliku_z_generacjami"]=sciezka[0]
            dialog.Destroy()
                
    def wx_zapisz_stan_początkowy(self,evt):#################
        """
        Zapisuje ciąg znaków reprezentujących osobniki z pliku o domyślenj 
        nazwie ze słownika pod wskazaną przez użytkownika. W przypadku istnienia
        już takiego pliku modyfikuje jego nazwe i wyświetla o tym komuniakt.

        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Zapisuje plik ze znakową reprezentacją aktualnego środowiska.
        """
        pop=wx.TextEntryDialog(self,"Podaj nazwę dla pliku ze stanem początkowym : ")

        
        nnn=nazwa_wczytanego_słownika.replace("Slownik", "Srodowisko")
        pop.SetValue(nnn)
        pop.ShowModal()
        nazwa=pop.GetValue() # GetValue do okienek
        
        if "Srodowisko" not in nazwa:
            nazwa="Srodowisko_"+nazwa
        if ".txt" not in nazwa:
            nazwa=nazwa+".txt"
        if path.exists(nazwa):
            nazwa2=nazwa.split(".")
            nazwa=nazwa2[0]+"_nowa_nazwa_generacji.txt"
            self.wx_wyświetl_wiadomość(("Podana nazwa jest już zajęta.\n Stan początkowy został zapisany jako "+nazwa),"warning")
            
        macierz=wczytaj_stan_początkowy( słownik["nazwa_pliku_z_generacjami"])
        zapisz_stan_poczatkowy(macierz,nazwa)
    
    def wx_wyświetl_słownik(self,evt):
        """
        Powoduje wyświetlenie się nie modyfikowalnego okna dialogowego ze
        wszystkimi wartościami z aktualnie używanego słownika.

        Parameters
        ----------
        evt :  Wywołane poprzez kliknięcie na widżet.

        Wynik
        -------
        Wyświetlenie okna z wartościami słownika.
        """
        tekst=""
        for name, value in słownik.items():
            tekst=tekst+name+" : "+str(value)+"\n"
        self.wx_wyświetl_wiadomość(tekst,"Paretry symulacjii")
        
    def wx_zapisz_słownik(self,evt):
        """
        Zapisuje wszystkimi wartościami z aktualnie używanego słownika pod 
        wskazaną przez użytkownika nazwą. W przypadku istnienia
        już takiego pliku modyfikuje jego nazwe i wyświetla o tym komuniakt.

        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.

        Wynik
        -------
        Zapisuje parametry słownika w pliku ".txt".
        """
        pop=wx.TextEntryDialog(self,"Podaj nazwę dla słownika : ")
        pop.ShowModal()
        nazwa=pop.GetValue() # GetValue do okienek
        if "Slownik" not in nazwa:
            nazwa="Slownik_"+nazwa
        if ".txt" not in nazwa:
            nazwa=nazwa+".txt"
        if path.exists(nazwa):
            nazwa2=nazwa.split(".")
            nazwa=nazwa2[0]+"_nowa_nazwa_slownika.txt"
            self.wx_wyświetl_wiadomość(("Podana nazwa jest już zajęta.\n Słownik został zapisany jako "+nazwa),"warning")
        zapisz_słownik(nazwa,słownik)
    
    def wx_wczytaj_słownik(self,evt):
        """
        Zmienia aktualnie użytkowany słownik poprzez podmienienie go na nowego,
        wskazanego przez użytkownika w oknie wyboru pliku.

        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.

        Wynik
        -------
        Zmienia parametry słownika na te z pliku.
        """
        dialog=wx.FileDialog(self,"Wybierz plik słownika",defaultFile='',wildcard='*.TXT',style=wx.FD_OPEN, pos=(10,10))
        if dialog.ShowModal() == wx.ID_OK:
            sciezka = dialog.GetPaths()
            global słownik
            global nazwa_wczytanego_słownika
            nazwa_wczytanego_słownika = (sciezka[0].split("\\")[-1])
            słownik=wczytaj_słownik(sciezka[0]) 
            dialog.Destroy()
                
    def wx_kod_komunikatów(self,kod):
        """
        Metoda wykorzystywana przy testach przed wywołaniem wx_test_do_....

        Parameters
        ----------
        kod (int) : wartość liczbowa, przypisana do każdego z przewidzianych
                    problemów, które mogą wyniknąc podczas użytkowania.

        Wynik
        -------
        Wyświetla komunikat (str) : wiadmość adekwatną do kodu
        """
        słownik_kodów={
            1: "Brak pliku z Generacjami w folderze.\n Proszę stworzyć, albo wczytać środowisko.",
            2: "Niezgodność ilości obiektów w parametrach, a w macierzy.\n Proszę sprawdzić dane.",
            3: "Brak planszy początkowej Generacja_0.bmp w folderze.\n Proszę stworzyć początkową planszę",
            4: "Brak pliku z animacją movie_ASF.gif w folderze.\n Proszę uruchomić symulację"
            }

        return (słownik_kodów[kod])
    def wx_wyświetl_wiadomość(self,wiadomość,tryb):
        """
        Wyświetla okno dialogowe z wartościami argumentów.

        Parameters
        ----------
        wiadomość (str): komunikat do przekazania użytkownikowi
        tryb (str) : odpowiada stylowu okna. 

        Wynik
        -------
        Okno z komunikatem.
        """
        if tryb=="error":
            styl= wx.ICON_ERROR
        elif tryb=="warning":
            styl= wx.ICON_WARNING
        elif tryb=="info":
            styl= wx.ICON_INFORMATION
        else:
            styl= wx.ICON_NONE        
        powiadomienie1=wx.MessageDialog(None,message=wiadomość,style = wx.OK | styl )
        powiadomienie1.ShowModal()
        
    def wx_pokaż_początkową_planszę(self,evt):
        """
        Generuje bitmapę wizualizującą stan początkowej planszy dla zadanej
        symulacji i wyświetla ją na obiekcie klasy "Okno_planszy_początkowej"
        W przypadku komplikacji wyświetla stosowną do problemu wiadomość w 
        oknie dialogowym.

        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.

        Wynik
        -------
        Wyświetla okno z bitmapa.
        """
        war=self.wx_test_do_pokaż_początkową_planszę()
        if type(war)!=int:
            stw_planszę_początkową()
            macierz=znaki(wczytaj_stan_początkowy(słownik["nazwa_pliku_z_generacjami"]))
            koloruj_mapę_tylko_początkową(macierz)
            ok2=Okno_planszy_początkowej()
            ok2.Show()
        else:
            self.wx_wyświetl_wiadomość(self.wx_kod_komunikatów(war),"error")   
            
    def wx_analiza_pojedyńcza(self):
        """
        Analizuję wskazany plik i produkuje nastepujące statystyki:
            - zachorowalność (int) : ilość zarażonych / dzień
            - zasieg (int) : ile przybyło zarażonych miejsc / dzień
            - łączną ilość zarażonych (int) / dzień
            - śmiertelność  (int) : łączne zgony spowodowane wirusem /od początku do tego dnia
            
        Parameters
        ----------
        nazwa (str) : nazwa pliku który będzie analizowany.
        
        Wynik
        -------
        Plik ".txt"
        """
        nazwa=słownik["nazwa_pliku_z_generacjami"]
        lista_generalna=[] # 
        licznik=0 # warunkuje wyliczanie pozycji .seek()
        lista_współrzędnych_inf=[] # koordynaty 
        l_23=[]
        lista_współrzędnych_martwych_inf=[]
        lista_generacji=[0,0,0,0,0,0,0,0,0,0,0] # ile było każdego typu na generację
                        #x,o,v,q,p,a,s,c,d,n,k
        l_pom=[]
        with open(nazwa,"r") as f:
            ile_znaków=len(f.readline().replace('\n', '')) # ile jest obiektow
            pierw=int(math.sqrt(ile_znaków)) # ile jest znakow na "rząd"
            while True :   
                f.seek((ile_znaków+2)*licznik)# +2 ze względu na "\n" na końcu lini
                txt_generacji=f.readline()
                if not txt_generacji :
                    break
                else:
                    txt_generacji.replace('\n', '')
                n_1=0 #koordynat 1
                for x in range(0,len(txt_generacji),pierw):
                    x_2=0 #koordynat 2
                    for kom in (txt_generacji[x:x+pierw]):
                        if kom =="x":  #puste pole
                            lista_generacji[0]+=1
                        elif kom=="o":   #zdrowa
                            lista_generacji[1]+=1
                        elif kom=="v":  #nosiciel
                            lista_generacji[2]+=1
                        elif kom=="q":     #inkub
                            lista_generacji[3]+=1
                            element=(n_1,x_2)
                            if element not in l_pom:
                                lista_współrzędnych_inf.append(element)
                                l_pom.append(element)
                        elif kom =="p":#peracute
                            lista_generacji[4]+=1
                        elif kom =="a":#acute
                            lista_generacji[5]+=1 
                        elif kom =="s": #subacute
                            lista_generacji[6]+=1
                        elif kom =="c":#chronical
                            lista_generacji[7]+=1
                        elif kom=="d":   #dead
                            lista_generacji[8]+=1
                        elif kom=="n":   #dead_ill
                            lista_generacji[9]+=1
                            element=(n_1,x_2)
                            if element not in lista_współrzędnych_martwych_inf:
                                lista_współrzędnych_martwych_inf.append(element)
                        elif kom=="k": #cured
                            lista_generacji[10]+=1 
                        x_2+=1
                    n_1+=1
                l_23.append(int(len(lista_współrzędnych_inf)))
                lista_łącząca=[lista_generacji,l_23]  
                lista_generalna.append(lista_łącząca)
                lista_generacji=[0,0,0,0,0,0,0,0,0,0,0] # ile było każdego typu na generację 
                lista_współrzędnych_inf=[]
                licznik+=1
        zamrło_na_chorob=len(lista_współrzędnych_martwych_inf) / lista_generalna[0][0][1]
        l_zachorowalności=[]
        for x in range(len(lista_generalna)): # patrze na dni po kolei
            try:
                r_zdrowych=abs((lista_generalna[x][0][1]-lista_generalna[x-1][0][1])) #moze sie tylko zmniejszac
                r_truchl_norm=(lista_generalna[x][0][8]-lista_generalna[x-1][0][8]) # jezeli przybylo to bedzie na plusie
                r_pustych=(lista_generalna[x][0][0]-lista_generalna[x-1][0][0]) # moze tylko sie zwiekszac
                suma=r_truchl_norm+r_pustych
                if suma > r_zdrowych:
                    zqwr=r_zdrowych
                else:
                   zqwr= r_zdrowych-(r_truchl_norm +r_pustych)
                l_zachorowalności.append(zqwr)
            except:
                l_zachorowalności.append(0)
        l_zaraz_w_czasie=0
        l_zachorowalności[0]=0
        nazwa2="Analiza_"+nazwa
        napis0="Dzień;Zasięg;Zachorowania;Łącznie_zarażonych\n"
        with open(nazwa2,'w') as f:
            f.write(napis0)
            for x in range(len(lista_generalna)):
                f.write("Dzień_"+str(x)+";"+str(l_23[x])+";"+str(l_zachorowalności[x])+";"+str(l_zaraz_w_czasie)+"\n") # zapisz generacje 
                l_zaraz_w_czasie+=l_zachorowalności[x]
            napis1="Śmiertelność : "+str(zamrło_na_chorob)+"\n"
            f.write(napis1)
                
class Okno_planszy_początkowej(wx.Frame):     
    """
    Klasa okna stanowiąca miejsce wyświetlania  wizualizacji planszy początkowej.
    """
    def __init__(self, parent=None):
        """
        Konstruktor klasy Okno_glowne.
        """
        super(Okno_planszy_początkowej, self).__init__(parent)
        self.InitUI()
        
    def InitUI(self):   
        """
        Metoda odpowiadająca za formę i widżety okna.
        """
        self.zdj=wx.Bitmap("Plansza_początkowa.bmp", wx.BITMAP_TYPE_ANY)
        self.png = wx.StaticBitmap(self, -1, wx.Bitmap("Plansza_początkowa.bmp", wx.BITMAP_TYPE_ANY))
        Height=self.zdj.GetHeight()
        Width=self.zdj.GetWidth()
        self.SetSize(Width+30,Height+40)
        self.Centre()    
        self.SetTitle('Podgląd planszy początkowej')
    
class Okno_animacji(wx.Frame):
    """
    Klasa której jedynym celem jesy utworzenie nowego okna i ustawienie 
    animacji jako tło.
    """
    def __init__(self, parent=None):
        """
        Konstruktor klasy Okno_animacji.
        """
        super(Okno_animacji, self).__init__(parent)
        self.InitUI()

    def InitUI(self):   
        """
        Metoda odpowiadająca za formę i widżety okna.
        """
        sizer = wx.BoxSizer(wx.VERTICAL)
        anim = Animation('movie_ASF.gif')
        ctrl = AnimationCtrl(self, -1, anim)
        ctrl.Play()
        sizer.Add(ctrl)
        self.SetSizerAndFit(sizer)
        self.Centre()    
        self.SetTitle('Podgląd animacji')
        self.Show()
        
class Okno_wielokrotnej_analizy(wx.Frame): #
    """
    Klasa Okno_wielokrotnej_analizy, która zawiera wszystkie metody skonstruowane pod kątem szeregowych
    symulacji i analiz.
    """
    def __init__(self,parent):
        """
        Konstruktor klasy Okno_wielokrotnej_analizy.
        """
        super(Okno_wielokrotnej_analizy, self).__init__(parent=parent)
        self.InitUI()
        
    def InitUI(self):   
        """
        Metoda odpowiadająca za formę i widżety okna.
        """
        self.SetSize(800,900)
        self.SetTitle('Ustawienia wielokrotnej analizy')
        panel2=wx.Panel(self)
        
        self.Lista_Plansz=wx.ListBox(panel2, pos=(10,20), size=(230,200)) # sekw do wybrania
        self.text_l_p = wx.StaticText(panel2,-1 , label='Środowiska', pos=(100, 5))
        self.Przycisk_1 = wx.Button(panel2,-1,"+",pos=(10,230),size=(50,50)) #(szerokosc, wysokoksc)
        self.Przycisk_1.Bind(wx.EVT_BUTTON,self.wx_dodaj_plansze)
        self.Przycisk_2 = wx.Button(panel2,-1,"-",pos=(70,230),size=(50,50)) 
        self.Przycisk_2.Bind(wx.EVT_BUTTON,self.wx_usuń_planszę)
        self.Przycisk_3 = wx.Button(panel2,-1,"^",pos=(130,230),size=(50,50)) 
        self.Przycisk_3.Bind(wx.EVT_BUTTON,self.wx_przesun_w_górę_plansze)  
        self.Przycisk_4 = wx.Button(panel2,-1,"v",pos=(190,230),size=(50,50)) 
        self.Przycisk_4.Bind(wx.EVT_BUTTON,self.wx_przesun_w_dół_plansze) 
        self.Przycisk_19 = wx.Button(panel2,-1,"Wczytaj spis środowisk z pliku ",pos=(10,290),size=(230,80)) 
        self.Przycisk_19.Bind(wx.EVT_BUTTON,self.wx_wczytaj_pliki_srodowisk)
        
        self.Lista_Parametry=wx.ListBox(panel2, pos=(260,20), size=(230,200))
        self.text_l_p2 = wx.StaticText(panel2,-1 , label='Parametry', pos=(340, 5))
        self.Przycisk_5 = wx.Button(panel2,-1,"+",pos=(260,230),size=(50,50)) 
        self.Przycisk_5.Bind(wx.EVT_BUTTON,self.wx_dodaj_słownik)
        self.Przycisk_6 = wx.Button(panel2,-1,"-",pos=(320,230),size=(50,50)) 
        self.Przycisk_6.Bind(wx.EVT_BUTTON,self.wx_usuń_słownik)
        self.Przycisk_7 = wx.Button(panel2,-1,"^",pos=(380,230),size=(50,50))
        self.Przycisk_7.Bind(wx.EVT_BUTTON,self.wx_przesun_w_górę_słownik) 
        self.Przycisk_8 = wx.Button(panel2,-1,"v",pos=(440,230),size=(50,50)) 
        self.Przycisk_8.Bind(wx.EVT_BUTTON,self.wx_przesun_w_dół_słownik)        
        self.Przycisk_20 = wx.Button(panel2,-1,"Wczytaj spis słowników z pliku",pos=(260,290),size=(230,80)) 
        self.Przycisk_20.Bind(wx.EVT_BUTTON,self.wx_wczytaj_pliki_slownikow)
        
        self.Lista_Cykli=wx.ListBox(panel2, pos=(510,20), size=(230,200)) # sekw do wybrania
        self.text_l_c = wx.StaticText(panel2,-1 , label='Ilość cykli', pos=(600, 5))
        self.Przycisk_9 = wx.Button(panel2,-1,"+",pos=(510,230),size=(50,50)) 
        self.Przycisk_9.Bind(wx.EVT_BUTTON,self.wx_ustaw_wartość_1_cyklu)
        self.Przycisk_10 = wx.Button(panel2,-1,"-",pos=(570,230),size=(50,50)) 
        self.Przycisk_10.Bind(wx.EVT_BUTTON,self.wx_usuń_cykl)
        self.Przycisk_11 = wx.Button(panel2,-1,"^",pos=(630,230),size=(50,50))
        self.Przycisk_11.Bind(wx.EVT_BUTTON,self.wx_przesun_w_górę_cykl) 
        self.Przycisk_12 = wx.Button(panel2,-1,"v",pos=(690,230),size=(50,50)) 
        self.Przycisk_12.Bind(wx.EVT_BUTTON,self.wx_przesun_w_dół_cykl) 
        self.Przycisk_13 = wx.Button(panel2,-1,"Ustaw ilość dla wszystkich symulacji",pos=(510,290),size=(230,80)) 
        self.Przycisk_13.Bind(wx.EVT_BUTTON,self.wx_ustaw_wartość_wszystkich_cykli)
        
        self.Lista_Analiz=wx.ListBox(panel2, pos=(10,400), size=(230,290)) # sekw do wybrania
        self.text_l_a = wx.StaticText(panel2,-1 , label='Analizy', pos=(100, 385))
        self.Przycisk_14 = wx.Button(panel2,-1,"+",pos=(260,400),size=(150,50)) 
        self.Przycisk_14.Bind(wx.EVT_BUTTON,self.wx_dodaj_plik_do_analizy)
        self.Przycisk_15 = wx.Button(panel2,-1,"-",pos=(260,460),size=(150,50)) 
        self.Przycisk_15.Bind(wx.EVT_BUTTON,self.wx_usuń_analizę)
        self.Przycisk_16 = wx.Button(panel2,-1,"Wczytaj liste plikow\n do analizy z pliku",pos=(260,520),size=(150,100)) 
        self.Przycisk_16.Bind(wx.EVT_BUTTON,self.wx_dodaj_pliki_do_analizy_z_txt)
        self.Przycisk_17 = wx.Button(panel2,-1,"Uruchom szereg symulacji",pos=(260,700),size=(230,80)) 
        self.Przycisk_17.Bind(wx.EVT_BUTTON,self.wx_uruchom_szereg_symulacji)       
        self.Przycisk_18 = wx.Button(panel2,-1,"Uruchom Analizy",pos=(10,700),size=(230,80)) 
        self.Przycisk_18.Bind(wx.EVT_BUTTON,self.wx_szereg_analiz)     
        self.maxPercent = 100
        self.percent = 0
        #opcjonalnie dodac 2 przyciski do laadowani tych srodowisk i plansz
        #
    def wx_wczytaj_pliki_srodowisk(self,evt):
        """
        Dodaje wiersze wybranego pliku do listobxa "Środowiska".
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Dodanie wielu elementów.
        """
        dialog=wx.FileDialog(self,"Wybierz plik z nazwami plików parametrów (słowników).",defaultFile='',wildcard='*.TXT',style=wx.FD_OPEN, pos=(10,10))
        if dialog.ShowModal() == wx.ID_OK:
            sciezka = dialog.GetPaths()
            with open(sciezka[0],"r") as f: 
                while True:
                    line=f.readline()
                    if not line:
                        break
                    line=line.replace('\n', '')
                    self.Lista_Plansz.Append(line)
            dialog.Destroy()
    
    def wx_wczytaj_pliki_slownikow(self,evt):
        """
        Dodaje wiersze wybranego pliku do listobxa "Parametry".
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Dodanie wielu elementów.
        """
        dialog=wx.FileDialog(self,"Wybierz plik z nazwami plików z planszą początkową.",defaultFile='',wildcard='*.TXT',style=wx.FD_OPEN, pos=(10,10))
        if dialog.ShowModal() == wx.ID_OK:
            sciezka = dialog.GetPaths()
            with open(sciezka[0],"r") as f: 
                while True:
                    line=f.readline()
                    if not line:
                        break
                    line=line.replace('\n', '')
                    self.Lista_Parametry.Append(line)
            dialog.Destroy()
            
            
    def wx_wyświetl_wiadomość(self,wiadomość,tryb):
        """
        Wyświetla okno dialogowe z wartościami argumentów.

        Parameters
        ----------
        wiadomość (str): komunikat do przekazania użytkownikowi
        tryb (str) : odpowiada stylowu okna. 

        Wynik
        -------
        Okno z wiadomością.
        """
        if tryb=="error":
            styl= wx.ICON_ERROR
        elif tryb=="warning":
            styl= wx.ICON_WARNING
        elif tryb=="info":
            styl= wx.ICON_INFORMATION
        else:
            styl= wx.ICON_NONE        
        powiadomienie1=wx.MessageDialog(None,message=wiadomość,style = wx.OK | styl )
        powiadomienie1.ShowModal()   

    def wx_przesun_w_dół_plansze(self,evt):
        """
        Przesuwa zaznaczoną pozycję listobxa "Środowiska w dół.
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Zmiane pozycji elementu.
        """
        if self.wx_test_do_operacji_listboxami("Plansza"):
             Który=(self.Lista_Plansz.GetSelection())
             if Który !=(self.Lista_Plansz.GetCount()-1): # nie jest ostatnia wartośćia
                a=self.Lista_Plansz.GetString(Który) # ten wyzej
                b=self.Lista_Plansz.GetString(Który+1) # zaznaczony1
                self.Lista_Plansz.SetString(Który,b)
                self.Lista_Plansz.SetString(Który+1,a)

                
    def wx_przesun_w_górę_plansze(self,evt):
        """
        Przesuwa zaznaczoną pozycję listobxa "Środowisko" w górę.
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Zmiane pozycji elementu.
        """
        if self.wx_test_do_operacji_listboxami("Plansza"):
            Który=(self.Lista_Plansz.GetSelection())
            if Który != 0: # nie jest pierwszą wartośćia
                a=self.Lista_Plansz.GetString(Który) # ten wyzej
                b=self.Lista_Plansz.GetString(Który-1) # zaznaczony1
                self.Lista_Plansz.SetString(Który,b)
                self.Lista_Plansz.SetString(Który-1,a)

                
    def wx_przesun_w_dół_słownik(self,evt):
        """
        Przesuwa zaznaczoną pozycję listobxa "Parametry" w dół.
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Zmiane pozycji elementu.
        """
        if self.wx_test_do_operacji_listboxami("Parametr"):
             Który=(self.Lista_Parametry.GetSelection())
             if Który !=(self.Lista_Parametry.GetCount()-1): # nie jest ostatnia wartośćia
                a=self.Lista_Parametry.GetString(Który) # ten wyzej
                b=self.Lista_Parametry.GetString(Który+1) # zaznaczony1
                self.Lista_Parametry.SetString(Który,b)
                self.Lista_Parametry.SetString(Który+1,a)
                
    def wx_przesun_w_górę_słownik(self,evt):
        """
        Przesuwa zaznaczoną pozycję listobxa "Parametry" w górę.
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Zmiane pozycji elementu.
        """
        if self.wx_test_do_operacji_listboxami("Parametr"):
            Który=(self.Lista_Parametry.GetSelection())
            if Który != 0: # nie jest pierwszą wartośćia
                a=self.Lista_Parametry.GetString(Który) # ten wyzej
                b=self.Lista_Parametry.GetString(Który-1) # zaznaczony1
                self.Lista_Parametry.SetString(Który,b)
                self.Lista_Parametry.SetString(Który-1,a)
                
    def wx_przesun_w_dół_cykl(self,evt):
        """
        Przesuwa zaznaczoną pozycję listobxa "Ilość cykli" w dół.
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Zmiane pozycji elementu.
        """
        if self.wx_test_do_operacji_listboxami("Cykle"):
             Który=(self.Lista_Cykli.GetSelection())
             if Który !=(self.Lista_Cykli.GetCount()-1): # nie jest ostatnia wartośćia
                a=self.Lista_Cykli.GetString(Który) # ten wyzej
                b=self.Lista_Cykli.GetString(Który+1) # zaznaczony1
                self.Lista_Cykli.SetString(Który,b)
                self.Lista_Cykli.SetString(Który+1,a)
                
    def wx_przesun_w_górę_cykl(self,evt):
        """
        Przesuwa zaznaczoną pozycję listobxa "Ilość cykli" w górę.
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Zmiane pozycji elementu.
        """
        if self.wx_test_do_operacji_listboxami("Cykle"):
            Który=(self.Lista_Cykli.GetSelection())
            if Który != 0: # nie jest pierwszą wartośćia
                a=self.Lista_Cykli.GetString(Który) # ten wyzej
                b=self.Lista_Cykli.GetString(Który-1) # zaznaczony1
                self.Lista_Cykli.SetString(Który,b)
                self.Lista_Cykli.SetString(Który-1,a)
          
                
    def wx_usuń_słownik(self, evt):
        """
        Usuwa zaznaczoną pozycję listobxa "Parametry".
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Usunięcie elementu.
        """
        if self.Lista_Parametry.GetSelection()==(-1) :
            pass
        else:
            self.Lista_Parametry.Delete((self.Lista_Parametry.GetSelection()))
                        
    def wx_usuń_planszę(self, evt):
        """
        Usuwa zaznaczoną pozycję listobxa "Środowiska".
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Usunięcie elementu.
        """
        if self.Lista_Plansz.GetSelection()==(-1) :
            pass
        else:
            self.Lista_Plansz.Delete((self.Lista_Plansz.GetSelection())) 
            
    def wx_usuń_cykl(self,evt):
        """
        Usuwa zaznaczoną pozycję listobxa "Ilość cykli".
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Usunięcie elementu.
        """
        if self.Lista_Cykli.GetSelection()==(-1) :
            pass
        else:
            self.Lista_Cykli.Delete((self.Lista_Cykli.GetSelection())) 
            
    def wx_usuń_analizę(self,evt):
        """
        Usuwa zaznaczoną pozycję listobxa "Analizy".
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Usunięcie elementu.
        """
        if self.Lista_Analiz.GetSelection()==(-1) :
            pass
        else:
            self.Lista_Analiz.Delete((self.Lista_Analiz.GetSelection())) 
                       
    def wx_test_do_operacji_listboxami(self,arg):
        """
        Sprawda czy jest na czym dokonać operacji.
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Wiadomoś w oknie dialgowym, lub warśtoć True.
        """
        if arg=="Plansza":
            if  self.Lista_Plansz.GetCount()<2 :
                self.wx_wyświetl_wiadomość("Najpierw dodaj plansze","warning")
            else:
                return True
        elif arg=="Parametr":
            if  self.Lista_Parametry.GetCount()<2 :
                self.wx_wyświetl_wiadomość("Najpierw dodaj parametr","warning")
            else:
                return True
        elif arg=="Cykle":
            if  self.Lista_Cykli.GetCount()< 2 :
                self.wx_wyświetl_wiadomość("Najpierw dodaj ilość  cykli","warning")
            else:
                return True

    def wx_dodaj_słownik(self,evt):
        """
        Dodaje wybrany plik do listobxa "Parametry".
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Dodanie elementu.
        """
        dialog=wx.FileDialog(self,"Wybierz plik z parametrami",defaultFile='',wildcard='*.TXT',style=wx.FD_OPEN, pos=(10,10))
        if dialog.ShowModal() == wx.ID_OK:
            param=[]
            sciezka = dialog.GetPaths()
            param.append(sciezka[0].split("\\")[-1]) 
            self.Lista_Parametry.Append(param)
            dialog.Destroy()
            
    def wx_dodaj_plansze(self,evt):
        """
        Dodaje wybrany plik do listobxa "Środowiska".
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Dodanie elementu.
        """
        dialog=wx.FileDialog(self,"Wybierz plik planszy początkowej",defaultFile='',wildcard='*.TXT',style=wx.FD_OPEN, pos=(10,10))
        if dialog.ShowModal() == wx.ID_OK:
            sciezka = dialog.GetPaths()
            param=[]
            param.append(sciezka[0].split("\\")[-1]) 
            self.Lista_Plansz.Append(param)
            dialog.Destroy()
        
    def wx_pobierz_wartość_ile_cykli(self):
        """
        Wywoluję okno tekstowe z polem do wpisania wartości.
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Zwraca wartość liczbową, lub komunikat o nieprawidłowości wprowadzonej danej.
        """
        pop=wx.TextEntryDialog(self,message="Podaj ilość cykli",caption="ustawienia")
        pop.ShowModal()
        liczba=pop.GetValue() 
        if liczba.isnumeric()==False:
            self.wx_wyświetl_wiadomość("Wprowadzona wartość nie jest liczbą","error")
        else:
            return liczba
    
    def wx_dodaj_plik_do_analizy(self,evt):
        """
        Dodaje wybrany plik do listobxa "Analizy".
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Dodanie elementu.
        """
        dialog=wx.FileDialog(self,"Wybierz plik ukończonej symulacji",defaultFile='',wildcard='*.TXT',style=wx.FD_OPEN, pos=(10,10))
        if dialog.ShowModal() == wx.ID_OK:
            sciezka = dialog.GetPaths()
            global Lista_Plansz
            self.Lista_Analiz.Append(sciezka[0])
            dialog.Destroy()
                
    def wx_dodaj_pliki_do_analizy_z_txt(self,evt):
        """
        Dodaje wiersze wybranego pliku do listobxa "Analizy".
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Dodanie wielu elementów.
        """
        dialog=wx.FileDialog(self,"Wybierz plik z nazwami plików ukończonych symulacji",defaultFile='',wildcard='*.TXT',style=wx.FD_OPEN, pos=(10,10))
        if dialog.ShowModal() == wx.ID_OK:
            sciezka = dialog.GetPaths()
            with open(sciezka[0],"r") as f: 
                while True:
                    line=f.readline()
                    if not line:
                        break
                    line=line.replace('\n', '')
                    self.Lista_Analiz.Append(line)
            dialog.Destroy()
    
    def wx_ustaw_wartość_1_cyklu(self,evt):
        """
        Dodaje pobraną wartość do listobxa "Ilość cykli".
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Dodanie elementu.
        """
        liczba=self.wx_pobierz_wartość_ile_cykli()
        if type(liczba)==str:
            cos=[]
            cos.append(liczba)
            self.Lista_Cykli.Append(cos)
        
    def wx_ustaw_wartość_wszystkich_cykli(self,evt):
        """
        Pobiera wartość od użytkownia i dodaje ją do listobxa "Ilość cykli", 
        tyle razy, ile jest pozycji w listboxie "Środowiska".
        
        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.
        
        Wynik
        -------
        Dodanie wielu elementów.
        """
        if self.Lista_Plansz.GetCount()> 0 :
            liczba=self.wx_pobierz_wartość_ile_cykli()
            if type(liczba)==str:
                cos=[]
                cos.append(liczba)
                while self.Lista_Cykli.GetCount()>0:
                    self.Lista_Cykli.Delete(0) #
                for x in range(0,self.Lista_Plansz.GetCount()):
                    self.Lista_Cykli.Append(cos)
        else:
             self.wx_wyświetl_wiadomość("Najpierw należy dodać środowiska","warning")
             
             
    def wx_uruchom_szereg_symulacji(self,evt):
        """
        Pobiera wartości o tym samym indeksie, kolejno z listboxów:
        "Środowiska, Parametry i Ilość cykli", tworząc z nich tulpę.
        Nastepnie wczytuje 2 pierwsze wartości i przeprowadza dla nich symulację
        tyle razy, ile wynosi wartość 3 listboxa. Efekt każdego takiego procesu
        jest zapisywane w postaci ciągu znaków w plikach o nazwie aktualnego 
        środowiska +"_numer powtórzenia". W przypadku istnienia już pliku 
        o tej samej nazwie, nazwa kończy się "_Nowsze_". Generuje również plik
        .txt o nazwie daty uruchomienia procesu z nazwami wszystkich 
        wygenerowanych plików symulacji.

        Parameters
        ----------
        evt : Wywołane poprzez kliknięcie na widżet.

        Wynik
        -------
        Utworzenie plików ".txt".

        """
        if ((self.Lista_Plansz.GetCount()+self.Lista_Parametry.GetCount()+self.Lista_Cykli.GetCount())/3 == self.Lista_Cykli.GetCount()) and self.Lista_Cykli.GetCount()!=0:
            lista_zbiórcza=[]
            Ile_łącznie_generacji=[]
            for x in range(self.Lista_Cykli.GetCount()):# tutaj powstaje 
                lista_wsadowa=[]
                lista_wsadowa.append(self.Lista_Plansz.GetString(x)) 
                lista_wsadowa.append(self.Lista_Parametry.GetString(x))
                lista_wsadowa.append(self.Lista_Cykli.GetString(int(x)))
                lista_zbiórcza.append(lista_wsadowa)
            for x in range(len(lista_zbiórcza)):
                with open(lista_zbiórcza[x][1],"r") as f:
                    for i, line in enumerate(f):
                        if i == 0:
                            line=f.readline()
                            line=line.replace('\n', '')
                            line=line.split(":")
                            Ile_łącznie_generacji.append(int(line[1])*int(lista_zbiórcza[x][2]))        
            Ile_łącznie_generacji2=0
            for x in Ile_łącznie_generacji:
                Ile_łącznie_generacji2+=x
            self.progress = wx.ProgressDialog("Operacja w toku", "proszę czekać", maximum=self.maxPercent, parent=self, style=wx.PD_SMOOTH|wx.PD_AUTO_HIDE)
            taskPercent_upd=100/Ile_łącznie_generacji2
            taskPercent =0
            licznik_b=0
            nazwa_p_z_lista_sym=datetime.now().strftime("Spis_Symulacji_%d-%m-%Y_%I-%M-%S_%p")
            for ru in range(len(lista_zbiórcza)):# dla każdego zestaw
                for ko in range(int(lista_zbiórcza[ru][2])):# tyle razy ile jest powtórzeń
                    global słownik
                    słownik=wczytaj_słownik(lista_zbiórcza[ru][1])
                    il_cyklów=słownik["ilość_cykli"]
                    m=lista_zbiórcza[ru][0]
                    lista=wczytaj_stan_początkowy(m)
                    a=""
                    za=m.split(".txt")
                    a=za[0]+"_"+str(ko+1)
                    if os.path.exists(a+".txt"): #
                        while os.path.exists(a):
                            a=za[0]+"_Nowsze_"+str(ko+1)
                    else:
                        a=za[0]+"_"+str(ko+1)  
                    if "Srodowisko" in a:
                        a=a.replace("Srodowisko","Symulacja")
                    a=a+".txt"
                    słownik["nazwa_pliku_z_generacjami"]=a
                    zapisz_słownik(lista_zbiórcza[ru][1],słownik)
                    with open(a,"w") as f:
                        K_N=1
                        warstwa_1=lista # podstawka
                        ca2=znaki(warstwa_1)
                        f.write(str(ca2)+"\n") # zapisz generacje nr 0
                        współrzędne=[] 
                        współrzędne2=[]
                        for n in range(0,len(warstwa_1)):   
                            for z in range(0,len(warstwa_1[0])):
                                współrzędne.append([n,z])    
                        while K_N< il_cyklów: # dopóty nie przjedzie cyklów
                            warstwa_2=warstwa_1.copy()
                            współrzędne2=współrzędne.copy()
                            while len(współrzędne2)!=0:
                                qqq=random.choice((współrzędne2))
                                n=qqq[0]
                                z=qqq[1]
                                wsp_akt=warstwa_1[n][z].wybór(n,z,warstwa_1,warstwa_2) 
                                if wsp_akt[0] in współrzędne2:
                                    współrzędne2.remove(wsp_akt[0])
                                    warstwa_1[n][z].starzenie(wsp_akt[0][0],wsp_akt[0][1],warstwa_2)# wymagane w przypadku ruchu osobnika na pole z tura
                                else:
                                    współrzędne2.remove(wsp_akt[1])
                                    warstwa_1[n][z].starzenie(wsp_akt[1][0],wsp_akt[1][1],warstwa_2)# wymagane w przypadku ruchu osobnika na pole ktore mialo wczesniej wybor
                            #skończyło całą listę
                            ca2=znaki(warstwa_2)
                            f.write(str(ca2)+"\n") # zapisz generacje
                            warstwa_1=warstwa_2.copy()
                            K_N+=1
                            licznik_b+=1
                            taskPercent +=taskPercent_upd
                            self.progress.Update(taskPercent,("{} / {}".format(licznik_b,Ile_łącznie_generacji2) ))
                    with open((nazwa_p_z_lista_sym+".txt"),"a") as f:
                              f.write(a+"\n")
                    cos=[]
                    cos.append(a)
                    self.Lista_Analiz.Append(cos)
            self.wx_zniszcz_pasek_postępu()
            self.wx_wyświetl_wiadomość("Ukończono symulację", "info")    
        else:
            self.wx_wyświetl_wiadomość("Brak zgodności w ilości wprowadzoncyh danych","error")
    def wx_szereg_analiz(self,evt):
        """    
        Analizuję wskazany plik i produkuje nastepujące statystyki:
            - zachorowalność (int) : ilość zarażonych / dzień
            - zasieg (int) : ile przybyło zarażonych miejsc / dzień
            - łączną ilość zarażonych (int) / dzień
            - śmiertelność  (int) : łączne zgony spowodowane wirusem /od początku do tego dnia
            - moment outbreaku (int) : dzień
            
        Parameters
        ----------
        nazwa (str) : nazwa pliku który będzie analizowany
        
        Wynik
        -------
        Plik ".txt"
        """
        Ile_łacznie=self.Lista_Analiz.GetCount()
        self.progress = wx.ProgressDialog("Operacja w toku", "proszę czekać", maximum=self.maxPercent, parent=self, style=wx.PD_SMOOTH|wx.PD_AUTO_HIDE)
        taskPercent_upd=100/Ile_łacznie
        taskPercent =0

        if self.Lista_Analiz.GetCount()!=0:
            lista_analizowanych_plików=[]
            for x in range(self.Lista_Analiz.GetCount()):# tutaj powstaje 
                nazwa=self.Lista_Analiz.GetString(x)
                lista_generalna=[] # 
                licznik=0 # warunkuje wyliczanie pozycji .seek()
                lista_współrzędnych_inf=[] # koordynaty 
                l_23=[]
                lista_współrzędnych_martwych_inf=[]
                lista_generacji=[0,0,0,0,0,0,0,0,0,0,0] # ile było każdego typu na generację
                                #x,o,v,q,p,a,s,c,d,n,k
                l_pom=[]
                with open(nazwa,"r") as f:
                    ile_znaków=len(f.readline().replace('\n', '')) # ile jest obiektow
                    pierw=int(math.sqrt(ile_znaków)) # ile jest znakow na "rząd"
                    while True :   
                        f.seek((ile_znaków+2)*licznik)# +2 ze względu na "\n" na końcu lini
                        txt_generacji=f.readline()
                        if not txt_generacji :
                            break
                        else:
                            txt_generacji.replace('\n', '')
                        n_1=0 #koordynat 1
                        for d_x in range(0,len(txt_generacji),pierw):
                            x_2=0 #koordynat 2
                            for kom in (txt_generacji[d_x:d_x+pierw]):
                                if kom =="x":  #puste pole
                                    lista_generacji[0]+=1
                                elif kom=="o":   #zdrowa
                                    lista_generacji[1]+=1
                                elif kom=="v":  #nosiciel
                                    lista_generacji[2]+=1
                                elif kom=="q":     #inkub
                                    lista_generacji[3]+=1
                                    element=(n_1,x_2)
                                    if element not in l_pom:
                                        lista_współrzędnych_inf.append(element)
                                        l_pom.append(element)
                                elif kom =="p":#peracute
                                    lista_generacji[4]+=1
                                elif kom =="a":#acute
                                    lista_generacji[5]+=1 
                                elif kom =="s": #subacute
                                    lista_generacji[6]+=1
                                elif kom =="c":#chronical
                                    lista_generacji[7]+=1
                                elif kom=="d":   #dead
                                    lista_generacji[8]+=1
                                elif kom=="n":   #dead_ill
                                    lista_generacji[9]+=1
                                    element=(n_1,x_2)
                                    if element not in lista_współrzędnych_martwych_inf:
                                        lista_współrzędnych_martwych_inf.append(element)
                                elif kom=="k": #cured
                                    lista_generacji[10]+=1 
                                x_2+=1
                            n_1+=1
                        l_23.append(int(len(lista_współrzędnych_inf)))
                        lista_łącząca=[lista_generacji,l_23]  
                        lista_generalna.append(lista_łącząca)
                        lista_generacji=[0,0,0,0,0,0,0,0,0,0,0] # ile było każdego typu na generację 
                        lista_współrzędnych_inf=[]
                        licznik+=1
                zamrło_na_chorob=len(lista_współrzędnych_martwych_inf) / lista_generalna[0][0][1]
                l_zachorowalności=[]
                for x_23 in range(len(lista_generalna)): # patrze na dni po kolei
                    try:
                        r_zdrowych=abs((lista_generalna[x_23][0][1]-lista_generalna[x_23-1][0][1])) #moze sie tylko zmniejszac
                        r_truchl_norm=(lista_generalna[x_23][0][8]-lista_generalna[x_23-1][0][8]) # jezeli przybylo to bedzie na plusie
                        r_pustych=(lista_generalna[x_23][0][0]-lista_generalna[x_23-1][0][0]) # moze tylko sie zwiekszac
                        suma=r_truchl_norm+r_pustych
                        if suma > r_zdrowych:
                            zqwr=r_zdrowych
                        else:
                           zqwr= r_zdrowych-(r_truchl_norm +r_pustych)
                        l_zachorowalności.append(zqwr)
                    except:
                        l_zachorowalności.append(0)
                l_zaraz_w_czasie=0
                l_zachorowalności[0]=0
                nazwa2=nazwa.replace("Symulacja","Analiza")
                lista_analizowanych_plików.append(nazwa2)
                napis0="Dzień;Zasięg;Zachorowania;Łącznie_zarażonych\n"
                with open(nazwa2,'w') as f:
                    f.write(napis0)
                    for x_cel in range(len(lista_generalna)):
                        f.write("Dzień_"+str(x_cel)+";"+str(l_23[x_cel])+";"+str(l_zachorowalności[x_cel])+";"+str(l_zaraz_w_czasie)+"\n") # zapisz generacje 
                        l_zaraz_w_czasie+=l_zachorowalności[x_cel]
                    napis1="Śmiertelność : "+str(zamrło_na_chorob)+"\n"
                    f.write(napis1)
                taskPercent +=taskPercent_upd
                self.progress.Update(taskPercent,("{} / {}".format(x,Ile_łacznie) ))
            nazwa_p_z_lista_sym=datetime.now().strftime("Spis_Analiz_%d-%m-%Y_%I-%M-%S_%p")
            with open((nazwa_p_z_lista_sym+".txt"),"a") as f:
                for x_nom in lista_analizowanych_plików:
                    f.write(x_nom+"\n")
            self.wx_zniszcz_pasek_postępu()
            self.wx_wyświetl_wiadomość("Ukończono analizy", "info")    
        else:
            self.wx_wyświetl_wiadomość("Brak zgodności w ilości wprowadzoncyh danych","error")
                

    def wx_zniszcz_pasek_postępu(self):
        """
        Zdalnie niszczy wywołane okno postepu
        """
        self.progress.Destroy()
    
            
class Cell() :
    """
    Klasa Cell : puste pole.
    Zawiera wszystkie podstawowe metody obiektów oraz parametry:
        symbol (str): reprezentacja graficzna
        live (int): zakres życia
        licznik (int) : wiek
        move_time (int) : czas po którym może się ponownie przemieścić
    """
    symbol="x"
    def __init__(self):
        """
        Konstruktor klasy Cell.
        """
        self.licznik=słownik["All_licznik"]
        self.live=słownik["Cell_live"]
        self.move_time=słownik["Cell_move_time"]


    def znak (self): 
        """
        Zwraca symbol obiektu.
        
        Wynik
        -------
        Znakowa reprezentację obiektu w pliku symulacji.
        """
        return self.symbol
    
    def wiek (self): 
        """
        Zwraca wiek obiektu.
        
        Wynik
        -------
        Liczba (int)
        """
        return self.licznik

    def test(self,współczynnik): #0-1
        """
        Przeprowadza losowanie za pomocą modułu random w zakresie 0-1, po czym 
        sprawdza czy podany argument się w nim zawiera.
        
        Wynik
        -------
        Wartość logiczna (Bool) : True lub False
        """
    
        return random.random()<= współczynnik 
    
    def starzenie (self,n,z,lista2): # 1 wystarczy
        """
        Dodaje dla wywołanego obiektu +1 do licznika. Jeżeli jego warotć wykracza
        poza parametr "live", zmienia jego typ na "Cell_Dead", przenosząc wraz
        ze zmianę aktualny licznik.
        
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej
            
        lista2 (list) : Lista na której nanieść wynik metody
        
        Wynik
        -------
        Zmiana parametru "licznik", lub klasy obiektui
        """
        if type(lista2[n][z])==Cell():
            pass
        else:
            if self.licznik >= self.live:
                lista2[n][z]=Cell_Dead()
                lista2[n][z].licznik=0
            else:
                lista2[n][z].licznik+=1

    def test_przecinkowy(self):
        """
        Przeprowadza losowanie za pomocą modułu random w zakresie
        parametru "przecinki", obiektu i zwraca wartość logiczną.

        Wynik
        -------
        Wartość logiczna (Bool) : True lub False
        
        """
        współczynnik=random.uniform(self.przecinki[0],self.przecinki[1])
        return self.test(współczynnik)
        
    def losuj_kom_z_l_i_przekszt(self,pula_l,lista2,w_jaką_kom): 
        """
        Za pomocą modułu random, wybiera losowe koordynaty,
        i zmienia obiektu w tym miejscu na zadany typ we wskazanej warstwie.
        
        Parameters
        ----------
        pula_l (list): zbiorcza lista współrzędnych w postaci tulp.
        
        lista2 (list): 1 z 2 warstw. .
        
        w_jaką_kom (klasa): w jaką klasę, wylosowany obiekt ma być zmieniony.

        Wynik
        -------
        Zmiana klasy obiektu + wartoś logicczna True.

        """
        los=random.choice(pula_l)
        wsp_1=los[0]#n
        wsp_2=los[1]#z
        lista2[wsp_1][wsp_2]=w_jaką_kom()
        q=True  
        return q
    
    def zachoruj(self,n,z,lista1,lista2): # jedna wystarczy
        """
        Moduł random losuje formę chorobową, nastepnie szuka czy są w jego 
        sąsiedztwo wektory chorobotwórcze. Jeżeli tak, to obliczane jest 
        prawdopodobieństwo zakażenia; jeżeli test okaże się pozytywny, to 
        obiekt który wywołał te funkcję zmienia swój typ na "Cell_Incubating".
    
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
            
        lista2 (list) : Lista na której nanieść wynik metody.
        
        Wynik
        -------
        Zmiana klasy obiektu 
        Zwaraca listę zawierającą wartość logiczna adekwatną do wyniku testu,
        oraz swoje współrzędne.
        """
        l_zar=[ Cell_Cured_Infectious, Cell_Ill_Peracute , Cell_Ill_Acute,  Cell_Ill_Subacute , Cell_Ill_Chronic, Cell_Dead_Ill ]
        param=self.szukaj(n,z,lista1,l_zar,1)
        wynik=[False,[n,z]]
        y=0
        #param[0] #wsp
        #parm[1] #liczenosc szukanych typow
        if self.spr_czy_pusty(param[1])!=0:
            for qw in range(0,len(param[1])):
                y+=l_zar[qw]().c_poison*param[1][qw]
                te=self.test(y)
                if te==True:
                    lista2[n][z]=Cell_Incubating()
                    wynik=(True,[n,z])
        return wynik

    def spr_czy_pusty(self,lista_list):
        """
        Sumje ilość każdego ze znalezionych typów, zadanych w metodzie "szukaj".
        
        Parameters
        ----------
        lista_list (lista): lista, gdzie każdy element reprezentuje ilość
            obiektów o danym typie.

        Wynik
        -------
        Liczba (int).
        """
        l=0
        for x in lista_list:
           l+=x
        return(l)

    def ruch(self,n,z,lista,lista2):
        """
        Obiektu wywołującego tę metodę, wykonuje test na przemieszczenie się.
        W przypadku powodzenia, sprawdzane jest czy w jego sąsiedzwie występują
        pola, na które mógłby "przejść". Jeżeli tak to wykonwca i wylosowany 
        obiekt są zamieniane miejscami. Ponadto obiekowi sprawczemu przydzielany 
        jest wartość do parametru "move_time" warunkujący czas między możliwością
        przeprowadzenia kolejnego testu.

        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
        
        lista (list) : lista na której badana jest dostępność pół w sąsiedztwie.
            
        lista2 (list) : Lista na której nanieść wynik metody
            
        Wynik
        -------
        Zmiana miejsca obiektu na liście2 na wybrane wspórzędne i ich zwrócenie
        wraz z wartością logiczną odpowidnią do powodzenia procesu.
        """
        wynik=[[n,z],0]
        l_ruch=[Cell,Cell_Alive,Cell_Cured_Infectious, Cell_Ill_Peracute , Cell_Ill_Acute,  Cell_Ill_Subacute , Cell_Ill_Chronic]
        if self.move_time <=0: #jeżeli odczekał po ostatnim przemieszczeniu
            if self.test(self.c_move):#zdał
                a=self.szukaj(n,z,lista,l_ruch,1) # może zamienić sie tylko z tymi 2 typami
                if self.spr_czy_pusty(a[1])==0 :
                    pass
                else:
                    l_tymczasowa=[]
                    for q1 in a[0]:
                        if len(q1)!=0:
                            for q2 in q1:
                                l_tymczasowa.append(q2)
                    los_wsp=random.choice(l_tymczasowa)
                    wsp_1=los_wsp[0]#n
                    wsp_2=los_wsp[1]#z
                    cos1=copy.deepcopy(lista[n][z]) #przemieszczajacy sie obiekt
                    cos2=copy.deepcopy(lista[wsp_1][wsp_2]) # wybrane miejsce
                    lista2[n][z]=cos2
                    lista2[wsp_1][wsp_2]=cos1
                    wynik=[[wsp_1,wsp_2],[n,z]]
                    if słownik["Draw_move_time"]:
                        lista2[wsp_1][wsp_2].move_time=random.randrange(słownik["Cell_range_move_time"][0],słownik["Cell_range_move_time"][1])
                    else:
                        lista2[wsp_1][wsp_2].move_time=słownik["Cell_move_time"]
            else:# nie zdał testu
                pass
        else:
            self.move_time-=1
        return wynik
            
    def wybór(self,n,z,lista,lista2):
        """
        Funkcja definiująca możliwe do wykonania, przez obiekt klasy Cell, akcje.
        
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
        
        lista (list) : lista na której badana jest dostępność pół w sąsiedztwie.
            
        lista2 (list) : Lista na której nanieść wynik metody
        
        Wynik
        -------
        Lista zawierająca swoje koodynaty i 0, ponieważ ta klasa nie ma zdolności
        przemieszczania się.
        """
        wynik=[[n,z],0]
        return wynik
    
    def pws(self,dost_wsp,lista_macierz,jakie_kom): # skrócenie wyborów w zasadach 
        """
        Jest to funkcja ułatawiająca działanie metody "Zasady".
        
        Parameters
        ----------
        dost_wsp (list): lista współrzędnych wokół obiektu.
        
        lista_macierz (list) : lista na której znajduje się obiekt.
        
        jakie_kom (list) : pod względem jakich typów, przeszukiwane są pola.
        
        Wynik
        -------
        Zwraca listę tulp (jaka kom, ile jej wystąpień).
        """
        pula_2=[] # zwracamy  tulpę ( współrzędne_daneg_typu ->pula_2, ile_kom_danego_typu -> p  )
        p=[] #  na współrzedne danego typu kom
        for kom in jakie_kom: #x[0] to Y,  x[1] to X
            l_wsp=[]
            for x in dost_wsp:
                if type(lista_macierz[x[0]][x[1]])==kom: # czy ta której szukamy jest w danym polu   
                    l_wsp.append(x)
            pula_2.append(l_wsp)
            p.append(len(l_wsp))
        return ((pula_2,p)) 
    
    def szukaj(self,n,z,lista,jakie_kom,zakres):
        """
        W zależności od umiejscowienia obiektu względem Środowiska (lista),
        selekcjonuję koordynaty pól sąsiadujących. Nastepnie wybiera z nich 
        jedynie to o wskazanym typie.

        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
        
        lista (list) : lista na której badana jest dostępność pół w sąsiedztwie.
        
        jakie_kom (list) : pod względem jakich typów, przeszukiwane są pola.
        
        zakres (int) : dommyślnie 1

        Wynik
        -------
        Lista pól sąsiądujących, o zadanym typie.

        """
        wsp_y=n # numer listy danej komórki
        wsp_x=z# pozycja danej komórki
        if zakres==1:
            if wsp_x ==0 and wsp_y==0:   # LEWA RÓG góra 
                pula_wsp=[(wsp_y,wsp_x+1),(wsp_y+1,wsp_x+1),(wsp_y+1,wsp_x)]
            elif  wsp_x ==(len(lista[wsp_y])-1) and wsp_y==0:   # PRAWA-RÓG góra 
                pula_wsp=[(wsp_y,wsp_x-1),(wsp_y+1,wsp_x-1),(wsp_y+1,wsp_x)]
            elif wsp_x ==(len(lista[wsp_y])-1) and wsp_y==(len(lista)-1): # PRAWY-DOŁ 
                pula_wsp=[(wsp_y-1,wsp_x),(wsp_y-1,wsp_x-1),(wsp_y,wsp_x-1)]
            elif wsp_x ==0 and wsp_y==(len(lista)-1): #LEWY-DOŁ 
                pula_wsp=[(wsp_y-1,wsp_x),(wsp_y-1,wsp_x+1),(wsp_y,wsp_x+1)]
            elif wsp_x ==0 and  0<wsp_y<(len(lista)-1): #LEWA ŚCIANA 
                pula_wsp=[(wsp_y-1,wsp_x),(wsp_y-1,wsp_x+1),(wsp_y,wsp_x+1),(wsp_y+1,wsp_x+1),(wsp_y+1,wsp_x)]
            elif wsp_x ==(len(lista[wsp_y])-1) and  0<wsp_y<(len(lista)-1): #PRAWA ŚCIANA 
                pula_wsp=[(wsp_y-1,wsp_x),(wsp_y-1,wsp_x-1),(wsp_y,wsp_x-1),(wsp_y+1,wsp_x-1),(wsp_y+1,wsp_x)]
            elif 0<wsp_x<(len(lista[wsp_y])-1) and  wsp_y==0: #GÓRNA ŚCIANA 
                pula_wsp=[(wsp_y+1,wsp_x),(wsp_y+1,wsp_x-1),(wsp_y,wsp_x-1),(wsp_y+1,wsp_x+1),(wsp_y,wsp_x+1)]
            elif 0<wsp_x<(len(lista[wsp_y])-1) and  wsp_y==(len(lista)-1): #DOLNA ŚCIANA 
                pula_wsp=[(wsp_y-1,wsp_x),(wsp_y-1,wsp_x-1),(wsp_y,wsp_x-1),(wsp_y-1,wsp_x+1),(wsp_y,wsp_x+1)]
            elif 0<wsp_x<(len(lista[wsp_y])-1) and  0<wsp_y<(len(lista)-1): #Gdzieś w środku 
                pula_wsp=[(wsp_y-1,wsp_x),(wsp_y+1,wsp_x),(wsp_y,wsp_x-1),(wsp_y,wsp_x+1),(wsp_y-1,wsp_x-1),(wsp_y-1,wsp_x+1),(wsp_y+1,wsp_x+1),(wsp_y+1,wsp_x-1)]
            tulpa_l=self.pws(pula_wsp,lista,jakie_kom)
        return(tulpa_l)
            
class Cell_Alive(Cell):
    """
    Klasa Cell_Alive: żywy, zdrowy osobnik.
    Zawiera parametry:
        symbol (str): reprezentacja graficzna,
        live (int): zakres życia,
        licznik (int) : wiek,
        c_move (float) : prawdopodobieństwo wykonania ruchu,
    """
    symbol="o"
    def __init__(self):
        """
        Konstruktor klasy Cell_Alive.
        W zależności od wartości logicznej słownik["Draw_Cell_live"] przyjmuje rożne wartości.
        """
        super().__init__()
        if słownik["Draw_Cell_Live"]:
            self.live=random.randrange(słownik["Draw_Cell_Alive_live"][0],słownik["Draw_Cell_Alive_live"][1])
        else:
            self.live=słownik["Cell_Alive_live"]
        self.c_move=słownik["Cell_Alive_c_move"]     
        self.licznik=słownik["All_licznik"]

    def wybór(self,n,z,lista,lista2):
        """
        Funkcja definiująca możliwe do wykonania, przez obiekt klasy Cell_Alive, akcje.
        W tym przypadku może zachorować a w przypadku niepowodzenia, przemieścić się.
        
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
        
        lista (list) : lista na której badana jest dostępność pół w sąsiedztwie.
            
        lista2 (list) : Lista na której nanieść wynik metody
            
        Wynik
        -------
        Lista zawierająca swoje koodynaty i 0, lub koordynaty osobnika którego miejsce zajeła.
        """
        a=self.zachoruj(n,z,lista,lista2) #test w oparciu o otoczenie
        wynik=[[n,z],0]
        if a[0]: # jeżeli zachorował to koniec
            pass
        else:
            wynik=self.ruch(n,z,lista,lista2)  
        return wynik
    
class Cell_Cured(Cell): 
    """
    Metody oraz parametry przejmuje od klasy rodzicielskiej : Cell.
    Klasa Cell_Cured: żywy, wyzdrowiały osobnika, który wyzbył się właściwości
    zakaźnych.
    Zawiera parametry:
        symbol (str): reprezentacja graficzna,
        live (int): zakres życia,
        licznik (int) : wiek,
        c_move (float) : prawdopodobieństwo wykonania ruchu,
    """
    symbol="k"
    def __init__(self):
        """
        Konstruktor klasy Cell_Cured.
        W zależności od wartości logicznej słownik["Draw_Cell_live"] przyjmuje rożne wartości.
        """
        super().__init__()
        if słownik["Draw_Cell_Live"]:
            self.live=random.randrange(słownik["Draw_Cell_Cured_live"][0],słownik["Draw_Cell_Cured_live"][1])
        else:
            self.live=słownik["Cell_Cured_live"]
        self.licznik=słownik["All_licznik"]
        self.c_move=słownik["Cell_Cured_c_move"]
   
    def starzenie (self,n,z,lista2): 
        """
        Zwiększa wiek obiektu o 1. W przypadku przegroczenia progu, zmienia
        klasę na Cell_Dead.

        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
            
        lista2 (list) : Lista na której nanieść wynik metody

        Wynik
        -------
        Zwiększenie parametru "licznik". Ostatecznie zmiana klasy.

        """
        if self.licznik >= self.live:
            li=self.licznik
            lista2[n][z]=Cell_Dead()
            lista2[n][z].licznik=li
        lista2[n][z].licznik+=1
        
    def wybór(self,n,z,lista,lista2):
        """
        Funkcja definiująca możliwe do wykonania, przez obiekt klasy Cell_Cured, akcje.
        W tym przypadku, może się ona przemieścić.
        
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
        
        lista (list) : lista na której badana jest dostępność pół w sąsiedztwie.
            
        lista2 (list) : Lista na której nanieść wynik metody
            
        Wynik
        -------
        Lista zawierająca swoje koodynaty i 0, lub koordynaty osobnika którego miejsce zajeła.
        """
        wynik=self.ruch(n,z,lista,lista2)  
        return wynik
    
class Cell_Cured_Infectious(Cell):
    """
    Metody oraz parametry przejmuje od klasy rodzicielskiej : Cell.
    Klasa Cell_Cured_Infectious: żywy, osobnik który do końca życia jest nosicielem.
    Zawiera parametry:
        symbol (str): reprezentacja graficzna,
        live (int): zakres życia,
        licznik (int) : wiek,
        c_move (float) : prawdopodobieństwo wykonania ruchu,
        c_poison (float) :prawdopodobieństwo zakażenia osobnika zdrowego.
    """
    symbol="v"
    def __init__(self):
        """
        Konstruktor klasy Cell_Cured_Infectious.
        W zależności od wartości logicznej słownik["Draw_Cell_live"] przyjmuje rożne wartości.
        """
        super().__init__()
        if słownik["Draw_Cell_Live"]:
            self.live=random.randrange(słownik["Draw_Cell_Cured_Infectious_live"][0],słownik["Draw_Cell_Cured_Infectious_live"][1])
        else:
            self.live=słownik["Cell_Cured_Infectious_live"]
        self.c_move=słownik["Cell_Cured_Infectious_c_move"]
        self.c_poison=słownik["Cell_Cured_Infectious_c_poison"]
        self.licznik=słownik["All_licznik"]
        
    def starzenie (self,n,z,lista2): 
        """
        Zwiększa wiek obiektu o 1. W przypadku przegroczenia progu, zmienia
        klasę na Cell_Dead_Ill.

        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
            
        lista2 (list) : Lista na której nanieść wynik metody

        Wynik
        -------
        Zwiększenie parametru "licznik". Ostatecznie zmiana klasy.

        """
        if self.licznik >= self.live:
            lista2[n][z]=Cell_Dead_Ill()
        lista2[n][z].licznik+=1
                
    def wybór(self,n,z,lista,lista2):
        """
        Funkcja definiująca możliwe do wykonania, przez obiekt klasy Cell_Cured_Infectious, akcje.
        W tym przypadku, może się ona przemieścić.
        
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
        
        lista (list) : lista na której badana jest dostępność pół w sąsiedztwie.
            
        lista2 (list) : Lista na której nanieść wynik metody
            
        Wynik
        -------
        Lista zawierająca swoje koodynaty i 0, lub koordynaty osobnika którego miejsce zajeła.
        """
        wynik=self.ruch(n,z,lista,lista2)  
        return wynik
    
class Cell_Incubating(Cell):
    """
    Metody oraz parametry przejmuje od klasy rodzicielskiej : Cell.
    Klasa Cell_Incubating: żywy, zarażony osobnik, który po okresie
    inkubacji zmieni się w aktywna formę chorobową.
    Zawiera parametry:
        symbol (str): reprezentacja graficzna,
        live (int): zakres życia,
        licznik (int) : wiek,
        c_move (float) : prawdopodobieństwo wykonania ruchu.
    """
    symbol="q"
    def __init__(self):
        """
        Konstruktor klasy Cell_Incubating.
        W zależności od wartości logicznej słownik["Draw_Cell_live"] przyjmuje rożne wartości.
        """
        super().__init__()
        if słownik["Draw_Cell_Live"]:
            self.live=random.randrange(słownik["Draw_Cell_Incubating_live"][0],słownik["Draw_Cell_Incubating_live"][1])
        else:
            self.live=słownik["Cell_Incubating_live"]
        self.c_move=słownik["Cell_Incubating_c_move"]
        self.licznik=słownik["All_licznik"]

    def transform(self,n,z,lista2):
        """
        Losowany jest forma chorobowa w którą rozwinie się stadium inkubacyjne.
       
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
            
        lista2 (list) : Lista na której nanieść wynik metody

        Wynik
        -------
        Klasa, w którą zmieni się obiekt wywołujący tę metodę.

        """
        li= [Cell_Ill_Peracute(),Cell_Ill_Peracute(), #2
             Cell_Ill_Acute(), Cell_Ill_Acute(), #2
             Cell_Ill_Subacute(), #1
             Cell_Ill_Chronic()]  #1
        
        return random.choice(li)
        
    def wybór(self,n,z,lista,lista2):
        """
        Funkcja definiująca możliwe do wykonania, przez obiekt klasy Cell_Incubating, akcje.
        W tym przypadku, może się ona przemieścić.
        
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
        
        lista (list) : lista na której badana jest dostępność pół w sąsiedztwie.
            
        lista2 (list) : Lista na której nanieść wynik metody
            
        Wynik
        -------
        Lista zawierająca swoje koodynaty i 0, lub koordynaty osobnika którego miejsce zajeła.
        """
        wynik=self.ruch(n,z,lista,lista2)   
        return wynik
    
    def starzenie(self,n,z,lista2):
        """
        Zwiększa wiek obiektu o 1. W przypadku przegroczenia progu, zmienia
        klasę na formą chorobową wybraną w metodzie "transform"

        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
            
        lista2 (list) : Lista na której nanieść wynik metody

        Wynik
        -------
        Zwiększenie parametru "licznik". Ostatecznie zmiana klasy.

        """
        if self.licznik >= self.live:
            kom=self.transform(n,z,lista2)
            li=self.licznik
            lista2[n][z]=kom
            lista2[n][z].licznik=li
        lista2[n][z].licznik+=1

class Cell_Ill_Peracute(Cell):
    """
    Metody oraz parametry przejmuje od klasy rodzicielskiej : Cell.
    Klasa Cell_Ill_Peracute: żywego, osobnika w super-zajadłej formie chorobowej.
    Zawiera parametry:
        symbol (str): reprezentacja graficzna,
        live (int): zakres życia,
        licznik (int) : wiek,
        c_move (float) : prawdopodobieństwo wykonania ruchu,
        c_poison (float) : prawdopodobieństwa zarażenia zdrowego osobnika,
        autodestruction (bool) : od tego parametru zależy czy komórka po przekroczeniu
                                 okresu życia umrze, czy wyzdrowieje. W przypadku
                                 tej klasy, jest to domyślnie True.
    """
    symbol="p"
    def __init__(self):
        """
        Konstruktor klasy Cell_Ill_Peracute.
        W zależności od wartości logicznej słownik["Draw_Cell_live"] przyjmuje rożne wartości.
        """
        super().__init__()
        if słownik["Draw_Cell_Live"]:
            self.live=random.randrange(słownik["Draw_Cell_Ill_Peracute_live"][0],słownik["Draw_Cell_Ill_Peracute_live"][1])
        else:
            self.live=słownik["Cell_Ill_Peracute_live"]
        self.c_move=słownik["Cell_Ill_Peracute_c_move"]
        self.c_poison=słownik["Cell_Ill_Peracute_c_poison"]
        self.licznik=słownik["All_licznik"]
        self.autodestruction=True # ma 100% smiertelnosci

    def wybór(self,n,z,lista,lista2):
        """
        Funkcja definiująca możliwe do wykonania, przez obiekt klasy Cell_Incubating, akcje.
        W tym przypadku, może się ona przemieścić.
        
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
        
        lista (list) : lista na której badana jest dostępność pół w sąsiedztwie.
            
        lista2 (list) : Lista na której nanieść wynik metody
            
        Wynik
        -------
        Lista zawierająca swoje koodynaty i 0, lub koordynaty osobnika którego miejsce zajeła.
        """
        wynik=self.ruch(n,z,lista,lista2)  
        return wynik

    def starzenie(self,n,z,lista2):
        """
        Zwiększa wiek obiektu o 1. W przypadku przegroczenia progu, zmienia
        klasę na Cell_Dead_Ill.

        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
            
        lista2 (list) : Lista na której nanieść wynik metody

        Wynik
        -------
        Zwiększenie parametru "licznik". Ostatecznie zmiana klasy.

        """
        if self.licznik >= self.live:#powinna umrzeć z powodu chroby
                lista2[n][z]=Cell_Dead_Ill()
                lista2[n][z].licznik=0
        lista2[n][z].licznik+=1

class Cell_Ill_Acute(Cell):
    """
    Metody oraz parametry przejmuje od klasy rodzicielskiej : Cell.
    Klasa Cell_Ill_Acute: żywego, osobnika w wysoko-zajadłej formie chorobowej.
    Zawiera parametry:
        symbol (str): reprezentacja graficzna,
        live (int): zakres życia,
        licznik (int) : wiek,
        c_move (float) : prawdopodobieństwo wykonania ruchu,
        c_poison (float) : prawdopodobieństwa zarażenia zdrowego osobnika,
        autodestruction (bool) : od tego parametru zależy czy komórka po przekroczeniu
                                 okresu życia umrze, czy wyzdrowieje.
    """
    symbol="a"
    def __init__(self):
        """
        Konstruktor klasy Cell_Ill_Acute.
        W zależności od wartości logicznej słownik["Draw_Cell_live"] oraz
        ["Draw_Cell_c_mortality_rate"], przyjmuje rożne wartości.
        """
        super().__init__()
        if słownik["Draw_Cell_Live"]:
            self.live=random.randrange(słownik["Draw_Cell_Ill_Acute_live"][0],słownik["Draw_Cell_Ill_Acute_live"][1])
        else:
            self.live=słownik["Cell_Ill_Acute_live"]
            
        if słownik["Draw_Cell_c_mortality_rate"]:
            self.przecinki=słownik["Draw_Cell_Ill_Acute_c_mortality_rate"]
            self.autodestruction=self.test_przecinkowy()
        else:
            self.autodestruction=self.test(słownik["Cell_Ill_Acute_c_mortality_rate"])
        self.licznik=słownik["All_licznik"]
        self.c_move=słownik["Cell_Ill_Acute_c_move"]
        self.c_poison=słownik["Cell_Ill_Acute_c_poison"]
        

    def wybór(self,n,z,lista,lista2):
        """
        Funkcja definiująca możliwe do wykonania, przez obiekt klasy Cell_Incubating, akcje.
        W tym przypadku, może się ona przemieścić.
        
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
        
        lista (list) : lista na której badana jest dostępność pół w sąsiedztwie.
            
        lista2 (list) : Lista na której nanieść wynik metody
            
        Wynik
        -------
        Lista zawierająca swoje koodynaty i 0, lub koordynaty osobnika którego miejsce zajeła.
        """
        wynik=self.ruch(n,z,lista,lista2)
        return wynik
    
    def starzenie(self,n,z,lista2):
        """
        Zwiększa wiek obiektu o 1. W przypadku przegroczenia progu, spradzana 
        jest wartość parametru "autodestruction. True oznacza zmienę klasy na 
        Cell_Dead_Ill. W przeciwnym przypadku osobnik zdrowieje i zmienia typ
        na Cell_Cured.

        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
            
        lista2 (list) : Lista na której nanieść wynik metody

        Wynik
        -------
        Zwiększenie parametru "licznik". Ostatecznie zmiana klasy.

        """
        if self.licznik >= self.live:#powinna umrzeć z powodu chroby
            if self.autodestruction==False: # jeżeli nie umarła na ASF
                li=self.licznik
                lista2[n][z]=Cell_Cured()
                lista2[n][z].licznik=li
            else:
                li=self.licznik
                lista2[n][z]=Cell_Dead_Ill()
                lista2[n][z].licznik=0
        lista2[n][z].licznik+=1

   
class Cell_Ill_Subacute(Cell):
    """
    Metody oraz parametry przejmuje od klasy rodzicielskiej : Cell.
    Klasa Cell_Ill_Subacute: żywego, osobnika w zajadłej formie chorobowej.
    Zawiera parametry:
        symbol (str): reprezentacja graficzna,
        live (int): zakres życia,
        licznik (int) : wiek,
        c_move (float) : prawdopodobieństwo wykonania ruchu,
        c_poison (float) : prawdopodobieństwa zarażenia zdrowego osobnika,
        autodestruction (bool) : od tego parametru zależy czy komórka po przekroczeniu
                                 okresu życia umrze, czy wyzdrowieje.
    """
    symbol="s"
    def __init__(self):
        """
        Konstruktor klasy Cell_Ill_Subacute.
        W zależności od wartości logicznej słownik["Draw_Cell_live"] oraz
        ["Draw_Cell_c_mortality_rate"], przyjmuje rożne wartości.
        """
        super().__init__()
        if słownik["Draw_Cell_Live"]:
            self.live=random.randrange(słownik["Draw_Cell_Ill_Subacute_live"][0],słownik["Draw_Cell_Ill_Subacute_live"][1])
        else:
            self.live=słownik["Cell_Ill_Subacute_live"]
            
        if słownik["Draw_Cell_c_mortality_rate"]:
            self.przecinki=słownik["Draw_Cell_Ill_Subacute_c_mortality_rate"]
            self.autodestruction=self.test_przecinkowy()
        else:
            self.autodestruction=self.test(słownik["Cell_Ill_Subacute_c_mortality_rate"])
            
        self.licznik=słownik["All_licznik"]
        self.c_move=słownik["Cell_Ill_Subacute_c_move"]
        self.c_poison=słownik["Cell_Ill_Subacute_c_poison"]
        
    
    def wybór(self,n,z,lista,lista2):
        """
        Funkcja definiująca możliwe do wykonania, przez obiekt klasy Cell_Incubating, akcje.
        W tym przypadku, może się ona przemieścić.
        
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
        
        lista (list) : lista na której badana jest dostępność pół w sąsiedztwie.
            
        lista2 (list) : Lista na której nanieść wynik metody
            
        Wynik
        -------
        Lista zawierająca swoje koodynaty i 0, lub koordynaty osobnika którego miejsce zajeła.
        """
        wynik=self.ruch(n,z,lista,lista2)   
        return wynik

    def starzenie(self,n,z,lista2):
        """
        Zwiększa wiek obiektu o 1. W przypadku przegroczenia progu, spradzana 
        jest wartość parametru "autodestruction. True oznacza zmienę klasy na 
        Cell_Dead_Ill. W przeciwnym przypadku osobnik zdrowieje i zmienia typ
        na Cell_Cured.

        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
            
        lista2 (list) : Lista na której nanieść wynik metody

        Wynik
        -------
        Zwiększenie parametru "licznik". Ostatecznie zmiana klasy.

        """
        if self.licznik >= self.live:#powinna umrzeć z powodu chroby
            if self.autodestruction==False: # jeżeli nie umarła na ASF
                li=self.licznik
                lista2[n][z]=Cell_Cured()
                lista2[n][z].licznik=li
            else:
                li=self.licznik
                lista2[n][z]=Cell_Dead_Ill()
                lista2[n][z].licznik=0
        lista2[n][z].licznik+=1
        
class Cell_Ill_Chronic (Cell_Alive): 
    """
    Metody oraz parametry przejmuje od klasy rodzicielskiej : Cell.
    Klasa Cell_Ill_Chronic: żywego, osobnika w przewklekłej formie chorobowej.
    Zawiera parametry:
        symbol (str): reprezentacja graficzna,
        live (int): zakres życia,
        licznik (int) : wiek,
        c_move (float) : prawdopodobieństwo wykonania ruchu,
        c_poison (float) : prawdopodobieństwa zarażenia zdrowego osobnika,
        autodestruction (bool) : od tego parametru zależy czy komórka po przekroczeniu
                                 okresu życia umrze, czy wyzdrowieje.
    """
    symbol="c"
    def __init__(self):
        """
        Konstruktor klasy Cell_Ill_Chronic.
        W zależności od wartości logicznej słownik["Draw_Cell_live"] oraz
        ["Draw_Cell_c_mortality_rate"], przyjmuje rożne wartości.
        """
        super().__init__()
        if słownik["Draw_Cell_Live"]:
            self.live=random.randrange(słownik["Draw_Cell_Ill_Chronic_live"][0],słownik["Draw_Cell_Ill_Chronic_live"][1])
        else:
            self.live=słownik["Cell_Ill_Chronic_live"]
            
        if słownik["Draw_Cell_c_mortality_rate"]:
            self.przecinki=słownik["Draw_Cell_Ill_Chronic_c_mortality_rate"]
            self.autodestruction=self.test_przecinkowy()
        else:
            self.autodestruction=self.test(słownik["Cell_Ill_Chronic_c_mortality_rate"])
            
        self.c_become_vector=słownik["Cell_Ill_Chronic_c_become_vector"]
        self.licznik=słownik["All_licznik"]
        self.c_move=słownik["Cell_Ill_Chronic_c_move"]
        self.c_poison=słownik["Cell_Ill_Chronic_c_poison"]

        
    def wybór(self,n,z,lista,lista2) :
        """
        Funkcja definiująca możliwe do wykonania, przez obiekt klasy Cell_Incubating, akcje.
        W tym przypadku, może się ona przemieścić.
        
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
        
        lista (list) : lista na której badana jest dostępność pół w sąsiedztwie.
            
        lista2 (list) : Lista na której nanieść wynik metody
            
        Wynik
        -------
        Lista zawierająca swoje koodynaty i 0, lub koordynaty osobnika którego miejsce zajeła.
        """
        wynik=self.ruch(n,z,lista,lista2)   
        return wynik
   
    def starzenie(self,n,z,lista2):
        """
        Zwiększa wiek obiektu o 1. W przypadku przegroczenia progu, sprawdzana 
        jest wartość parametru "autodestruction. True oznacza zmienę klasy na 
        Cell_Dead_Ill. W przeciwnym przypadku osobnik wykonuje test na zostanie
        nosicielem , w którm niepowodzenie determinuje stanie się
        obiektem klasy Cell_Cured.

        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
            
        lista2 (list) : Lista na której nanieść wynik metody

        Wynik
        -------
        Zwiększenie parametru "licznik". Ostatecznie zmiana klasy.

        """
        if self.licznik >= self.live:#powinna umrzeć z powodu chroby
            if self.autodestruction==False: # jeżeli nie umarła na ASF
                if self.test(self.c_become_vector): # może zostać nosicielem albo wyzdrowieć
                    li=self.licznik
                    lista2[n][z]=Cell_Cured_Infectious()
                    lista2[n][z].licznik=li
                else:
                    li=self.licznik
                    lista2[n][z]=Cell_Cured()
                    lista2[n][z].licznik=li    
            else:
                lista2[n][z]=Cell_Dead_Ill()
                lista2[n][z].licznik=0
        lista2[n][z].licznik+=1
       
class Cell_Dead(Cell):
    """
    Metody oraz parametry przejmuje od klasy rodzicielskiej : Cell.
    Klasa Cell_Dead: niezaraźliwe szczątki osobnika.
    Zawiera parametry:
        symbol (str): reprezentacja graficzna,
        live (int): zakres rozkładu,
        licznik (int) : wiek
    """
    symbol="d"
    def __init__(self):
        """
        Konstruktor klasy Cell_Dead.
        W zależności od wartości logicznej słownik["Draw_Cell_live"]
        przyjmuje rożne wartości.
        """
        super().__init__()
        if słownik["Draw_Cell_Live"]:
            self.live=random.randrange(słownik["Draw_Cell_Dead_live"][0],słownik["Draw_Cell_Dead_live"][1])
        else:
            self.live=słownik["Cell_Dead_live"]
        self.licznik=słownik["All_licznik"]
            
    def starzenie (self,n,z,lista2): 
        """
        Zwiększa wiek obiektu o 1. W przypadku przegroczenia progu, 
        obiektem staje się pustym polem (Cell).

        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
            
        lista2 (list) : Lista na której nanieść wynik metody

        Wynik
        -------
        Zwiększenie parametru "licznik". Ostatecznie zmiana klasy.

        """
        if self.licznik >= self.live:
            lista2[n][z]=Cell()
            lista2[n][z].licznik=0
        lista2[n][z].licznik+=1
         
    def wybór(self,n,z,lista,lista2):
        """
        Funkcja definiująca możliwe do wykonania, przez obiekt klasy Cell_Dead, akcje.
        W tym przypadku, żadne.
        
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
        
        lista (list) : lista na której badana jest dostępność pół w sąsiedztwie.
            
        lista2 (list) : Lista na której nanieść wynik metody
            
        Wynik
        -------
        Lista zawierająca swoje koodynaty i 0, ponieważ ta klasa nie ma zdolności
        przemieszczania się.
        """
        wynik=[[n,z],0]
        return wynik
        
class Cell_Dead_Ill(Cell): 
    """
    Metody oraz parametry przejmuje od klasy rodzicielskiej : Cell.
    Klasa Cell_Dead_Ill: zaraźliwe szczątki osobnika.
    Zawiera parametry:
        symbol (str): reprezentacja graficzna,
        live (int): zakres rozkładu,
        licznik (int) : wiek
        c_poison (float) : prawdopodobieństwa zarażenia zdrowego osobnika,
    """
    symbol="n"
    def __init__(self):
        """
        Konstruktor klasy Cell_Dead_Ill.
        W zależności od wartości logicznej słownik["Draw_Cell_live"]
        przyjmuje rożne wartości.
        """
        super().__init__()
        if słownik["Draw_Cell_Live"]:
            self.live=random.randrange(słownik["Draw_Cell_Dead_Ill_live"][0],słownik["Draw_Cell_Dead_Ill_live"][1])
        else:
            self.live=słownik["Cell_Dead_Ill_live"]
        self.licznik=słownik["All_licznik"]
        self.c_poison=słownik["Cell_Dead_Ill_c_poison"]
   
    def starzenie (self,n,z,lista2): 
        """
        Zwiększa wiek obiektu o 1. W przypadku przegroczenia progu, 
        obiektem wyzbywa się właściwości chorobotwórczych - przechodzi w klasę
        Cell_Dead.

        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
            
        lista2 (list) : Lista na której nanieść wynik metody

        Wynik
        -------
        Zwiększenie parametru "licznik". Ostatecznie zmiana klasy.

        """
        if self.licznik >= self.live:
            li=self.licznik
            lista2[n][z]=Cell_Dead()
            lista2[n][z].licznik=li
        lista2[n][z].licznik+=1
        
    def wybór(self,n,z,lista,lista2):
        """
        Funkcja definiująca możliwe do wykonania, przez obiekt klasy Cell_Dead, akcje.
        W tym przypadku, żadne.
        
        Parameters
        ----------
        n (int) : określa w której lista zbiorcza znajduje się obiekt.
            
        z (int) : indeks w liście zbiorczej.
        
        lista (list) : lista na której badana jest dostępność pół w sąsiedztwie.
            
        lista2 (list) : Lista na której nanieść wynik metody
            
        Wynik
        -------
        Lista zawierająca swoje koodynaty i 0, ponieważ ta klasa nie ma zdolności
        przemieszczania się.
        """
        wynik=[[n,z],0]
        return wynik


def znaki(lista): 
    """
    Konweruję listę obiektów w ciąg liter, poprzez wywołania funkcji znak(), 
    na każdym z nich.
    
    Parameters
    ----------
    lista (list) : lista list z obiektami.

    Wynik
    -------
    tekst (str) : ciąg symboli obiektów.   
    """
    ca2=[]
    zbiór=[]
    for z in range(0,len(lista)): # dopóki nie przejdzie przez kazda liste z listy
        for x in range(0,len(lista[0])): # dla itema z listy_w_srodku
            m=lista[z][x].znak()
            ca2.append(m) # dla każdego obiektu w liscie x 
    zbiór="".join(ca2)
    return zbiór

def stw_macierz_losowa(i_w_szeregu,i_rzędów,ile_alive, ile_inkub): 
    """
    Tworzy środowisko dla symulacji, bazując na podanych argumentach.
    
    Parameters
    ----------
    i_w_szeregu (int) : ilość obiektów w listach wsadowych,
    
    i_rzędów (int) : ilość list wsadowych,
    
    ile_alive (int) : ile obiektów Cell_Alive ma być rozmieszczonych w ,
    
    ile_inkub (int) : ile obiektów Cell_Incubating ma być obsadzonych na 
                     "obrzeżach" środowiska.

    Wynik
    -------
    Zwraca listę list z obiektami.
    """

    r=0
    ded=[]
    macierz=[]
    while r<i_rzędów:
        for x in range(0,i_w_szeregu):
            z=Cell()
            ded.append(z)
        macierz.append(ded)
        r+=1
        ded=[]        
    współrzędne=[]
    lista_krawedzi=[] 
    
    for x in range(1,(i_rzędów-1)): 
        lista_krawedzi.append((x,0)) 
        lista_krawedzi.append((x,i_rzędów-1)) 
      
    for x in range(0,i_w_szeregu):
        lista_krawedzi.append((0,x)) 
        lista_krawedzi.append((i_w_szeregu-1,x)) 
        
    for n in range(0,len(macierz)):
        for z in range(0,len(macierz[0])):
            współrzędne.append((n,z))      
            
    if len(lista_krawedzi) >= ile_inkub:
        for x in range(ile_inkub):           
            a=random.choice(lista_krawedzi)
            macierz[a[0]][a[1]]=Cell_Incubating()
            współrzędne.remove((a[0],a[1]))
            lista_krawedzi.remove((a[0],a[1]))
            
    if len(współrzędne)>=ile_alive: 
        for x in range(ile_alive):
            a=random.choice(współrzędne)
            macierz[a[0]][a[1]]=Cell_Alive()
            współrzędne.remove((a[0],a[1]))
    return(macierz)

def życie_v_2(lista,il_cyklów,nazwa_pliku): 
    """
    Funkcja ta odpowiada za symulację. Jest sprawnym pierwowzorem metod 
    zastosowanych w interefejsie graficznym. 

    Parameters
    ----------
    lista (list) :  zbiór początkowy. ( Generacja_0),
    
    il_cyklów (int) : ile generacji (dni) ma trwać emulacja,
    
    nazwa_pliku (str) : nazwa pliku z rozszerzeniem "*.txt" w którym będzie
                    dokumnetowana symulacja.

    Wynik
    -------
    PLik ".txt" z zapisem przebiegu procesu symulacji.

    """
    m=nazwa_pliku
    if os.path.exists(m):
        os.remove(m)
    with open(m,"w") as f:
        K_N=1
        warstwa_1=lista # podstawka
        ca2=znaki(warstwa_1)
        f.write(str(ca2)+"\n") # zapisz generacje
        współrzędne=[] 
        współrzędne2=[]
        for n in range(0,len(warstwa_1)):
            for z in range(0,len(warstwa_1[0])):
                współrzędne.append([n,z])       
        while K_N< il_cyklów: # dopóty nie przjedzie cyklów

            warstwa_2=warstwa_1.copy()
            współrzędne2=współrzędne.copy()
            while len(współrzędne2)!=0:
                qqq=random.choice((współrzędne2))
                n=qqq[0]
                z=qqq[1]
                wsp_akt=warstwa_1[n][z].wybór(n,z,warstwa_1,warstwa_2) 
                if wsp_akt[0] in współrzędne2:
                    współrzędne2.remove(wsp_akt[0])
                    warstwa_1[n][z].starzenie(wsp_akt[0][0],wsp_akt[0][1],warstwa_2)# wymagane w przypadku ruchu osobnika na pole z tura
                else:
                    współrzędne2.remove(wsp_akt[1])
                    warstwa_1[n][z].starzenie(wsp_akt[1][0],wsp_akt[1][1],warstwa_2)# wymagane w przypadku ruchu osobnika na pole ktore mialo wczesniej wybor
            ca2=znaki(warstwa_2)
            f.write(str(ca2)+"\n") # zapisz generacje
            warstwa_1=warstwa_2.copy()
            K_N+=1

def słownik_kolorów(znak):
    """
    Zwraca odpowiedni dla symbolu danej klasy kolor RGB.
    Używana przy kolorowaniu_map.
    
    Parameters
    ----------
    znak (str) : symbol klasy,

    Wyniki
    -------
    kolor (list) - wartości RGB.

    """
    kom=znak
    kolor=0
    if kom =="x":   # Cell 
        kolor=(255,255,255) #= biały 
    elif kom=="o":   # Cell_Alive 
        kolor=(50,205,50) #= ziel
    elif kom=="v":   #Cell_Cured_Infectious 
        kolor=(146,161,17) #= zgniło-zielony
    elif kom=="q":   # Cell_Incubating   
        kolor=(255, 245, 185) #= żółty
    elif kom =="p":# Cell_Ill_Peracute 
        kolor=(255,0,0) # = mocny czerwony
    elif kom =="a":# Cell_Ill_Acute  
        kolor=(255,0,127)# = rózowa czerwień
    elif kom =="s":# Cell_Ill_Subacute  
        kolor=(255,102,102) #= łosiowy czerwony
    elif kom =="c":# Cell_Ill_Chronic 
        kolor=(255,204,204) #= odcień skóry
    elif kom=="d":   # Cell_Dead 
        kolor=(0,0,0) # = czarny
    elif kom=="n":  # Cell_Dead_Ill 
        kolor=(78, 87, 105) # szary
    elif kom=="k": # Cell_Cured
        kolor=(32,178,170) #niebieski
    return kolor
 
def słownik_typów(znak):
    """
    Używane przy przkeształcaniu symboli z wczytanego pliku z generacjami do
    odtworzenia listy zbiorczej obeiektów.

    Parameters
    ----------
    znak (str): symbol obiektu.

    Wynik
    -------
    Klasa  obiektu.

    """
    kom=znak
    typ="A"
    if kom =="x" : 
        typ=Cell()
    elif kom=="o":
        typ=Cell_Alive()
    elif kom=="v": 
        typ=Cell_Cured_Infectious()
    elif kom=="k":
        typ=Cell_Cured()
    elif kom=="q":
        typ=Cell_Incubating()
    elif kom=="p": 
        typ=Cell_Ill_Peracute()
    elif kom=="a": 
        typ=Cell_Ill_Acute()
    elif kom=="s": 
        typ=Cell_Ill_Subacute()
    elif kom=="c": 
        typ=Cell_Ill_Chronic()
    elif kom=="d":  
        typ=Cell_Dead()
    elif kom=="n":
        typ=Cell_Dead_Ill()
    return typ

def stw_planszę_początkową(): 
    """
    Tworzy oryginalną, niepokolorowaną mapę bitmapową. Ogólny szkic kratownicy,
    która potem jest kolorowana przez inne procesy. Wszelki wartości potrzebne
    do jej stworzenia pobierane są z aktualnie załadowanego słownika.

    Wynik
    -------
    Bitmapa "Generacja_0".

    """
    szerokość = słownik["ile_k_poziom"]
    wysokość = słownik["ile_k_pion"]
    step=słownik["szer_kom"]
    height=wysokość*step # prosta matematyka
    width=szerokość*step
    obraz=Image.new(mode="RGB",size=(width,height),color=(255,255,255)) #mode=F bo dziele niżej
    draw=ImageDraw.Draw(obraz) # nasze tło                          szerokość x wysokość
    x=0
    y_start=0
    y_end=obraz.height
    for x in range(0,width,step): # wszystkie pionowe
        line=((x,y_start),(x,y_end))
        draw.line(line,fill=20)
    line=((width-1,0),(width-1,height))
    draw.line(line,fill=20)
    y=0
    x_start=0
    x_end=obraz.width
    for y in range(0,height,step): # wszystkie poziome lewo-prawo
        line=((x_start,y),(x_end,y))
        draw.line(line,fill=20)
    line=((0,height-1),(width,height-1))
    draw.line(line,fill=20)
    obraz.save("Generacja_0.bmp")

def zapisz_słownik(nazwa,słownik):
    """
    Zapisuje wartości słownika w pliku ".txt".

    Parameters
    ----------
    nazwa (str): nazwa pliku do zapisu,
    słownik (dictionary): słownik, którego wartości zostaną zapisane,

    Wynik
    -------
    Plik ".txt".
    """
    with open(nazwa,"w",encoding="utf-8") as plik :
        for x in  słownik:
            line=x+":"+str(słownik[x])+"\n"
            plik.write(line)
    
def wczytaj_słownik(nazwa):
    """
    Wczytuje wartości wskazanego słownika z pliku ".txt" i aktulizuję 
    zmienną globalna "słownik".

    Parameters
    ----------
    nazwa (str): nazwa pliku do wczytania.

    Wynik
    -------
    Nadpisanie zmiennej "słownik".
    """
    with open(nazwa,"r",encoding="utf-8") as  plik:
        lista_lini=[]
        while True:
            line=plik.readline()
            if not line:
                break
            line=line.replace('\n', '')
            line=line.split(":")
            lista_lini.append(line)    
        słownik={}

        słownik['nazwa_pliku_z_generacjami']=lista_lini[0][1]
        for x in range(1,len(lista_lini)):
           if lista_lini[x][1]=="True":
               słownik[lista_lini[x][0]]=True
           elif lista_lini[x][1]=="False":
               słownik[lista_lini[x][0]]=False
           elif lista_lini[x][1][0]=="(":
               element=(lista_lini[x][1][1:-1]).split(",")
               słownik[lista_lini[x][0]]=(float(element[0]),float(element[1]))
           elif type(lista_lini[x][1])==str:
               if "." in lista_lini[x][1]:
                   słownik[lista_lini[x][0]]=float(lista_lini[x][1])
               else:
                   słownik[lista_lini[x][0]]=int(lista_lini[x][1])              
    return słownik
        
def wczytaj_stan_początkowy(nazwa):
    """
    Ze wskazanego pliku wczytuje ciąg znaków i przekształca go na listę główną 
    z listami zbiorczymi o elementach w postaci obiektów.

    Parameters
    ----------
    nazwa (str) : nazwa pliku "*.txt", w któym znajdue się zapis Środowiska. 

    Wynik
    -------
    Zwraca 
    macierz (list) : Lista list z obiektami.

    """
    dł_ze_słownika=słownik["ile_k_poziom"]
    with open(nazwa,"r") as plik:
        linia=plik.readline()
        linia=linia.replace("\n","")
        macierz=[]
        for x in range(0,len(linia),dł_ze_słownika):
            lista=[]
            for y in (linia[x:x+dł_ze_słownika]):
                y2=słownik_typów(y)
                lista.append(y2)
            macierz.append(lista)
    return macierz                
                    
def koloruj_mapę(ścieżka,macierz,nazwa,krok,szerokość,kolejka): # z macierzy pobiera rzędy i szereg
    """
    Funckja używana w celu stworzenia i umieszczenia w pamięci podrecznej 
    zbioru bitmap, które docelowo zostaną później przeakazane funkcji "z_gifa"
    w celu wizualizacji przebiegu symulacji.
    
    Parameters
    ----------
    ścieżka (str) : nazwa pliku "*.bmp", który jest szkicem, białą planszą z 
    zaznaczoną kratownicą,
    
    macierz (list) : Lista list z obiektami,
    
    nazwa (str) : nazwa pliku "*.txt", w któym znajdue się zapis Środowiska,
    
    krok (int) : odległość pomiędzy liniami kratownicy,
    
    szerokość (int) : ilość obiektów  w lini poziomej,
    
    kolejka (queue) : instancja klasy queue,

    Wynik
    -------
    Dodajanie elementów do zadeklarowanego obiektu "kolejka".
    """
    #sekcja wczytywania danych opisujących arkusz
    podst=Image.open(ścieżka) # zmienna jako oryginal
    im2=podst.copy() # w tym  miejscu robimy kopię oryginału i na nim praucjemy
    n2=0 # licznik szeregów - szerokość
    s_odl=krok
    x0=1
    x1=s_odl
    y0=1
    y1=s_odl
    litera=0
    while litera<len(macierz):# rzędy  | góra -> dół
        n2=0
        while n2<szerokość:# szeregi | lewo-> prawo
            komórka_w=macierz[litera] # ustala który znak
            kolor=słownik_kolorów(komórka_w)  # zwraca odpowiedni mu kolor
            for y in range(y0,y1):
                for x in range(x0,x1):
                    im2.putpixel((x,y),kolor)# ten fragment zamalowuje 1 komórkę
            x0=x0+s_odl
            x1=x1+s_odl
            n2+=1 #szerokość
            litera=litera+1 # ktory element ze str
        n2=0
        x0=1
        x1=s_odl
        y0=y0+s_odl
        y1=y1+s_odl
    tulpa=(im2,nazwa)
    kolejka.put(tulpa)

def z_gifa(zbiór_bitmap):
    """
    Tworzy plik "*.gif", z podanego w argumentach zbioru uszeregowanych 
    chronologicznie bitmap w celu animacji przebiegu symulacji.

    Parameters
    ----------
    zbiór_bitmap (list) : lista bitmap

    Wynik
    -------
    Plik "movie_ASF.gif".

    """
    imageio.mimsave(os.getcwd()+'\\movie.gif', zbiór_bitmap)

def stw_liste(ile_elem):
    """
    Tworzy spreparowną listę o zadanej wielkości, w celu późniejszej podmiany
    we wskazane miejsce po indeksie.
    
    Parameters
    ----------
    ile_elem (int) : wielkość  listy,

    Wynik
    -------
    lista (list) : zwraca listę z pustymi elementami.

    """
    lista=[]
    for x in range(ile_elem):
        lista.append("")
    return lista

def zapisz_stan_poczatkowy(macierz,nazwa):
    """
    Zapisuję przekazaną macierz w formie obiektów w pliku o wskazanej nazwie w 
    folderze ze skryptem.

    Parameters
    ----------
    macierz (list) : lista obiektów,
    
    nazwa (str): nazwa pod którą zostanie zapisany ciąg znaków.

    Wynik
    -------
    Plik ".txt"

    """
    with open(nazwa,'w') as f:
        f.write(str(znaki(macierz))+"\n") # zapisz generacje 
                        
def koloruj_mapę_tylko_początkową(macierz): # z macierzy pobiera rzędy i szereg
    """
    Funkcja kolorująca tylko 1 generację z podstawki krawtownicy, stworzonej
    w funckji "stw_planszę_początkową" o nazwie "Generacja_0.bmp"
    Potrzebne parametry są pobierane z aktualnego słownika.

    Parameters
    ----------
    macierz (list) : lista obiektów,

    Wynik
    -------
    Plik "Plansza_początkowa.bmp"
    """
    krok = słownik["szer_kom"]
    szerokość = słownik["ile_k_poziom"]
    #sekcja wczytywania danych opisujących arkusz
    podst=Image.open("Generacja_0.bmp") # zmienna jako oryginal
    im2=podst.copy() # w tym  miejscu robimy kopię oryginału i na nim praucjemy
    n2=0 # licznik szeregów - szerokość
    s_odl=krok
    x0=1
    x1=s_odl
    y0=1
    y1=s_odl
    litera=0
    while litera<len(macierz):# rzędy  | góra -> dół
        n2=0
        while n2<szerokość:# szeregi | lewo-> prawo
            komórka_w=macierz[litera] # ustala który znak
            kolor=słownik_kolorów(komórka_w)  # zwraca odpowiedni mu kolor
            for y in range(y0,y1):
                for x in range(x0,x1):
                    im2.putpixel((x,y),kolor)# ten fragment zamalowuje 1 komórkę
            x0=x0+s_odl
            x1=x1+s_odl
            n2+=1 #szerokość
            litera=litera+1 # ktory element ze str
        n2=0
        x0=1
        x1=s_odl
        y0=y0+s_odl
        y1=y1+s_odl
    im2.save("Plansza_początkowa.bmp")

def Analiza(nazwa):
    """
    Analizuję wskazany plik i produkuje nastepujące statystyki:
        - zachorowalność (int) : ilość zarażonych / dzień
        - zasieg (int) : ile przybyło zarażonych miejsc / dzień
        - łączną ilość zarażonych (int) / dzień
        - śmiertelność  (int) : łączne zgony spowodowane wirusem /od początku do tego dnia
        
    Parameters
    ----------
    nazwa (str) : nazwa pliku który będzie analizowany *.txt
    
    Wynik
    -------
    plik ".txt"
    """
    lista_generalna=[] # 
    licznik=0 # warunkuje wyliczanie pozycji .seek()
    lista_współrzędnych_inf=[] # koordynaty 
    l_23=[]
    lista_współrzędnych_martwych_inf=[]
    
    lista_generacji=[0,0,0,0,0,0,0,0,0,0,0] # ile było każdego typu na generację
                    #x,o,v,q,p,a,s,c,d,n,k
    l_pom=[]
    with open(nazwa,"r") as f:
        ile_znaków=len(f.readline().replace('\n', '')) # ile jest obiektow
        pierw=int(math.sqrt(ile_znaków)) # ile jest znakow na "rząd"
        while True :   
            f.seek((ile_znaków+2)*licznik)# +2 ze względu na "\n" na końcu lini
            txt_generacji=f.readline()
            if not txt_generacji :
                break
            else:
                txt_generacji.replace('\n', '')
            n_1=0 #koordynat 1
            for x in range(0,len(txt_generacji),pierw):
                x_2=0 #koordynat 2
                for kom in (txt_generacji[x:x+pierw]):
                    if kom =="x":  #puste pole
                        lista_generacji[0]+=1
                    elif kom=="o":   #zdrowa
                        lista_generacji[1]+=1
                    elif kom=="v":  #nosiciel
                        lista_generacji[2]+=1
                    elif kom=="q":     #inkub
                        lista_generacji[3]+=1
                        element=(n_1,x_2)
                        if element not in l_pom:
                            lista_współrzędnych_inf.append(element)
                            l_pom.append(element)
                    elif kom =="p":#peracute
                        lista_generacji[4]+=1
                    elif kom =="a":#acute
                        lista_generacji[5]+=1 
                    elif kom =="s": #subacute
                        lista_generacji[6]+=1
                    elif kom =="c":#chronical
                        lista_generacji[7]+=1
                    elif kom=="d":   #dead
                        lista_generacji[8]+=1
                    elif kom=="n":   #dead_ill
                        lista_generacji[9]+=1
                        element=(n_1,x_2)
                        if element not in lista_współrzędnych_martwych_inf:
                            lista_współrzędnych_martwych_inf.append(element)
                    elif kom=="k": #cured
                        lista_generacji[10]+=1 
                    x_2+=1
                n_1+=1
            l_23.append(int(len(lista_współrzędnych_inf)))
            lista_łącząca=[lista_generacji,l_23]  
            lista_generalna.append(lista_łącząca)
            lista_generacji=[0,0,0,0,0,0,0,0,0,0,0] # ile było każdego typu na generację 
            lista_współrzędnych_inf=[]
            licznik+=1
    zamrło_na_chorob=len(lista_współrzędnych_martwych_inf) / lista_generalna[0][0][1]
    l_zachorowalności=[]
    for x in range(len(lista_generalna)): # patrze na dni po kolei
        try:
            r_zdrowych=abs((lista_generalna[x][0][1]-lista_generalna[x-1][0][1])) #moze sie tylko zmniejszac
            r_truchl_norm=(lista_generalna[x][0][8]-lista_generalna[x-1][0][8]) # jezeli przybylo to bedzie na plusie
            r_pustych=(lista_generalna[x][0][0]-lista_generalna[x-1][0][0]) # moze tylko sie zwiekszac
            suma=r_truchl_norm+r_pustych
            if suma > r_zdrowych:
                zqwr=r_zdrowych
            else:
               zqwr= r_zdrowych-(r_truchl_norm +r_pustych)
            l_zachorowalności.append(zqwr)
        except:
            l_zachorowalności.append(0)
    l_zaraz_w_czasie=0
    l_zachorowalności[0]=0
    nazwa2="Analiza_"+nazwa
    napis0="Dzień;Zasięg;Zachorowania;Łącznie_zarażonych\n"
    with open(nazwa2,'w') as f:
        f.write(napis0)
        for x in range(len(lista_generalna)):
            f.write("Dzień_"+str(x)+";"+str(l_23[x])+";"+str(l_zachorowalności[x])+";"+str(l_zaraz_w_czasie)+"\n") # zapisz generacje 
            l_zaraz_w_czasie+=l_zachorowalności[x]
        napis1="Śmiertelność : "+str(zamrło_na_chorob)+"\n"
        f.write(napis1)
        
def Stwórz_pliki_słownika_oraz_plansze(lista_wartosci, lista_pozycji):
    """
    Funkcja tworząca pliki konfiguracyjne w postaci słownika i srodowisk.
    Np:
    lista_wartosci=[[int,int],[int,int,int]]
    lista_pozycji=[[str,str],[str,str,str]]
    Parameters
    ----------
    lista_wartosc (list) : wartosci które będą podmieniane w oryginalnym slowniku.
    
    lista_pozycji (list) : pozycję do podmienienia w oryginalnym slowniku.

    Wynik
    -------
    pliki *.txt srodowisk, slownikow + 2 pliki z ich spisem.

    """
    wartosci_do_zmiany=lista_wartosci
    nazwy_słowników=[]
    nazwy_plansz_początkowych=[]
    global słownik
    for n in range(len(lista_pozycji)):
        for x in range(len(wartosci_do_zmiany)):
            słownik[lista_pozycji[n][x]]=lista_wartosci[n][x]
        gestosc=round(słownik["ile_alive"]/(słownik["ile_k_pion"]*słownik["ile_k_pion"]),1)
        nazwa21="Slownik_"+str(słownik["Draw_move_time"])+"_"+str(słownik["ile_inkub"])+"x"+str(gestosc)+"x"+str(słownik["ile_alive"])+".txt"
        nazwy_słowników.append(nazwa21)
        zapisz_słownik(nazwa21,słownik)
        
        nazwa212="Srodowisko_"+str(słownik["Draw_move_time"])+"_"+str(słownik["ile_inkub"])+"x"+str(gestosc)+"x"+str(słownik["ile_alive"])+".txt"
        nazwy_plansz_początkowych.append(nazwa212)
        macierz=stw_macierz_losowa(słownik["ile_k_poziom"],słownik["ile_k_pion"],słownik["ile_alive"], słownik["ile_inkub"]) #tworzy podstawową macierz z osobnikami
        zapisz_stan_poczatkowy(macierz,nazwa212)
    with open("Spis_nazwy_Srodowisk.txt","a") as f:
        for x in nazwy_plansz_początkowych:
            f.write(x+"\n")     
    with open("Spis_nazwy_Slowników.txt","a") as f:
        for x in nazwy_słowników:
            f.write(x+"\n")

        
        
if __name__ == '__main__':
    app = wx.App()
    ex = Okno_glowne()
    ex.Show()
    app.MainLoop()