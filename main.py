#!/usr/bin/env python3

from os.path import basename, splitext
import tkinter as tk
import datetime
import requests

# from tkinter import ttk


class MyEntry(tk.Entry):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)

        if "textvariable" not in kw:
            self.variable = tk.StringVar()
            self.config(textvariable=self.variable)
        else:
            self.variable = kw["textvariable"]

    @property
    def value(self):
        return self.variable.get()

    @value.setter
    def value(self, new: str):
        self.variable.set(new)


class About(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent, class_=parent.name)
        self.config()

        btn = tk.Button(self, text="Konec", command=self.close)
        btn.pack()

    def close(self):
        self.destroy()


class Application(tk.Tk):
    name = basename(splitext(basename(__file__.capitalize()))[0])
    name = "Foo"

    def __init__(self):
        super().__init__(className=self.name)
        self.title(self.name)
        self.bind("<Escape>", self.quit)
        self.lbl = tk.Label(self, text="Smenarna")
        self.lbl.pack()


        self.varAuto = tk.BooleanVar()
        self.chbtnAuto = tk.Checkbutton(self, text="Stahovat automaticky kurzovní lístek", variable=self.varAuto, command=self.chbtnAutoClick)
        self.chbtnAuto.pack()
        self.btnDownload = tk.Button(self, text="Stáhnout kurzovní lístek", command=self.download)
        self.btnDownload.pack()

        self.lblTransaction = tk.LabelFrame(self, text="Transakece")
        self.lblTransaction.pack(anchor='w', padx=5)
        self.varTransaction = tk.StringVar(value="purchase")
        self.rbtnPurchase = tk.Radiobutton(self.lblTransaction, text="Nákup", variable=self.varTransaction, value="purchase")
        self.rbtnSale = tk.Radiobutton(self.lblTransaction, text="Prodej", variable=self.varTransaction, value="sale")
        self.rbtnPurchase.pack()
        self.rbtnSale.pack()

        self.btn = tk.Button(self, text="Quit", command=self.quit)
        self.btn.pack()

    def chbtnAutoClick(self):
        if self.varAuto.get():
            self.btnDownload.config(state=tk.DISABLED)
        else:
            self.btnDownload.config(state=tk.NORMAL)
    
    def download(self):
        URL='https://www.cnb.cz/en/financial_markets/foreign_exchange_market/exchange_rate_fixing/daily.txt'
        try:
            response = requests.get(URL)
            data = response.text
            with open('kurzovni_listek.text', 'w') as f:
                f.write(data)
            for line in data.splitlines()[2:]:
                country, currency, amount, code, rate = line.split('|')
        except requests.exceptions.ConnectionError as e:
            print(f"Error: {e}")
            return

    def quit(self, event=None):
        super().destroy()


app = Application()
app.mainloop()
