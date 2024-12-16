#!/usr/bin/env python3

from os.path import basename, splitext, exists
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
import requests


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

        self.lblTransaction = tk.LabelFrame(self, text="Transakce")
        self.lblTransaction.pack(anchor='w', padx=5)
        self.varTransaction = tk.StringVar(value="purchase")
        self.rbtnPurchase = tk.Radiobutton(self.lblTransaction, text="Nákup", variable=self.varTransaction, value="purchase")
        self.rbtnSale = tk.Radiobutton(self.lblTransaction, text="Prodej", variable=self.varTransaction, value="sale")
        self.rbtnPurchase.pack()
        self.rbtnSale.pack()

        self.varTransaction.trace_add("write", self.transactionClick)

        self.cboxCountry = ttk.Combobox(self, values=[])
        self.cboxCountry.set("Vyber zemi...")
        self.cboxCountry.pack(anchor="w", padx=5, pady=5)
        self.cboxCountry.bind("<<ComboboxSelected>>", self.on_select)

        self.lblCourse = tk.LabelFrame(self, text="Kurz")
        self.lblCourse.pack(anchor='w', padx=5, pady=5)
        self.entryAmount = MyEntry(self.lblCourse, state="readonly")
        self.entryAmount.pack()
        self.entryRate = MyEntry(self.lblCourse, state="readonly")
        self.entryRate.pack()

        self.lblConversion = tk.LabelFrame(self, text="Konverze")
        self.lblConversion.pack(anchor='w', padx=5, pady=5)

        val_f_tuple = (self.register(self.validate), "%P", "%s")

        self.entryInputAmount = MyEntry(self.lblConversion, validate="key", validatecommand=val_f_tuple)
        self.entryInputAmount.grid(row=0, column=0, padx=5, pady=2)
        self.entryInputAmount.variable.trace_add("write", self.convert)

        self.lblInput = tk.Label(self.lblConversion, text="--", width=5)
        self.lblInput.grid(row=0, column=1, padx=5, pady=2)

        self.entryOutputAmount = MyEntry(self.lblConversion, state="readonly")
        self.entryOutputAmount.grid(row=1, column=0, padx=5, pady=2)
        self.lblOutput = tk.Label(self.lblConversion, text="--", width=5)
        self.lblOutput.grid(row=1, column=1, padx=5, pady=2)

        self.btn = tk.Button(self, text="Quit", command=self.quit)
        self.btn.pack()

        self.on_load()

    def transactionClick(self, *arg):
        self.on_select()

    def chbtnAutoClick(self):
        if self.varAuto.get():
            self.btnDownload.config(state=tk.DISABLED)
            self.check_and_download()
            self.after(60000, self.periodic_check)
        else:
            self.btnDownload.config(state=tk.NORMAL)
    
    def check_and_download(self):
        if not exists('kurzovni_listek.txt'):
            self.download()
            return

        with open('kurzovni_listek.txt', 'r') as f:
            first_line = f.readline().strip()

        try:
            file_date = datetime.strptime(first_line.split(" #")[0], '%d %b %Y')
            today = datetime.now()
            if file_date.date() < today.date():
                self.download()
        except ValueError:
            self.download()

    def periodic_check(self):
        if self.varAuto.get():
            self.check_and_download()
        self.after(60000, self.periodic_check)

    def download(self):
        URL = 'https://www.cnb.cz/en/financial_markets/foreign_exchange_market/exchange_rate_fixing/daily.txt'
        try:
            response = requests.get(URL)
            with open('kurzovni_listek.txt', 'w') as f:
                f.write(response.text)
            self.on_load()
        except requests.exceptions.ConnectionError as e:
            print(f"Error: {e}")
            if not exists('kurzovni_listek.txt'):
                messagebox.showerror("Chyba:", "Kurzovní lístek nenalezen")
                return
            self.on_load()

    def on_load(self):
        if not exists('kurzovni_listek.txt'):
            messagebox.showerror("Chyba:", "Kurzovní lístek nenalezen")
            return
        with open('kurzovni_listek.txt', 'r') as f:
            data = f.read()
        self.ticket = {}
        for line in data.splitlines()[2:]:
            country, currency, amount, code, rate = line.split('|')
            self.ticket[country] = {
                'currency': currency,
                'amount': amount,
                'code': code,
                'rate': rate,
            }
        self.cboxCountry.config(values=list(self.ticket.keys()))

    def on_select(self, event=None):
        try:
            country = self.cboxCountry.get()
            self.lblCourse.config(text=self.ticket[country]['code'])
            self.amount = int(self.ticket[country]['amount'])
            if self.varTransaction.get() == 'purchase':
                self.rate = float(self.ticket[country]['rate']) * 0.96
            else:
                self.rate = float(self.ticket[country]['rate']) * 1.04

            self.entryAmount.value = str(self.amount)
            self.entryRate.value = str(self.rate)

            # Update labels for input and output
            if self.varTransaction.get() == 'purchase':
                self.lblInput.config(text="CZK")
                self.lblOutput.config(text=self.ticket[country]['code'])
                self.convert()
            else:
                self.lblInput.config(text=self.ticket[country]['code'])
                self.lblOutput.config(text="CZK")
                self.convert()
        except KeyError:
            pass
    
    def validate(self, P: str, s):
        P = P.replace(",", ".")
        if P == "":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False

    def convert(self, *args):
        try:
            input_amount = float(self.entryInputAmount.value.replace(",", "."))
            if self.varTransaction.get() == 'purchase':
                result = input_amount / self.rate
            else:
                result = input_amount * self.rate

            self.entryOutputAmount.value = str(f"{result:.2f}")
        except (ValueError, KeyError, AttributeError):
            self.entryOutputAmount.value = ""

    def quit(self, event=None):
        super().destroy()


app = Application()
app.mainloop()
