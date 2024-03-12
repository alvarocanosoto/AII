#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import re
import datetime

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def extraer_recetas():    
    import locale
    locale.setlocale(locale.LC_TIME, "es_ES")
    
    lista=[]
    f = urllib.request.urlopen("https://www.recetasgratis.net/Recetas-de-Aperitivos-tapas-listado_receta-1_1.html")
    s = BeautifulSoup(f,"lxml")
    l= s.find_all("div", class_=['resultado','link'])
    for i in l:
        titulo = i.a.string.strip()
        dificultad = i.find('div', class_="info_snippet").find("span",string=re.compile("Dificultad"))
        if dificultad:
            dificultad = dificultad.string.strip()
            dificultad = dificultad.replace('Dificultad','').strip()
        else:
            dificultad = "desconocida"
        comensales = i.find("span",class_="comensales")
        if comensales:
            comensales = int(comensales.string.strip())
        else:
            comensales=-1
        duracion = i.find("span",class_="duracion")
        if duracion:
            duracion = duracion.string.strip()
            minutos = re.findall('(\d+)([hm])',duracion)
            if len(minutos)==1:
                if minutos[0][1] == 'm':
                    duracion = int(minutos[0][0])
                else: # en horas
                    duracion = 60*int(minutos[0][0])              
            else:
                duracion = 60*int(minutos[0][0])+int(minutos[1][0])
        else:
            duracion=-1

        f1 = urllib.request.urlopen(i.find('a')['href'])
        s1 = BeautifulSoup(f1,"lxml")
        autor = s1.find("div", class_='nombre_autor').a.string.strip()
        fecha = s1.find("div", class_='nombre_autor').find('span', class_="date_publish").string
        fecha = fecha.replace('Actualizado:','').strip()
        fecha = datetime.datetime.strptime(fecha, "%d %B %Y")
                
        lista.append((titulo, dificultad, comensales, duracion, autor, fecha))
        
    return lista


def imprimir_lista(cursor):
    v = Toplevel()
    v.title("LISTADO DE RECETAS")
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width = 150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,row[0])
        lb.insert(END,"    Dificultad: "+ row[1])
        lb.insert(END,"    Comensales: "+ str(row[2] if row[2]>=0 else "desconocido"))
        lb.insert(END,"    Duracion: "+ str(row[3] if row[3]>=0 else "desconocido") + " minutos")
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT,fill=BOTH)
    sc.config(command = lb.yview)

def imprimir_lista_1(cursor,recetasporautor):
    v = Toplevel()
    v.title("RECETAS DEL " + recetasporautor)
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width = 150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,row[0])
        lb.insert(END,"    Dificultad: "+ row[1])
        lb.insert(END,"    Comensales: "+ str(row[2] if row[2]>=0 else "desconocido"))
        lb.insert(END,"    Duracion: "+ str(row[3] if row[3]>=0 else "desconocido") + " minutos")
        lb.insert(END,"    Autor: "+ row[4])
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT,fill=BOTH)
    sc.config(command = lb.yview)
    
def imprimir_lista_2(cursor,recetasporfecha):
    v = Toplevel()
    v.title("RECETAS ANTERIORES AL " + recetasporfecha)
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width = 150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,row[0])
        lb.insert(END,"    Dificultad: "+ row[1])
        lb.insert(END,"    Comensales: "+ str(row[2] if row[2]>=0 else "desconocido"))
        lb.insert(END,"    Duracion: "+ str(row[3] if row[3]>=0 else "desconocido") + " minutos")
        fecha = datetime.datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")
        fecha_formateada = datetime.datetime.strftime(fecha,"%d/%m/%Y")
        lb.insert(END,"    Fecha de publicacion: "+ fecha_formateada)
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT,fill=BOTH)
    sc.config(command = lb.yview)
    
 
def almacenar_bd():
    conn = sqlite3.connect('recetas.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS RECETAS") 
    conn.execute('''CREATE TABLE RECETAS
       (TITULO     TEXT    NOT NULL,
       DIFICULTAD  TEXT    ,
       COMENSALES  INT    ,
       DURACION     INT   ,
       AUTOR       TEXT,
       FECHA       DATE);''')

    for i in extraer_recetas():              
        conn.execute("""INSERT INTO RECETAS VALUES (?,?,?,?,?,?)""",i)
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM RECETAS")
    cursor1 = conn.execute("SELECT COUNT (DISTINCT AUTOR) FROM RECETAS")
    messagebox.showinfo( "Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " recetas y " + str(cursor1.fetchone()[0]) + " autores")
    conn.close()


def listar_recetas():
    conn = sqlite3.connect('recetas.db')
    conn.text_factory = str  
    cursor = conn.execute("SELECT * FROM RECETAS")
    imprimir_lista(cursor)
    conn.close()
    
 
def buscar_por_autores():
    def listar(event):
            conn = sqlite3.connect('recetas.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT * FROM RECETAS where AUTOR LIKE '%" + str(autor.get()) + "%'")
            conn.close
            imprimir_lista_1(cursor,"AUTOR "+ autor.get())
    
    conn = sqlite3.connect('recetas.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT DISTINCT AUTOR FROM RECETAS")
    
    autores = [i[0] for i in cursor]

    v = Toplevel()
    label = Label(v,text="Seleccione el autor: ")
    label.pack(side=LEFT)
    autor = Spinbox(v, width= 30, values=autores, state='readonly')
    autor.bind("<Return>", listar)
    autor.pack(side=LEFT)
    
    conn.close()   

def buscar_por_fecha():
    def listar(event):
            conn = sqlite3.connect('recetas.db')
            conn.text_factory = str
            fec = re.match(r"\d\d/\d\d/\d{4}",entry.get().strip())
            if fec:
                fecha = datetime.datetime.strptime(entry.get().strip(),"%d/%m/%Y")
                cursor = conn.execute("SELECT * FROM RECETAS WHERE FECHA < ?", (fecha,))
                conn.close
                imprimir_lista_2(cursor, entry.get().strip() )
            else:
                messagebox.showerror("Error", "Formato de fecha incorrecto")
    
    
    v = Toplevel()
    label = Label(v,text="Escriba la fecha (dd/mm/aaaa): ")
    label.pack(side=LEFT)
    entry = Entry(v)
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)   
  
def ventana_principal():       
    root = Tk()
    root.geometry("150x100")

    menubar = Menu(root)
    
    datosmenu = Menu(menubar, tearoff=0)
    datosmenu.add_command(label="Cargar", command=almacenar_bd)
    datosmenu.add_separator()   
    datosmenu.add_command(label="Salir", command=root.quit)
    
    menubar.add_cascade(label="Datos", menu=datosmenu)
    
    listarmenu = Menu(menubar, tearoff=0)
    listarmenu.add_command(label="Recetas", command=listar_recetas)
    
    
    menubar.add_cascade(label="Listar", menu=listarmenu)
    
    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Recetas por autor", command=buscar_por_autores)
    buscarmenu.add_command(label="Recetas por fecha", command=buscar_por_fecha)
    
    menubar.add_cascade(label="Buscar", menu=buscarmenu)
        
    root.config(menu=menubar)
    root.mainloop()

    

if __name__ == "__main__":
    ventana_principal()