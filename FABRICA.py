# -*- coding: utf-8 -*-
import os
import zipfile
import json
import heapq
from math import floor
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime, timedelta
import copy
import math


# ============================================
# CREACION DE LA FUNCION PARA DESCOMPRIMIR EL ARCHIVO CON LAS CONFIGURACIONES NECESARIAS
# ============================================
DATA_DIR = "C:\\Users\\MAT\\Pictures\\PROYECTO_GRAFOS\\data"
CONFIG_ZIP = os.path.join(DATA_DIR, "configurations.zip")
def setup_environment():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if os.path.exists(CONFIG_ZIP):
        with zipfile.ZipFile(CONFIG_ZIP, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)
    else:
        print("No se encontró configurations.zip en ./data/")

# ============================================
# CREACION DE LA CLASE MACHINE O MAQUINA
# ============================================

class Machine:
    #Se crea una clase Maquina con los atributos
    #configurations= contendra un hash de cada uno de los productos que la fabrica produce, cada uno con sus materiales necesarios y su velocidad de produccion
    #config=Sera el producto en especifico para el que servira la maquina, como por ejemplo una tejedora para pantalones
    #production_velocity_rate=Sera la tasa de produccion de la maquina para fabricar el producto
    #depletion_rate= Significa la proporcion del desperdicio, es decir cuanto del material se desperdicia en cada fabricacion de un producto, ya que la maquina no es perfecta
    #min_operators= cantidad minima de operarios que soprta la maquina
    #max_operators= cantidad maxima de operarios que soporta la maquina
    #operators_productivity=una funcion que determina como aumenta la produccion de una maquina, en funcion de los operarios que la operan                                                                                                                                                                             lambda x : 2-abs(x-2) - x**2/16 + x**/5 min = [1,2,3], max = 6
    def __init__(self, Configurations = dict(), config = "", production_velocity_rate = .95, depletion_rate = 0.3, min_operators = 0, max_operators = 3,operators_productivity = lambda x : 2-abs(x-2) - x**2/16 + x**2/5):
        self.Configurations = Configurations
        self.config = config
        self.Configuration = Configurations[config]
        self.production_velocity_rate = production_velocity_rate
        self.depletion_rate = depletion_rate
        self.max_operators = max_operators
        self.min_operators = min_operators
        self.operators_productivity = operators_productivity

    #Se crea un archivo json que contiene los datos o atributos de la clase machine, menos los atributos operators_productivity y Configuration, con la finalidad de guardar el estado de la maquina
    def export_to_json(self, file_name):
        # Exportar el diccionario kwargs a un archivo JSON
        with open(file_name, 'w') as json_file:
            D = dict(vars(self))
            #Se elimina el atributo operators_productivity
            D.pop('operators_productivity')
            #Se elimina el atributo Configuration
            D.pop("Configuration")
            # D['operators_productivity'] = lambda ...
            json.dump(D, json_file, indent=4)


    #Se crea un metodo para obtener la cantidad de productos fabricados
    #Recibiendo como parametros el tiempo para la fabbricacion y una lista con las habilidades de cada operador que operara en la maquina
    def production_by_time(self,time, operators = [ 0.4, 0.8, 0.3 ] ):
        self.Configuration = self.Configurations[self.config]
      #Se verifica que el numero de operarios ingresados que seria igual al tamaño de la lista de habilidades este en el rango, es decir que no sea 0 como tambien que no sea mayor al numero de operarios que soporta la maquina
      #Debido a que asignarle un operario mas que no operara realmente la maquina, es un desperdicion de mano de obra
        if not(self.min_operators <= len(operators) <= self.max_operators):
        #Si no esta en el rango se crea una excepcio y el proceso se detiene
            raise ValueError(f"Operators must be an integer between {self.min_operators} and {self.max_operators} inclusive")
        #Se obtiene la proporcion de material util, restando a 1 la proporcion del desperdicio
        non_depletion = (1-self.depletion_rate)
        objs = dict()
        total_objs = 0
        #Representa la productividad promedio de un operador en la maquina
        average = (self.operators_productivity(len(operators))/len(operators))
        for skill_coefficient in operators:
       #Se calcula cuántos objetos puede producir un operador específico durante el tiempo dado, teniendo en cuenta su coeficiente de habilidad, la velocidad de producción de la máquina, el tiempo de producción, el ajuste de velocidad de producción y la productividad promedio de los operadores
       #Se usa floor porque no se pueden productir 18.3 productos y redondear supone inventarse un nuevo producto, por lo que se redondea al entero inferior
            objs_per_operator = floor(skill_coefficient*self.Configuration["velocity"]["value"] * time * self.production_velocity_rate*average)
            #se crea un nuevo registro en el diccionario objs, emparejando la habilidad de cada operario con la cantidad de productos que produce
            objs[ skill_coefficient ] = objs_per_operator
       #Se suma los objetos producidos por cada operador para tener el total de productos producidos
            total_objs += objs_per_operator
      #Se crea una lista nueva de materiales, que contendra las cantidades necesarias de material requeridas para producir la cantidad de productos anteriormente calculado
        Material = []
      #Se itera sobre cada material especifico
        for x in self.Configuration["materiales"]:
          #Se va añadiendo a la nueva lista de Materiles una dupla que contendra el tipo de material como tambien la cantidad necesaria de material para producir la cantidad de productos en total
          #Se toma en cuenta la proporcion de utilidad de los materiales como tambien la cantidad total de productos y se redondea a tres decimales
            Material.append( (x["type"], round( (x["mount"]/non_depletion)*total_objs, 3) ))
        return (total_objs,objs),Material


