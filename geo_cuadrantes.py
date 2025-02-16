import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point, Polygon
import webbrowser

class DistritoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Asignador de Cuadrantes")
        self.root.geometry("400x300")
        
        self.label = tk.Label(root, text="Seleccione los archivos")
        self.label.pack(pady=10)
        
        self.btn_cargar_excel = tk.Button(root, text="Cargar Excel", command=self.cargar_excel)
        self.btn_cargar_excel.pack(pady=5)
        
        self.btn_cargar_kmz = tk.Button(root, text="Cargar KMZ", command=self.cargar_kmz)
        self.btn_cargar_kmz.pack(pady=5)
        
        self.btn_procesar = tk.Button(root, text="Procesar", command=self.procesar_datos, state=tk.DISABLED)
        self.btn_procesar.pack(pady=5)
        
        self.btn_mapa = tk.Button(root, text="Ver Mapa", command=self.mostrar_mapa, state=tk.DISABLED)
        self.btn_mapa.pack(pady=5)
        
        self.btn_guardar = tk.Button(root, text="Guardar Resultados", command=self.guardar_excel, state=tk.DISABLED)
        self.btn_guardar.pack(pady=5)
        
        self.excel_file = None
        self.kmz_file = None
        self.df = None
        self.gdf = None
        self.mapa = None
    
    def cargar_excel(self):
        self.excel_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if self.excel_file:
            messagebox.showinfo("Carga Exitosa", "Archivo Excel cargado correctamente.")
            if self.kmz_file:
                self.btn_procesar.config(state=tk.NORMAL)
    
    def cargar_kmz(self):
        self.kmz_file = filedialog.askopenfilename(filetypes=[("KMZ files", "*.kmz")])
        if self.kmz_file:
            messagebox.showinfo("Carga Exitosa", "Archivo KMZ cargado correctamente.")
            if self.excel_file:
                self.btn_procesar.config(state=tk.NORMAL)
    
    def procesar_datos(self):
        self.df = pd.read_excel(self.excel_file)
        self.gdf = gpd.read_file(f"/vsizip/{self.kmz_file}")
        self.gdf = self.gdf.to_crs(epsg=4326)
        self.df["geometry"] = self.df.apply(lambda row: Point(row["x"], row["y"]), axis=1)
        df_gdf = gpd.GeoDataFrame(self.df, geometry="geometry", crs="EPSG:4326")
        
        def asignar_nodo(point):
            min_dist = float("inf")
            closest_node = "Fuera de rango"
            
            for _, row in self.gdf.iterrows():
                if row["geometry"].contains(point):
                    return row["Name"]
                
                dist = point.distance(row["geometry"].centroid)
                if dist < min_dist:
                    min_dist = dist
                    closest_node = row["Name"]
            
            return closest_node
        
        self.df["Nodo"] = self.df["geometry"].apply(asignar_nodo)
        
        messagebox.showinfo("Proceso Completo", "Los cuadrantes han sido asignados correctamente.")
        self.btn_guardar.config(state=tk.NORMAL)
        self.btn_mapa.config(state=tk.NORMAL)
    
    def mostrar_mapa(self):
        self.mapa = folium.Map(location=[self.df["y"].mean(), self.df["x"].mean()], zoom_start=12)
        
        for _, row in self.df.iterrows():
            folium.Marker(location=[row["y"], row["x"]], popup=row["Nodo"]).add_to(self.mapa)
        
        map_path = "mapa_nodos.html"
        self.mapa.save(map_path)
        webbrowser.open(map_path)
    
    def guardar_excel(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if save_path:
            self.df.to_excel(save_path, index=False)
            messagebox.showinfo("Guardado Exitoso", "El archivo ha sido guardado correctamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DistritoApp(root)
    root.mainloop()
