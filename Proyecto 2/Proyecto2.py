import os
import pygame
from pygame import mixer
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class NodoCancion:
    def __init__(self, nombre, artista, duracion, ruta):
        self.nombre = nombre
        self.artista = artista
        self.duracion = duracion
        self.ruta = ruta
        self.siguiente = None
        self.anterior = None

class ListaReproduccion:
    def __init__(self):
        self.cabeza = None
        self.actual = None
        self.tamanio = 0
    
    def esta_vacia(self):
        return self.cabeza is None
    
    def agregar_cancion(self, nombre, artista, duracion, ruta):
        nuevo_nodo = NodoCancion(nombre, artista, duracion, ruta)
        
        if self.esta_vacia():
            nuevo_nodo.siguiente = nuevo_nodo
            nuevo_nodo.anterior = nuevo_nodo
            self.cabeza = nuevo_nodo
            self.actual = nuevo_nodo
        else:
            ultimo = self.cabeza.anterior
            
            nuevo_nodo.siguiente = self.cabeza
            nuevo_nodo.anterior = ultimo
            ultimo.siguiente = nuevo_nodo
            self.cabeza.anterior = nuevo_nodo
        
        self.tamanio += 1
    
    def eliminar_cancion(self, nombre):
        if self.esta_vacia():
            return False
        
        actual = self.cabeza
        encontrado = False
        
        for _ in range(self.tamanio):
            if actual.nombre == nombre:
                encontrado = True
                break
            actual = actual.siguiente
        
        if not encontrado:
            return False
        
        if self.tamanio == 1:
            self.cabeza = None
            self.actual = None
        else:
            if actual == self.cabeza:
                self.cabeza = actual.siguiente
            
            if actual == self.actual:
                self.actual = actual.siguiente
            
            actual.anterior.siguiente = actual.siguiente
            actual.siguiente.anterior = actual.anterior
        
        self.tamanio -= 1
        return True
    
    def obtener_lista_canciones(self):
        canciones = []
        if self.esta_vacia():
            return canciones
        
        actual = self.cabeza
        for _ in range(self.tamanio):
            canciones.append(f"{actual.nombre} - {actual.artista} ({actual.duracion})")
            actual = actual.siguiente
        
        return canciones
    
    def siguiente_cancion(self):
        if not self.esta_vacia():
            self.actual = self.actual.siguiente
            return self.actual
        return None
    
    def anterior_cancion(self):
        if not self.esta_vacia():
            self.actual = self.actual.anterior
            return self.actual
        return None
    
    def obtener_cancion_actual(self):
        return self.actual