#Se crea un metodo para obtener el tiempo necesario para relizar una cierta cantidad de productos
#Recibiendo como parametros la cantidad de productos que se desean fabricar y una lista con las habilidades de cada operador que operara en la maquina
    def production_by_obj(self,obj, operators = [ 0.4, 0.8, 0.3 ] ):
        self.Configuration = self.Configurations[self.config]
        #Se redondea la cantidad de objetos introducida, en caso de que se ingrese 14.2, cosa que no deberia pasar
        obj = floor(obj)
        non_depletion = (1-self.depletion_rate)
        average = self.operators_productivity(len(operators))/len(operators)
        S = 0
        #Se itera sobre las habilidades de cada uno de los empleados
        for skill_coefficient in operators:
        #Se va calculando la cantidad de productos por tiempo de cada ooperador y se van sumando para obtener la cantidad total de productos en una unidad de tiempo
        #Considerando que los operadores estan trabajando de forma simultanea
            S += (self.Configuration["velocity"]["value"] * self.production_velocity_rate * average) * skill_coefficient
        #Se calcula el tiempo total que les lleva a los trabajadores produccir la cantidad de productos ingresada en el metodo
        time = obj/S
        Material = dict()
        for x in self.Configuration["materiales"]:
        #Se calcula la cantidad que se necesita en cada material para la fabricar la cantidad de productos ingresada
            Material[x["type"]] =  round( (x["mount"]/non_depletion)*obj, 3)
        #Se retorn el tiempo de produccion con dos decimales
        return time,Material


# ============================================
# CREACION DE LA CLASE GRAFO CON LOS METODOS Y ALGORITMOS NECESARIOS
# ============================================

class Grafo:
    def __init__(self):
        self.vertices = set()
        self.aristas = {}
        self.conexiones = {}

    def añadir_nodo(self, SectorName):
        self.vertices.add(SectorName)

    def añadir_arista(self, sector1, sector2, peso):
        dupla = (sector1, sector2)
        self.aristas[dupla] = peso
        if sector1 in self.conexiones:
            self.conexiones[sector1].append(sector2)
        else:
            self.conexiones[sector1] = [sector2]
        if sector2 not in self.conexiones:
            self.conexiones[sector2] = []

    def añadir_aristaNoDirigida(self, sector1, sector2, peso):
        dupla = (sector1, sector2)
        self.aristas[dupla] = peso
        if sector1 in self.conexiones:
            self.conexiones[sector1].append(sector2)
            if sector2 in self.conexiones:
              self.conexiones[sector2].append(sector1)
        else:
            self.conexiones[sector1] = [sector2]
            if sector2 not in self.conexiones:
                self.conexiones[sector2] = [sector1]
            else:
                self.conexiones[sector2].append(sector1)

    def BFS(self, s, t, parent):
        visited = set()
        queue = []

        queue.append(s)
        visited.add(s)

        while queue:
            u = queue.pop(0)
            for v in self.conexiones[u]:
                if v not in visited and self.aristas[(u, v)] > 0:
                    queue.append(v)
                    parent[v] = u
                    visited.add(v)
                    if v == t:
                        return True
        return False

    def FordFulkerson(self, fuente, sumidero):
      padre = {}
      flujo_maximo = 0
      cuellos_de_botella = {}

      while self.BFS(fuente, sumidero, padre):
          flujo_camino = float("inf")
          nodo = sumidero
          while nodo != fuente:
              flujo_camino = min(flujo_camino, self.aristas[(padre[nodo], nodo)])
              nodo = padre[nodo]

          flujo_maximo += flujo_camino

          nodo = sumidero
          while nodo != fuente:
              anterior = padre[nodo]
              self.aristas[(anterior, nodo)] -= flujo_camino

              if (anterior, nodo) in cuellos_de_botella:
                  cuellos_de_botella[(anterior, nodo)] += flujo_camino
              else:
                  cuellos_de_botella[(anterior, nodo)] = flujo_camino

              nodo = padre[nodo]

      cantidad_productos = {}
      for (origen, destino), flujo in cuellos_de_botella.items():
          if origen == fuente:
              if destino in cantidad_productos:
                  cantidad_productos[destino] += flujo
              else:
                  cantidad_productos[destino] = flujo

      grafo_residual = Grafo()
      for vertice in self.vertices:
          grafo_residual.añadir_nodo(vertice)
      for (origen, destino), peso in self.aristas.items():
          grafo_residual.añadir_arista(origen, destino, peso)

      alcanzables, aristas_corte = self.min_cut(fuente)

      return flujo_maximo, cantidad_productos, grafo_residual, aristas_corte


    def min_cut(self, fuente):
      visitados = set()
      self.dfs(fuente, visitados)

      aristas_corte = []
      for u in visitados:
          for v in self.conexiones[u]:
               if v not in visitados and (u, v) in self.aristas:
                  aristas_corte.append((u, v, self.aristas[u, v]))

      return visitados, aristas_corte

    def dfs(self, nodo, visitados):
        visitados.add(nodo)
        for vecino in self.conexiones[nodo]:
            if vecino not in visitados and self.aristas[(nodo, vecino)] > 0:
                self.dfs(vecino, visitados)

    # Método para encontrar el conjunto al que pertenece un elemento

    def find(self, padres, i):
      if padres[i] == i:
          return i
      return self.find(padres, padres[i])

    # Método para unir dos conjuntos
    def union(self, padres, rango, x, y):
        raiz_x = self.find(padres, x)
        raiz_y = self.find(padres, y)

        if rango[raiz_x] < rango[raiz_y]:
            padres[raiz_x] = raiz_y
        elif rango[raiz_x] > rango[raiz_y]:
            padres[raiz_y] = raiz_x
        else:
            padres[raiz_y] = raiz_x
            rango[raiz_x] += 1

    # Método de Kruskal para encontrar el árbol de expansión mínimo
    def prim(self):
        result = []  # Esto almacenará el árbol de expansión mínimo

        # Ordena todas las aristas en orden no decreciente de su peso
        aristas_ordenadas = sorted(self.aristas.items(), key=lambda item: item[1])

        parent = {}
        rank = {}

        # Crea subconjuntos con un solo elemento
        for vertice in self.vertices:
            parent[vertice] = vertice
            rank[vertice] = 0

        # Número de aristas que necesitamos en el árbol de expansión mínimo
        e = 0
        i = 0

        while e < len(self.vertices) - 1:
            sector1, sector2 = aristas_ordenadas[i][0]
            peso = aristas_ordenadas[i][1]
            i = i + 1

            x = self.find(parent, sector1)
            y = self.find(parent, sector2)

            # Si no forma un ciclo, incluirlo en el resultado y unir los dos subconjuntos
            if x != y:
                e = e + 1
                result.append((sector1, sector2, peso))
                self.union(parent, rank, x, y)

        # Construye el grafo del árbol de expansión mínimo
        grafo_minimo = Grafo()
        for vertice in self.vertices:
            grafo_minimo.añadir_nodo(vertice)
        for sector1, sector2, peso in result:
            grafo_minimo.añadir_arista(sector1, sector2, peso)

        return grafo_minimo


