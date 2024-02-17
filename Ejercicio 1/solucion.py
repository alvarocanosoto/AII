import re
import urllib.request
import os.path

def extraer_lista(file):
    f = open(file, "r", encoding = 'utf-8') #abre el archivo en modo lectura ("r") y lo guardo en f 
    s = f.read() #lee el contenido del archivo y lo almacena en una variable como cadena de texto
    l1 = re.findall(r'<title>(.*)</title>\s*<link>(.*)</link>', s) #buscar los patrones de texto que coincidan con la expresión regular r'...
    l2 = re.findall(r'<pubDate>(.*)</pubDate>', s)
    l = [] #crea lista vacía
    l = [list(e1) for e1 in l1] #itera sobre los elementos de l1 y los convierte en una lista
    for e1, e2 in zip (l, l2): #para cada par de elementos se añade la fecha de publicación al final de la lista que representa la noticia
        e1.append(e2)
    f.close() #cierra el archivo después para leer su contenido para liberar recursos
    return l[1:] #devuelve la lista l a partir del segundo elemento

def imprimir_lista(l): 
    for t in l: #para cada elemento de la lista, lo imprime
        print ("Título:", str(t[0])) 
        print ("Link:", t[1])
        f=formatear_fecha(t[2]) #guarda en una variable f las fechas formateadas
        print ("Fecha: {0:2s}/{1:2s}/{2:4s}\n".format(f[0],f[1],f[2])) #format sirve para incrustar valores dentro de una cadena de texto 

def formatear_fecha(s): #le entra la fecha de un elemento de la lista de noticias y devuelve la fecha actualizada
    meses={'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    fecha = re.match(r'.*(\d\d)\s*(.{3})\s*(\d{4}).*', s) #busca un patrón que coincida con la expresión regular
    l = list(fecha.groups()) #obtiene una tupla de los grupos encontrados en s y los convierte en lista. Esto crea una lista que contiene el día, mes y año como elementos
    l[1] = meses[l[1]] #actualiza los meses según el diccionario
    return tuple(l) #devuelve una tupla con el día, el mes (actualizado), y el año

def buscar_fecha(l): #busca noticias que coincidan con la fecha introducida por el usuario
    mes = input("Introduzca el mes (mm):")
    dia = input("Introduzca el dia (dd):")
    enc=False #flag para ver si se encontraron fechas 
    for t in l:
        f = formatear_fecha(t[2]) 
        if mes == f[1] and dia == f[0]: #si encuentra, la imprime
            print ("Título:", str(t[0]))
            print ("Link:", t[1])
            print ("Fecha: {0:2s}/{1:2s}/{2:4s}\n".format(f[0],f[1],f[2]))
            enc = True
    if not enc:
        print ("No hay noticias para ese mes")
        
def abrir_url(url,file):
    try:
        if os.path.exists(file):
            recarga = input("La página ya ha sido cargada. Desea recargarla (s/n)?")
            if recarga == "s":
                urllib.request.urlretrieve(url,file)
        else:
            urllib.request.urlretrieve(url,file)
        return file
    except:
        print  ("Error al conectarse a la página")
        return None


if __name__ == "__main__": #para comprobar que se ejecuta como un script
    fichero = "noticias" #creo un fichero que se llama noticias
    if abrir_url("https://sevilla.abc.es/rss/feeds/Sevilla_Sevilla.xml",fichero):
        l = extraer_lista(fichero)
    if l:
        imprimir_lista(l)
        buscar_fecha(l)