class ReproductorMusica:
    def __init__(self, root):
        self.root = root
        self.root.title("Reproductor de Música")
        self.root.geometry("800x400")
        
        
        pygame.init()
        mixer.init()
        
        
        self.lista_reproduccion = ListaReproduccion()
        
        
        self.reproduciendo = False
        self.pausado = False
        
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        
        btn_anterior = tk.Button(control_frame, text="⏮ Anterior", command=self.anterior)
        btn_anterior.pack(side=tk.LEFT, padx=5)
        
        btn_play = tk.Button(control_frame, text="▶ Reproducir", command=self.reproducir)
        btn_play.pack(side=tk.LEFT, padx=5)
        
        btn_pausa = tk.Button(control_frame, text="⏸ Pausar", command=self.pausar)
        btn_pausa.pack(side=tk.LEFT, padx=5)
        
        btn_detener = tk.Button(control_frame, text="⏹ Detener", command=self.detener)
        btn_detener.pack(side=tk.LEFT, padx=5)
        
        btn_siguiente = tk.Button(control_frame, text="⏭ Siguiente", command=self.siguiente)
        btn_siguiente.pack(side=tk.LEFT, padx=5)
        
        
        carga_frame = tk.Frame(main_frame)
        carga_frame.pack(fill=tk.X, pady=5)
        
        btn_cargar = tk.Button(carga_frame, text="Cargar Canciones", command=self.cargar_canciones)
        btn_cargar.pack(side=tk.LEFT, padx=5)
        
        btn_eliminar = tk.Button(carga_frame, text="Eliminar Seleccionada", command=self.eliminar_cancion)
        btn_eliminar.pack(side=tk.LEFT, padx=5)
        
        
        self.lista_canciones = ttk.Treeview(main_frame, columns=('Artista', 'Duración'), selectmode='browse')
        self.lista_canciones.heading('#0', text='Canción')
        self.lista_canciones.heading('Artista', text='Artista')
        self.lista_canciones.heading('Duración', text='Duración')
        self.lista_canciones.column('#0', width=200)
        self.lista_canciones.column('Artista', width=150)
        self.lista_canciones.column('Duración', width=100)
        
        scroll = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.lista_canciones.yview)
        self.lista_canciones.configure(yscroll=scroll.set)
        
        self.lista_canciones.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        
        self.etiqueta_estado = tk.Label(main_frame, text="No hay canciones cargadas", anchor=tk.W)
        self.etiqueta_estado.pack(fill=tk.X, pady=5)
    
    def cargar_canciones(self):
        archivos = filedialog.askopenfilenames(
            title="Seleccionar canciones",
            filetypes=[("Archivos de audio", "*.mp3 *.wav *.ogg")]
        )
        
        if not archivos:
            return
        
        for archivo in archivos:
            nombre = os.path.basename(archivo)
            nombre_sin_ext = os.path.splitext(nombre)[0]
            artista = "Desconocido"
            duracion = "0:00"
            
            
            if " - " in nombre_sin_ext:
                artista, nombre_cancion = nombre_sin_ext.split(" - ", 1)
                nombre = nombre_cancion
            else:
                nombre = nombre_sin_ext
            
            self.lista_reproduccion.agregar_cancion(nombre, artista, duracion, archivo)
        
        self.actualizar_lista()
    
    def actualizar_lista(self):
        
        for item in self.lista_canciones.get_children():
            self.lista_canciones.delete(item)
        
        
        if not self.lista_reproduccion.esta_vacia():
            actual = self.lista_reproduccion.cabeza
            for _ in range(self.lista_reproduccion.tamanio):
                self.lista_canciones.insert(
                    '', 'end', 
                    text=actual.nombre,
                    values=(actual.artista, actual.duracion)
                )
                actual = actual.siguiente
            
            
            if self.lista_reproduccion.obtener_cancion_actual() is None:
                self.lista_reproduccion.actual = self.lista_reproduccion.cabeza
            
            self.actualizar_etiqueta_estado()
    
    def eliminar_cancion(self):
        seleccion = self.lista_canciones.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una canción para eliminar")
            return
        
        item = seleccion[0]
        nombre_cancion = self.lista_canciones.item(item, 'text')
        
        if self.lista_reproduccion.eliminar_cancion(nombre_cancion):
            self.actualizar_lista()
            
            if self.reproduciendo:
                mixer.music.stop()
                self.reproduciendo = False
                self.pausado = False
        else:
            messagebox.showerror("Error", "No se pudo eliminar la canción")
    
    def reproducir(self):
        if self.lista_reproduccion.esta_vacia():
            messagebox.showwarning("Advertencia", "No hay canciones en la lista de reproducción")
            return
        
        cancion_actual = self.lista_reproduccion.obtener_cancion_actual()
        
        if not self.reproduciendo and not self.pausado:
            mixer.music.load(cancion_actual.ruta)
            mixer.music.play()
            self.reproduciendo = True
            self.pausado = False
        elif self.pausado:
            mixer.music.unpause()
            self.pausado = False
            self.reproduciendo = True
        
        self.actualizar_etiqueta_estado()
    
    def pausar(self):
        if self.reproduciendo:
            mixer.music.pause()
            self.pausado = True
            self.reproduciendo = False
            self.actualizar_etiqueta_estado()
    
    def detener(self):
        if self.reproduciendo or self.pausado:
            mixer.music.stop()
            self.reproduciendo = False
            self.pausado = False
            self.actualizar_etiqueta_estado()
    
    def siguiente(self):
        if self.lista_reproduccion.esta_vacia():
            return
        
        if self.reproduciendo or self.pausado:
            self.detener()
        
        self.lista_reproduccion.siguiente_cancion()
        
        if self.reproduciendo or self.pausado:
            self.reproducir()
        
        self.actualizar_etiqueta_estado()
    
    def anterior(self):
        if self.lista_reproduccion.esta_vacia():
            return
        
        if self.reproduciendo or self.pausado:
            self.detener()
        
        self.lista_reproduccion.anterior_cancion()
        
        if self.reproduciendo or self.pausado:
            self.reproducir()
        
        self.actualizar_etiqueta_estado()
    
    def actualizar_etiqueta_estado(self):
        if self.lista_reproduccion.esta_vacia():
            self.etiqueta_estado.config(text="No hay canciones cargadas")
            return
        
        cancion_actual = self.lista_reproduccion.obtener_cancion_actual()
        estado = f"Canción actual: {cancion_actual.nombre} - {cancion_actual.artista}"
        
        if self.reproduciendo:
            estado += " (Reproduciendo)"
        elif self.pausado:
            estado += " (Pausado)"
        else:
            estado += " (Detenido)"
        
        self.etiqueta_estado.config(text=estado)
        
        
        for item in self.lista_canciones.get_children():
            if self.lista_canciones.item(item, 'text') == cancion_actual.nombre:
                self.lista_canciones.selection_set(item)
                self.lista_canciones.see(item)
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = ReproductorMusica(root)
    root.mainloop() 