# ============================================
# CREACION DE LA CLASE FABRICA
# ============================================

class Fabrica:

    def __init__(self,horaTrabajoDiario):
        self.TrabajoDiario=horaTrabajoDiario
    #Se crea un metodo para subir el archivo jason de machines.json, el cual contiene los tipos de maquinas de la fabrica anexado cada tipo a una lista de archivos json, los cuales contienen las configuraciones de cada maquina perteneciente a ese tipo de maquina
    #Por ejemplo:
    #"corte": [
    #    "corte_001.json",
    #    "corte_002.json",
    #    "corte_003.json",
    #    "corte_004.json",
    #   "corte_005.json"
    #]


    def load_machines_from_json(self, file_name):
        self.Machines = dict()
        with open(file_name, "r") as f:
            D = json.load(f)
  #Se itera sobre cada tipo de maquina en el jason machines.jason
            for x in D:
              #Se le añade una nueva seccion al diccionario Machines, el cual hasheara el tipo de maquina con una lista que cntendra listas con el nombre de cada maquina y la maquina creada con su configuracion
                self.Machines[x] = []
              #Se obtiene el nombre de cada archivo jason en el tipo de maquina especifico, ya que cada archivo contiene las configuraciones especificas
                for fileM in D[x]:
                  #Se lee el archivo jason con el nombre obtenido en fileM
                    with open(fileM, "r") as g:
                      #Se descomprime el archivo, el cual contiene las configuraciones especificas y se crea con esas configuraciones un objeto del tipo Maquina
                        u = json.load(g)
                        # u.pop("Configuration")
                        M = Machine(**u)
                      #Se añade a Machines el nombre del archivo jason que contiene esas configuraciones y la maquina creada con esas configuraciones
                        self.Machines[x].append( [fileM,M] )

    #Se crea un metodo para exportar la información de las máquinas contenida en la instancia de una clase a un archivo JSON
    def export_machines_to_json(self, file_name, prefix=""):
      #verifica si la instancia tiene datos en el atributo Machines
        if not self.Machines:
          #Si Machines está vacío o no tiene datos, lanza una excepción
            raise Exception("No machines data to export. Load machines data first.")
        #En caso de que haya informacion, se crea un diccionario vacio
        machines_data = {}
        #Se itera sobre el nombre de cada maquina como corte y mediante esta tambien se guarda la lista con el nombre de las maquinas
        for machine_name, machine_list in self.Machines.items():
            machines_data[machine_name] = [ prefix + file_path for file_path, _ in machine_list]
        #Se escribe el diccionario con la informacion de las maquinas
        with open(file_name, "w") as f:
            json.dump(machines_data, f)

     #Se crea un metodo para exportar la información de las instancias de las máquinas en un archivo JSON
    def export_machine_instances_to_json(self, prefix):
      #verifica si la instancia tiene datos en el atributo Machines
        if not self.Machines:
          #En caso de no tenerla, se lanza una excepcion
            raise Exception("No machines data to export. Load machines data first.")
        #Caso contrario, sigue con el proceso y se itera sobre cada tipo de maquina con su lista de maquinas hasheada
        for machine_name, machine_list in self.Machines.items():
          #Se accede de la lista de maquinas que es una dupla
            for file_name, instance_machine in machine_list:
                #Se llama en cada instancia al metodo export_to_jason, para almacenar en archivo jason la informacion de cada maquina, enviandole como nombre del archivo el file_name extraido de la dupla
                instance_machine.export_to_json( prefix+"_"+file_name)



    #Se crea un metodo para cargar la traza de un archivo jason, es decir por cuales maquinas o secciones pasara el producto
    #Por Ejemplo:
    #{"camisa": [
    #    {
    #        "machine": "corte",
    #        "configuration": "corte de tela para camisa"
    #    },
    #    {
    #        "machine": "recta",
    #        "configuration": "costura de camisa"
    #    },
    #    {
    #        "machine": "overlock",
    #        "configuration": "acabado de camisa"
    #    }]}
    def load_trace_from_json(self, file_name ):
        with open(file_name, "r") as f:
    #Trace sera el diccionario que contendra las trazas de los productos
    #Cada seccion sera el nombre del producto hashedo con una lista que contiene otros diccionarios internos, en el que cada diccionario interno representara una etapa de la fabricacion del producto
    #Cada diccionario interno contendra el nombre de la maquina por la que pasara el producto y la configuracion de cada uno
            self.Trace = json.load(f)


  #Se crea un metodo para exportar a un archivo jason, la traza del producto, es decir porque maquinas debe pasar para fabricarlo
    def export_trace_to_json(self, file_name):
        with open(file_name, "w") as f:
            json.dump(self.Trace, f)

   #Se crea un metodo para retornar los materiales que seran usados en la fabricacion de todos los productos
    def materials(self):
        self.Materiales = set()
        #Se itera sobre cada clave o tipo de maquina del diccionario Machines
        for y in self.Machines:
          #Se accede al diccionario Machines en el tipo de maquina determinado por y, se accede a la primera lista de la lista de maquinas establecidas en ese tipo de maquinas
          #Finalmente una vez accedido se guarda esa maquina instanciada en la variable Machine
            Machine = self.Machines[y][0][1]
            #Se itera sobre las configuraciones de la variable Machine, debido a que cada maquina posee una configuracion disinta, dependiendo del producto que se quiera fabricar
            for x in Machine.Configurations:
              #Se accede a la lista de materiales de cada configuracion
                for material in Machine.Configurations[x]['materiales']:
                  #Se crea un conjunto que contiene el material usado, accediendo con la clave type y se realiza una union de conjuntos con el Materiales
                    self.Materiales |= {material['type']}
        return self.Materiales



  #Se crea un metodo para exportar a archivo jason, los materiales que se utilizaran en general para realizar la fabricacion del producto
    def export_materials_to_json(self, file_name):
      #Se verifica si la instancia tiene datos en el atributo Materiales
        if self.Materiales is None:
            # En caso de no tenerlos, se los calcula automaticamente mediante el metodo materials()
            self.materials()
        # Finalmnete se exporta los datos del atributo a un archivo jason
        with open(file_name, "w") as f:
            json.dump(list(self.Materiales), f)


    #Se crea un metodo para almacenar los precios de cada material usado
    def load_raw_material_cost_from_json( self, file_name ):
        with open(file_name, "r") as f:
          #Se carga los precios de cada material del documento prices.json
            self.Prices = json.load(f)
          #Se verifica que el archivo jason no contenga los precios de todos los materiales
            if not self.materials().issubset(set(self.Prices.keys())):
              #En caso de que no los contenga a todos, se establece al atributo Prices como nulo
                self.Prices = None
              #Se genera una excepcion diciendo que la lista de precios no contiene a todos los materiales que se van a utilizar
                raise Exception("Lista de precios incompleta, faltan materiales")

  #Se crea un metodo para exportar a archivo jason los costos individuales de los materiales que se utilizaran
    def export_material_costs_to_json(self, file_name):
      #Se veridica si la instancia tiene datos en el atributo Prices
        if self.Prices is None:
          #En caso de no tener datos en el atributo, se lanza una excepcion
            raise Exception("Material costs have not been loaded. Call load_and_validate_material_costs_from_json first.")
        # En caso de tener datos, se los guarda en un archivo jason, con el nombre de archivo que se le pasa por parametro
        with open(file_name, "w") as f:
            json.dump(self.Prices, f)




    #Se crea un metodo para calcular el costo total de cada material, teniendo en cuenta el monto que se utilizara de cada material
    def cost( self, file_name = None ):
      #Se verifica que no se haya enviado con archivo jason con la informacion ya contenida
        if(file_name == None):
            self.Costs = dict()
        #Se itera sobre el nombre de cada producto en Trace
            for product in self.Trace:
                s = 0
            #Se itera sobre cada diccionario que contiene machine y configuracion
                for config in self.Trace[product]:
              #Se accede al diccionario Machines y se cambia la por una nueva configuracion
                    self.Machines[ config["machine"] ][0][1].config = config["configuration"]
                #Se obtiene llama al metodo production_by_obj(1) el cual devuelve el tiempo invertido en la produccion de un objeto y la acantidad de material inevrtido en total, por lo que se accede a la posicion 1
                #Los materiales devueltos son un diccionario, el cual se guarda en u
                #El diccionario hashea el nombre del material con su cantidad usada
                    u = self.Machines[ config["machine"] ][0][1].production_by_obj(1)[1]
                #Se itera sobre cada material en la lista
                    for material in u:
                  #Se multiplica el precio del material obtenido de self.Prices con la cantidad usada del material, accediendo en u mediante la llave material
                        s += self.Prices[material]*u[material]
            #Se crea una seccion en el diccionario Costs, donde este el nombre del producto y cuando se gasto en total
                self.Costs[product] = round(s,2)
            return self.Costs
        else:
          #En caso de que el archivo contenga los costos, siemplemenete se lo lee
            with open(file_name, "r") as f:
              #Se guarda la informacion como un atributo de la clase
                self.Costs = json.load(f)




    #Se crea un metodo para guardar los datos de Costs en un archovo Json, el cual contiene el gasto total invertido en cada producto
    def export_cost_to_json(self, file_name):
      #Se verifica si la instancia tiene datos en este atributo
        if self.Costs is None:
            # En caso de no tener datos, se los calcula llamando al metodo cost()
            self.cost()
        # Finalmente se guada los datos del atributo Costs en un archivo jason, con el nombre que se le paso por parametro
        with open(file_name, "w") as f:
            json.dump(self.Costs, f)




     #Se crea un metodo que carga los precios de venta de cada producto de un archivo JSON
    def load_sell_prices_from_json(self, file_name):
        with open(file_name, "r") as f:
          #Se carga el precio de venta de cada producto del archivo sell_prices.json
            self.Sell_Prices = json.load(f)
          #Se verifica si Sell_Prices no contiene todos los productos fabricados en Costs
            if not set( self.Costs.keys() ).issubset( set(self.Sell_Prices.keys()) ):
              #Se imrpime que productos faltan
                print( list(set( self.Costs.keys() ) - set(self.Sell_Prices.keys())) )
              #Se lanza una excepcion
                raise Exception( "Se requieren los precios de venta de todos los articulos" )
            return self.Sell_Prices


    def leer_red_Secciones_Fabrica_json(self,file_path):
        # Leer el archivo JSON
        with open(file_path, 'r') as file:
            data = json.load(file)
        self.red_Tiempo_Secciones=data


  #Se crea un metodo para exportar los precios de venta de los productos
    def export_sell_prices_to_json(self, file_name):
      #Se verifica si la instancia tiene datos en el atributo Sell_Prices
        if self.Sell_Prices is None:
          #En caso de no tenerlos, se lanza una excepcion
            raise Exception("Sell prices have not been loaded. Call load_and_validate_sell_prices_from_json first.")
        # Se exporta el diccionario Sell_Prices a un archivo JSON
        with open(file_name, "w") as f:
            json.dump(self.Sell_Prices, f)


    #Se crea un metodo para obtener las ganacias obtenidas
    def profit(self, file_name=None):
        if file_name is None:
            # Calculate profit if file_name is not provided
            D = self.cost()
            U = self.Sell_Prices
            G = {}
        #Se resta de cada material, su precio de venta menos el monto invertido en su fabricacion
            for x in D:
          #Se crea una nueva seccion en G que hashee el nombre del producto y su ganancia
                G[x] = round(U[x] - D[x], 2)
            self.Profit = G
            return G
        else:
            # Cargar ganancias de un archivo JSON si se proporciona nombre_archivo
            with open(file_name, "r") as f:
                self.Profit = json.load(f)

  #Se crea un metodo para exportar las ganacias totales de cada producto, teniendo en cuenta lo invertido en el producto y su precio de venta
    def export_profit_to_json(self, file_name):
      #Se verifica si la instancia tiene datos en el atributo Profit
        if self.Profit is None:
            # En caso de no tener datos, se los calcula llamando a la funcion profit()
            self.profit()
        # Se exporta los datos de las ganacias a un jason
        with open(file_name, "w") as f:
            json.dump(self.Profit, f)

    #Se crea un metodo para asignar óptimamente operadores a máquinas dados ciertos criterios de optimización como la funcion de produccion o el atributo operators_productivity
    def assign_operators_optimizer( self, operators, machines ):
        X = [ (Machi.min_operators, Machi.max_operators) for name,Machi in machines ]
        M = machines[0][1].max_operators
        if not (sum([x for x, y in X]) <= len(operators) <= sum([y for x, y in X])):
            raise Exception("Incorrect number of operators, either exceeding or falling short of required amount")
        if not all( Max == M for Min,Max in X ):
            raise Exception(f"All machines must have the same max_operators variable {M}\n")
        if not all( 1<=Min<Max for Min,Max in X ):
            raise Exception(f"All max and min operators variables must satisfy 1 <= min < max")
        m = [ machine[1].min_operators for machine in machines ]
        D = {}
        k = len(machines)
        while machines:
            # b = tuple(machines.pop())
            u = machines.pop()
            b = u[0]
            f = u[1].operators_productivity
            D[b] = []
            j = 0
            argmax = m[ k - len(D) ]
            funmax = f(argmax)
            while j<M and sum(m[ : k-len(D) ]) < len(operators):
                o = operators.pop()
                D[b].append(o)
                q = len(D[b])

                if m[ k - len(D) ] < q:
                    if funmax < f(q):
                        funmax = f(q)
                        argmax = q
                j += 1
            while argmax < len(D[b]):
                operators.append( D[b].pop() )
        return D,tuple(operators)



    #Se crea un metodo que se se encarga de cargar datos de un archivo JSON que contiene listas de operadores para cada máquina
    #Luego optimiza la asignación de operadores a las máquinas y finalmente exporta la configuración óptima resultante a archivos JSON individuales
    def machines_optimizer_from_json(self, file_name ):
        with open(file_name, "r") as f:
            self.operators_lists = json.load(f)
            self.OPTIMAL_MACHINES = {}
            for machine_name in self.operators_lists:
                operators = sorted(self.operators_lists[machine_name])
                machines = sorted(self.Machines[ machine_name ], key = lambda x:x[1].production_by_obj(1,[1 for i in range(x[1].max_operators)])[0], reverse = True )
                n = len(machines)
                rank = { machines[i][0]:n-i for i in range(n) }
                # for x,y in machines:
                #    y.min_operators = randint(1,3)
                #    y.max_operators = 6
                try:
                    print(f"Type machine: {machine_name}")
                    D, inutils = self.assign_operators_optimizer(operators, machines)
                    for x in D:
                        #name, inst_machine = x
                        #print(f"\t\tMachine: {name[:-5]}, min_operators: {inst_machine.min_operators}, optimal solution: {D[x]}")
                        print(f"\t\tMachine: {x[:-5]}, optimal solution: {D[x]}")
                    if inutils:
                        print(f"\tUnnecessary employees: {inutils}\n")
                    else:
                        print()
                    self.OPTIMAL_MACHINES[machine_name] = [ { "name":name, "instance":instance, "operators": D[name], "rank":rank[name] } for name, instance in self.Machines[ machine_name ] ]
                    # Exportar D e inutils a archivos JSON
                    self.export_optimal_configuration_to_json(D, inutils, machine_name )

                except Exception as e:
                    print(f"Error procesando {machine_name}: {e}")
        self.CopiaOPTIMAL_MACHINES=copy.deepcopy(self.OPTIMAL_MACHINES)

    #Se crea un metodo para exportar la distriucion eficiente de los operadores en las maquinas
    def export_optimal_configuration_to_json(self, D, inutils, machine_name):
        # Construir el diccionario para exportar
        data_to_export = {
            "optimal": D,
            "inutils": inutils
        }
        # Construir el nombre de archivo
        file_name = f"{machine_name}_optimal_configuration.json"
        # Exportar a JSON
        with open(file_name, "w") as f:
            json.dump(data_to_export, f)

    #Se crea un metodo para exportar la lista de operadores en las máquinas a un archivo JSON
    def export_operators_to_json(self, file_name):
      #Se verifica si la instancia tiene datos en el tributo operators_lists
        if self.operators_lists is None:
          #En caso de que no tenga datos en el atributo, se lanza una excepcion
            raise Exception("No operators lists to export. Call load_operators_lists_from_json first.")
        #En caso de que si tenga datos, se los guarda en un archivo json
        with open(file_name, "w") as f:
            json.dump(self.operators_lists, f)


    #Se crea un metodo para exportar todo los datos, llamando a todos los metodos de exportar anteriores, mediante este metodo como intermediario, al cual se le pasa con que prefijo se guardaran los archivos json
    def export_to_json(self, export_file_prefix ):
        # Export machines data
        self.export_machines_to_json(f"{export_file_prefix}_machines.json", export_file_prefix + "_")

        self.export_machine_instances_to_json(export_file_prefix)

        # Export trace data
        self.export_trace_to_json(f"{export_file_prefix}_trace.json")

        # Export materials data
        self.export_materials_to_json(f"{export_file_prefix}_materials.json")

        # Export material costs data
        self.export_material_costs_to_json(f"{export_file_prefix}_material_costs.json")

        # Export cost data
        self.export_cost_to_json(f"{export_file_prefix}_cost.json")

        # Export sell prices data
        self.export_sell_prices_to_json(f"{export_file_prefix}_sell_prices.json")

        # Export profit data
        self.export_profit_to_json(f"{export_file_prefix}_profit.json")

        # Export operators lists data
        self.export_operators_to_json(f"{export_file_prefix}_operators.json")


    #Se crea un metodo que calcula la producción de objetos para un tipo de maquina como corte, dada su configuración, y la cantidad de objetos que se desea producir.
    #Teniendo en cuenta que varias maquinas de ese tipo de maquinas trabajaran de forma simultanea o al mismo tiempo
    def production_by_object(self, maquina, config, amount, filter=None ):
        priority_queue = []

        if filter == None:
            G = self.OPTIMAL_MACHINES[maquina]
        else:
            G = [ Machine for Machine in self.OPTIMAL_MACHINES[maquina] if Machine["rank"] in filter ]

        for D in G:
            D["instance"].config = config
            single_time = D["instance"].production_by_obj(1,D["operators"])[0]
            if not (single_time):
                print( "produce cero: ",D["rank"] )
                print("*"*30)
            heapq.heappush(priority_queue, (single_time,[single_time,D["rank"],0]))
        for i in range(amount):
            X = heapq.heappop(priority_queue)
            heapq.heappush( priority_queue, ( X[1][0] * (X[1][2]+1), [X[1][0],X[1][1],X[1][2]+1] ) )
        D = { X[1][1]:{ "objects":X[1][2], "time":X[1][2]*X[1][0] } for X in priority_queue }
        return D

    # Filter is a set of RANKS
    def production_by_time( self, maquina, config, time, filter=None ):
        Total = 0
        U = dict()

        if filter == None:
            G = self.OPTIMAL_MACHINES[maquina]
        else:
            G = [ Machine for Machine in self.OPTIMAL_MACHINES[maquina] if Machine["rank"] in filter ]

        for D in G:
            D["instance"].config = config
            (total, u), _ = D["instance"].production_by_time( time, D["operators"])
            Total += total
            U[ D["rank"] ] = (total,u)
        return Total,U

    def cantidadProductosDiaria(self):
      self.bandera=False
      self.contador=1
      self.auxiliarPrincipal()
      print("Antes de la optimizacion")
      print("Configuraciones de maquinas")
      for i in self.CopiaOPTIMAL_MACHINES:
        for p in self.CopiaOPTIMAL_MACHINES[i]:
          instancia=p["instance"]
          nombre=p["name"]
          print(nombre)
          print(instancia.Configurations)
      print("Maquinas con empleados")
      print(self.CopiaOPTIMAL_MACHINES)
      print("Flujo maximo obtenido")
      print(self.flujoMaximo)
      print("Grafo Residual")
      print(self.grafoResidual.aristas)
      self.contador=2
      while(self.bandera==False):
       self.auxiliarOptimizador()
      self.auxiliarPrincipal()
      print("Despues de la optimizacion")
      print("Configuraciones de maquinas")
      for i in self.OPTIMAL_MACHINES:
              for p in self.OPTIMAL_MACHINES[i]:
                instancia=p["instance"]
                nombre=p["name"]
                print(nombre)
                print(instancia.Configurations)
      print("Maquinas con empleados")
      print(self.OPTIMAL_MACHINES)
      print("Flujo maximo obtenido")
      print(self.flujoMaximo)
      print("Grafo Residual")
      print(self.grafoResidual.aristas)

    def auxiliarPrincipal(self):
        self.GrafoProduccion = Grafo()
        self.GrafoProduccion.añadir_nodo("T")
        self.GrafoProduccion.añadir_nodo("S")
        maximos = {}
        for producto, secciones in self.Trace.items():
            seccionAnterior = None
            seccionActual = None
            max = 0
            for indice, seccion in enumerate(secciones):
                self.GrafoProduccion.añadir_nodo(seccion['configuration'])

                if indice == 0:
                    seccionActual = seccion['configuration']
                    tipoMaquinaSeccionActual = seccion['machine']
                    pesoArista, diccionario = self.production_by_time(tipoMaquinaSeccionActual, seccionActual, self.TrabajoDiario)
                    self.GrafoProduccion.añadir_arista("S", seccionActual, pesoArista)
                else:
                    seccionAnterior = seccionActual
                    seccionActual = seccion['configuration']
                    tipoMaquinaSeccionActual = seccion['machine']
                    configuracionSeccion = seccion['configuration']
                    pesoArista, diccionario = self.production_by_time(tipoMaquinaSeccionActual, configuracionSeccion, self.TrabajoDiario)
                    self.GrafoProduccion.añadir_arista(seccionAnterior, seccionActual, pesoArista)
                if max < pesoArista:
                    max = pesoArista
            self.GrafoProduccion.añadir_arista(seccionActual, "T", float('inf'))
            maximos[producto] = max
            copiaGrafoProduccion = copy.deepcopy(self.GrafoProduccion)
        self.flujoMaximo, cantidadProductos, self.grafoResidual, aristasCortas = copiaGrafoProduccion.FordFulkerson("S", "T")

    def auxiliarOptimizador(self):
       banderaAuxiliar=False
       banderaAuxiliar2=False
       for u,v in self.grafoResidual.aristas:
        if(self.grafoResidual.aristas[u,v]>4 and not(self.grafoResidual.aristas[u,v]==float('inf'))):
          seccion=v
          for i in self.Trace:
            for p in self.Trace[i]:
              if(p["configuration"]==seccion):
                zonaGeneral=p["machine"]
          for registro in self.OPTIMAL_MACHINES[zonaGeneral]:
            if registro["instance"].min_operators<len(registro["operators"]):
              registro["operators"].pop()
              banderaAuxiliar=True
              banderaAuxiliar2=True
              break
          if(banderaAuxiliar==False):
                for i in self.Trace:
                  for p in self.Trace[i]:
                    if(p["configuration"]==seccion):
                      zonaGeneral=p["machine"]
                      banderaAuxiliar=False
                for registro in self.OPTIMAL_MACHINES[zonaGeneral]:
                  registro["instance"].config=seccion
                  registro["instance"].Configuration = registro["instance"].Configurations[registro["instance"].config]
                  if registro["instance"].Configuration["velocity"]["value"]>0.5:
                     registro["instance"].Configuration["velocity"]["value"]=registro["instance"].Configuration["velocity"]["value"]-0.5
                     banderaAuxiliar2=True
                     break
          if(banderaAuxiliar2==False):
              for i in self.Trace:
                  for p in self.Trace[i]:
                    if(p["configuration"]==seccion):
                      zonaGeneral=p["machine"]
                      banderaAuxiliar=False
              for registro in self.OPTIMAL_MACHINES[zonaGeneral]:
                if(len(registro)>4):
                  registro.pop()
                  break
          self.auxiliarPrincipal()
        self.bandera=True
        for u,v in self.grafoResidual.aristas:
          if (self.grafoResidual.aristas[u,v]>4 and not(self.grafoResidual.aristas[u,v]==float('inf'))):
              self.bandera=False



    def crearGrafoMinimoTransporte(self):
      self.GrafoTransporte=Grafo()
      for i in self.red_Tiempo_Secciones:
        self.GrafoTransporte.añadir_nodo(i)
        for llave, valor in self.red_Tiempo_Secciones[i].items():
          self.GrafoTransporte.añadir_aristaNoDirigida(i,llave,valor)
      self.Grafo_Red_Transporte_Minimo=self.GrafoTransporte.prim()
      return self.Grafo_Red_Transporte_Minimo

    def produccionProductosPorTiempo(self,fecha1, fecha2, cantidadFeriados=0):
      fecha1_obj = datetime.strptime(fecha1, '%Y-%m-%d')
      fecha2_obj = datetime.strptime(fecha2, '%Y-%m-%d')
      dias = 0
      while fecha1_obj < fecha2_obj:
          if fecha1_obj.weekday() != 6:
              dias += 1
          fecha1_obj += timedelta(days=1)
      if(dias-cantidadFeriados>0):
        dias=dias-cantidadFeriados
      else:
        raise Exception("Holidays are longer or cover the entire period of time, so the company presents 0 manufactured products.")

      produccionTotal=dias*self.flujoMaximo
      print(f"La cantidad maxima de productos producido en el lapso de tiempo es: {produccionTotal}")



if __name__=="__main__":
    # ============================================
    # CARGANDO CONFIGURACION INICIAL DE ARCHIVO
    # ============================================
    setup_environment()

    # ============================================
    # EJECUCION DE PRUEBA DEL FLUJO DE PRODUCTIVIDAD DE UNA FABRICA, ESTABLECIENDO LAS CONDICIONES NECESARIAS COMO HORARIOS, CAPACIDAD, ETC
    # ============================================
    maquila = Fabrica(7) #Estableciendo que la fabrica trabaja 7 horas diarias
    maquila.load_machines_from_json(os.path.join(DATA_DIR, "prueba_1_machines.json"))
    maquila.load_trace_from_json(os.path.join(DATA_DIR, "prueba_1_trace.json"))
    maquila.load_raw_material_cost_from_json(os.path.join(DATA_DIR, "prueba_1_material_costs.json"))
    maquila.leer_red_Secciones_Fabrica_json(os.path.join(DATA_DIR, "redTransporteSecciones.json"))
    maquila.machines_optimizer_from_json(os.path.join(DATA_DIR, 'prueba_1_operators.json'))
    maquila.Trace
    maquila.materials()
    maquila.cost()
    maquila.load_sell_prices_from_json("prueba_1_sell_prices.json")
    maquila.profit()
    maquila.production_by_time("corte","corte de tela para camisa",4)
    maquila.production_by_object("corte","corte de tela para camisa",31)
    maquila.machines_optimizer_from_json('prueba_1_operators.json')
    maquila.OPTIMAL_MACHINES
    """Fijarse los empleados en la seccion de Recta para ver la variacion"""
    maquila.cantidadProductosDiaria()
    maquila.crearGrafoMinimoTransporte()
    print("vertices:")
    print(maquila.Grafo_Red_Transporte_Minimo.vertices)
    print("aristas:")
    print(maquila.Grafo_Red_Transporte_Minimo.aristas)
    print("conexiones:")
    print(maquila.Grafo_Red_Transporte_Minimo.conexiones)

    # ============================================
    # GRAFICA DE LA RED DE TRANSPORTE ORIGINAL
    # ============================================
    G = nx.Graph()
    for vertice in maquila.GrafoTransporte.vertices:
        G.add_node(vertice)
    for (v1, v2), peso in maquila.GrafoTransporte.aristas.items():
        G.add_edge(v1, v2, weight=peso)
    pos = nx.spring_layout(G)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color='skyblue')  #
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title('Red de Transporte Original')
    plt.show()


    # ============================================
    # GRAFICA DE LA RED DE TRANSPORTE MINIMA
    # ============================================
    G = nx.Graph()
    for vertice in maquila.Grafo_Red_Transporte_Minimo.vertices:
        G.add_node(vertice)
    for (v1, v2), peso in maquila.Grafo_Red_Transporte_Minimo.aristas.items():
        G.add_edge(v1, v2, weight=peso)
    pos = nx.spring_layout(G)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color='skyblue')  #
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title('Red de Transporte Mínimo')
    plt.show()
    maquila.produccionProductosPorTiempo("2024-05-01","2024-06-01",0)