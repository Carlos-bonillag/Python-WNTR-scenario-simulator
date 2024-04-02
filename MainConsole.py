#Importo las librerias
import os
import wntr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random as rd
from tkinter import Tk, filedialog, messagebox
import itertools

# Configurar el filtro para ignorar los UserWarnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="wntr.epanet.io")

###################################################################################
#Funcion para imprimir presiones y caudales sin ninguna modificación

#Funcion cuando se presentan medidores de presión o caudal
def Medidor_presion_o_caudal(wnx,vec,tipo):
    #simulo la red    
    sim = wntr.sim.EpanetSimulator(wnx)
    results = sim.run_sim()
    #extraigo los datos de presion de los nodos
    if tipo == 'presion':
        npresion = len(vec)
        #nmp = [0]*npresion
        presion = results.node['pressure'] 
        df_presiones = pd.DataFrame()
        for i in range(0,npresion,1):
            #nmp[i] = presion.loc[:,vec[i]]
            df_presiones[vec[i]] = presion.loc[:,vec[i]]
        df_presiones.index  /= 3600 #TIEMPO A HORAS
        
        #GENERAMOS EL EXCEL
        with pd.ExcelWriter("Resultados_presiones.xlsx") as writer:
            df_presiones.to_excel(writer,sheet_name='Presiones', index_label='Tiempo')
        print("########_ESCENARIO SIN VARIACIONES EN LA RED_##########")
        print("Archivo Excel  generado exitosamente.")
        
    if tipo == 'caudal':
        ncaudal = len(vec)
        #nmq = [0]*ncaudal
        flow = results.link['flowrate']*1000
        df_caudales = pd.DataFrame()
        for y in range(0,ncaudal,1):
            #nmq[y] = flow.loc[:,vec[y]]
            df_caudales[vec[y]] = flow.loc[:,vec[y]]
        df_caudales.index  /= 3600 #TIEMPO A HORAS
        #GENERAMOS EL EXEL
        with pd.ExcelWriter("Resultados_caudales.xlsx") as writer:
            df_caudales.to_excel(writer, sheet_name='Caudales', index_label='Tiempo')
        print("########_ESCENARIO SIN VARIACIONES EN LA RED_##########")
        print("Archivo Excel  generado exitosamente.")

#Funcion cuando se presentan medidores de presión y caudal
def Medidor_presion_y_caudal(wnx,vecq,vecp):
    #simulo la red
    sim = wntr.sim.EpanetSimulator(wnx)
    results = sim.run_sim()
    npresion = len(vecp)
    ncaudal = len(vecq)
    flow = results.link['flowrate']*1000
    presion = results.node['pressure'] 
    #pandas to exel
    df_pres = pd.DataFrame()
    df_cau = pd.DataFrame()
    #print("PRESIONES")
    for i in range(0,npresion,1):
        df_pres[vecp[i]] = presion.loc[:,vecp[i]]
    df_pres.index  /= 3600 #TIEMPO A HORAS
    #print("caudales")
    for y in range(0,ncaudal,1):
        #nmq[y] = flow.loc[:,vecq[y]]
        df_cau[vecq[y]] = flow.loc[:,vecq[y]]
    df_cau.index  /= 3600 #TIEMPO A HORAS
    
    print("########_ESCENARIO SIN VARIACIONES EN LA RED_##########")
    # Guardar los datos en un archivo Excel
    with pd.ExcelWriter("Resultados_presiones_caudales.xlsx") as writer:
        df_pres.to_excel(writer, sheet_name="Presiones", index_label='Tiempo')
        df_cau.to_excel(writer, sheet_name="Caudales", index_label='Tiempo') 
    print("Archivo Excel generado exitosamente.")

# def Duracionfugas(numerodefugas):
#     listaduracion =[]
#     for n in numerodefugas:
#         listaduracion.append(24)
#     print(n, listaduracion)
#     return listaduracion


###################################################################################
#Funcion para incluir Fugas e imprimir presiones y caudales

#Función con fugas en la red
def Medidor_fugas_presion_o_caudal(wnx,vecq,ntipo,nfugas,ce,nhf_inicial, nhf_final):
    
    #Extraigo los valores de caudal o presión antes de asignar la fuga
    if ntipo == 'presion' :
        print("solo medidor de presiones")
        Medidor_presion_o_caudal(wnx, vecq, 'presion')
    # llamo la funcion de caudal
    if ntipo == 'caudal':
        print("solo medidor de caudales")
        Medidor_presion_o_caudal(wnx, vecq, 'caudal')
    
    #Asigno el area del orificio de fugas a los nodos
    n = len(nfugas)
    for i in range(0,n,1):
        node = wnx.get_node(nfugas[i])
        node.add_leak(wnx, area=ce[i],start_time=nhf_inicial[i]*3600, end_time=nhf_final[i]*3600)
    #Ahora corro el modelo con wntrnosimulator
    sim = wntr.sim.WNTRSimulator(wnx)
    results = sim.run_sim()
    #Extraigo los datos de caudal en las tuberias cuando tengo medidores de flujo
    if ntipo == 'caudal':
        ncaudal = len(vecq)
        flow = results.link['flowrate']*1000
        df_caudales = pd.DataFrame()
        for y in range(0,ncaudal,1):
            df_caudales[vecq[y]] = flow.loc[:,vecq[y]]
        df_caudales.index  /= 3600 #TIEMPO A HORAS
        #GENERAMOS EL EXCEL
        with pd.ExcelWriter("Resultados_caudales_confugas.xlsx") as writer:
            df_caudales.to_excel(writer, sheet_name='Caudales', index_label='Tiempo')
        print("########_ESCENARIO CON FUGAS EN LA RED_##########")
        print("Archivo Excel generado exitosamente.")
        
    #Extraigo los datos de caudal en los nodos cuando tengo medidores de presión
    if ntipo == 'presion':
        npresion = len(vecq)
        presion = results.node['pressure'] 
        df_presiones = pd.DataFrame()
        for i in range(0,npresion,1):
            df_presiones[vecq[i]] = presion.loc[:,vecq[i]]
        df_presiones.index  /= 3600 #TIEMPO A HORAS
        #GENERAMOS EL EXCEL
        with pd.ExcelWriter("Resultados_presiones_confuga.xlsx") as writer:
            df_presiones.to_excel(writer,sheet_name='Presiones', index_label='Tiempo')
        print("########_ESCENARIO CON FUGAS EN LA RED_##########")
        print("Archivo Excel generado exitosamente.")

def Medidor_fugas_presion_y_caudal(wnx,vecq,vecp,nfugas,ce,nhf_inicial, nhf_final):
    
    #Extraigo los valores de caudal o presión antes de asignar la fuga
    Medidor_presion_y_caudal(wnx, vecq, vecp)
    
    #Asigno el area del orificio de fugas a los nodos
    n = len(nfugas)
    for i in range(0,n,1):
        node = wnx.get_node(nfugas[i])
        node.add_leak(wnx, area=ce[i],start_time=nhf_inicial[i]*3600, end_time=nhf_final[i]*3600)
    
    #Ahora corro el modelo con wntrsimulator
    sim = wntr.sim.WNTRSimulator(wnx)
    results = sim.run_sim()
   #dataframe
    df_pres = pd.DataFrame()
    df_cau = pd.DataFrame()
    
    #caudal
    ncaudal = len(vecq)
    flow = results.link['flowrate']*1000
    #presion 
    npresion = len(vecp)
    presion = results.node['pressure'] 
    
    for y in range(0,ncaudal,1):
        df_cau[vecq[y]] = flow.loc[:,vecq[y]]
    df_cau.index  /= 3600 #TIEMPO A HORAS

    for i in range(0,npresion,1):
        df_pres[vecp[i]] = presion.loc[:,vecp[i]]
    df_pres.index  /= 3600 #TIEMPO A HORAS
    print("########_ESCENARIO CON FUGAS EN LA RED_##########")
    # Guardar los datos en un archivo Excel
    with pd.ExcelWriter("Resultados_presiones_caudales_confugas.xlsx") as writer:
        df_pres.to_excel(writer, sheet_name="Presiones", index_label='Tiempo')
        df_cau.to_excel(writer, sheet_name="Caudales", index_label='Tiempo') 
    print("Archivo Excel generado exitosamente.")


###################################################################################
#Funcion para la variación de la demanda e imprimir presiones y caudales
def Medidor_presion_o_caudal_demanda(wnx,vec,tipo, fdmin, fdmax):
    #Extraigo los valores existentes de la curva de consumo
    patt = wnx.pattern_name_list    
    patt_c = wnx.get_pattern(patt[0])
    value_patt_d = patt_c.multipliers
    resul_value_d = value_patt_d
    nhoras = len(resul_value_d)
    fc_d = [0]*nhoras
    for i in range(0,nhoras,1):
        #creo un número aleatorio a partir de los limites y lo multiplico a
        x_d = rd.uniform(fdmin,fdmax)
        fc_d[i] = x_d*resul_value_d[i]
    
    #Asigno los nuevos valores a la curva con el factor mutiplicador                
    patt_c.multipliers = fc_d
        
    #simulo la red    
    sim = wntr.sim.EpanetSimulator(wnx)
    results = sim.run_sim()
    #extraigo los datos de presion de los nodos
    if tipo == 'presion':
        npresion = len(vec)
        #nmp = [0]*npresion
        presion = results.node['pressure'] 
        df_presiones = pd.DataFrame()
        for i in range(0,npresion,1):
            #nmp[i] = presion.loc[:,vec[i]]
            df_presiones[vec[i]] = presion.loc[:,vec[i]]
        df_presiones.index  /= 3600 #TIEMPO A HORAS
        
        #GENERAMOS EL EXCEL
        with pd.ExcelWriter("Resultados_presiones_conVDemanda.xlsx") as writer:
            df_presiones.to_excel(writer,sheet_name='Presiones', index_label='Tiempo')
        print("########_ESCENARIO CON VARIACIONES EN LA DEMANDA DE LA RED_#######")
        print("Archivo Excel  generado exitosamente.")
        
    if tipo == 'caudal':
        ncaudal = len(vec)
        #nmq = [0]*ncaudal
        flow = results.link['flowrate']*1000
        df_caudales = pd.DataFrame()
        for y in range(0,ncaudal,1):
            #nmq[y] = flow.loc[:,vec[y]]
            df_caudales[vec[y]] = flow.loc[:,vec[y]]
        df_caudales.index  /= 3600 #TIEMPO A HORAS
        #GENERAMOS EL EXEL
        with pd.ExcelWriter("Resultados_caudales_conVDemanda.xlsx") as writer:
            df_caudales.to_excel(writer, sheet_name='Caudales', index_label='Tiempo')
        print("########_ESCENARIO CON VARIACIONES EN LA DEMANDA DE LA RED_#######")
        print("Archivo Excel  generado exitosamente.")

#Funcion cuando se presentan medidores de presión y caudal
def Medidor_presion_y_caudal_demanda(wnx,vecq,vecp,fdmin, fdmax):
    #Extraigo los valores existentes de la curva de consumo
    patt = wnx.pattern_name_list    
    patt_c = wnx.get_pattern(patt[0])
    value_patt_d = patt_c.multipliers
    resul_value_d = value_patt_d
    nhoras = len(resul_value_d)
    fc_d = [0]*nhoras
    for i in range(0,nhoras,1):
        #creo un número aleatorio a partir de los limites y lo multiplico a
        x_d = rd.uniform(fdmin,fdmax)
        fc_d[i] = x_d*resul_value_d[i]
    
    #Asigno los nuevos valores a la curva con el factor mutiplicador                
    patt_c.multipliers = fc_d
    
    #simulo la red
    sim = wntr.sim.EpanetSimulator(wnx)
    results = sim.run_sim()
    npresion = len(vecp)
    ncaudal = len(vecq)
    flow = results.link['flowrate']*1000
    presion = results.node['pressure'] 
    #pandas to exel
    df_pres = pd.DataFrame()
    df_cau = pd.DataFrame()
    #print("PRESIONES")
    for i in range(0,npresion,1):
        df_pres[vecp[i]] = presion.loc[:,vecp[i]]
    df_pres.index  /= 3600 #TIEMPO A HORAS
    #print("caudales")
    for y in range(0,ncaudal,1):
        #nmq[y] = flow.loc[:,vecq[y]]
        df_cau[vecq[y]] = flow.loc[:,vecq[y]]
    df_cau.index  /= 3600 #TIEMPO A HORAS
    
    print("########_ESCENARIO CON VARIACIONES EN LA DEMANDA DE LA RED_#######")
    # Guardar los datos en un archivo Excel
    with pd.ExcelWriter("Resultados_presiones_caudales_conVDemanda.xlsx") as writer:
        df_pres.to_excel(writer, sheet_name="Presiones", index_label='Tiempo')
        df_cau.to_excel(writer, sheet_name="Caudales", index_label='Tiempo') 
    print("Archivo Excel generado exitosamente.")

###################################################################################
#Funcion para la variación de la rugusidad e imprimir presiones y caudales
def Medidor_presion_o_caudal_rugosidad(wnx,vec,tipo,rumin, rumax):
    #Extraigo los nombres de las tuberias
    link_names = wnx.link_name_list
    #Extraigo el número de tuberias
    ntub = len(link_names)
    #Asigno las nuevas rugosidades a la red
    roughness_t = [0]*ntub
    for i in range(0,ntub,1):
        x_r = rd.uniform(rumin,rumax)
        pipe = wnx.get_link(link_names[i])
        roughness_t[i] = pipe.roughness*x_r
        pipe.roughness = pipe.roughness*x_r
    
    #simulo la red    
    sim = wntr.sim.EpanetSimulator(wnx)
    results = sim.run_sim()
    #extraigo los datos de presion de los nodos
    if tipo == 'presion':
        npresion = len(vec)
        #nmp = [0]*npresion
        presion = results.node['pressure'] 
        df_presiones = pd.DataFrame()
        for i in range(0,npresion,1):
            #nmp[i] = presion.loc[:,vec[i]]
            df_presiones[vec[i]] = presion.loc[:,vec[i]]
        df_presiones.index  /= 3600 #TIEMPO A HORAS
        
        #GENERAMOS EL EXCEL
        with pd.ExcelWriter("Resultados_presiones_conVRugosidad.xlsx") as writer:
            df_presiones.to_excel(writer,sheet_name='Presiones', index_label='Tiempo')
        
        print("#######_ESCENARIO CON VARIACIONES DE LA RUGOSIDAD EN LA RED_#######")       
        print("Archivo Excel  generado exitosamente.")
         
    if tipo == 'caudal':
        ncaudal = len(vec)
        #nmq = [0]*ncaudal
        flow = results.link['flowrate']*1000
        df_caudales = pd.DataFrame()
        for y in range(0,ncaudal,1):
            #nmq[y] = flow.loc[:,vec[y]]
            df_caudales[vec[y]] = flow.loc[:,vec[y]]
        df_caudales.index  /= 3600 #TIEMPO A HORAS
        #GENERAMOS EL EXEL
        with pd.ExcelWriter("Resultados_caudales_conVRugosidad.xlsx") as writer:
            df_caudales.to_excel(writer, sheet_name='Caudales', index_label='Tiempo')
        print("#######_ESCENARIO CON VARIACIONES DE LA RUGOSIDAD EN LA RED_#######")
        print("Archivo Excel  generado exitosamente.")
          
def Medidor_presion_y_caudal_rugosidad(wnx,vecq,vecp,rumin, rumax):
    #Extraigo los nombres de las tuberias
    link_names = wnx.link_name_list
    #Extraigo el número de tuberias
    ntub = len(link_names)
    #Asigno las nuevas rugosidades a la red
    roughness_t = [0]*ntub
    for i in range(0,ntub,1):
        x_r = rd.uniform(rumin,rumax)
        pipe = wnx.get_link(link_names[i])
        roughness_t[i] = pipe.roughness*x_r
        pipe.roughness = pipe.roughness*x_r
    
    #simulo la red con los nuevos valores de rugosidad
    sim = wntr.sim.EpanetSimulator(wnx)
    results = sim.run_sim()
    npresion = len(vecp)
    ncaudal = len(vecq)
    flow = results.link['flowrate']*1000
    presion = results.node['pressure'] 
    #pandas to exel
    df_pres = pd.DataFrame()
    df_cau = pd.DataFrame()
    #print("PRESIONES")
    for i in range(0,npresion,1):
        df_pres[vecp[i]] = presion.loc[:,vecp[i]]
    df_pres.index  /= 3600 #TIEMPO A HORAS
    #print("caudales")
    for y in range(0,ncaudal,1):
        #nmq[y] = flow.loc[:,vecq[y]]
        df_cau[vecq[y]] = flow.loc[:,vecq[y]]
    df_cau.index  /= 3600 #TIEMPO A HORAS
    
    print("#######_ESCENARIO CON VARIACIONES DE LA RUGOSIDAD EN LA RED_#######")
    print("EXCEL")
    # Guardar los datos en un archivo Excel
    with pd.ExcelWriter("Resultados_presiones_caudales_conVRugosidad.xlsx") as writer:
        df_pres.to_excel(writer, sheet_name="Presiones", index_label='Tiempo')
        df_cau.to_excel(writer, sheet_name="Caudales", index_label='Tiempo') 
    print("Archivo Excel generado exitosamente.")
        
###################################################################################
#Funcion para cerrar tuberías e imprimir presiones y caudales
def Medidor_presion_o_caudal_tcerradas(wnx,vec,tipo, nametubc):
    #cierro las tuberías en la red
    ntub = len(nametubc)
    for name, pipe in wn.pipes():
        for i in range(0,ntub,1):
            if pipe.name == nametubc[i]:
                pipe.initial_status = 'Closed'
                    
    #simulo la red    
    sim = wntr.sim.EpanetSimulator(wnx)
    results = sim.run_sim()
    #extraigo los datos de presion de los nodos
    if tipo == 'presion':
        npresion = len(vec)
        #nmp = [0]*npresion
        presion = results.node['pressure'] 
        df_presiones = pd.DataFrame()
        for i in range(0,npresion,1):
            #nmp[i] = presion.loc[:,vec[i]]
            df_presiones[vec[i]] = presion.loc[:,vec[i]]
        df_presiones.index  /= 3600 #TIEMPO A HORAS
        
        #GENERAMOS EL EXCEL
        with pd.ExcelWriter("Resultados_presiones_conTcerradas.xlsx") as writer:
            df_presiones.to_excel(writer,sheet_name='Presiones', index_label='Tiempo')
        
        print("#########_ESCENARIO CON TUBERÍAS CERRADAS EN LA RED_###########")       
        print("Archivo Excel  generado exitosamente.")
         
    if tipo == 'caudal':
        ncaudal = len(vec)
        #nmq = [0]*ncaudal
        flow = results.link['flowrate']*1000
        df_caudales = pd.DataFrame()
        for y in range(0,ncaudal,1):
            #nmq[y] = flow.loc[:,vec[y]]
            df_caudales[vec[y]] = flow.loc[:,vec[y]]
        df_caudales.index  /= 3600 #TIEMPO A HORAS
        #GENERAMOS EL EXEL
        with pd.ExcelWriter("Resultados_caudales_conTcerradas.xlsx") as writer:
            df_caudales.to_excel(writer, sheet_name='Caudales', index_label='Tiempo')
        print("#########_ESCENARIO CON TUBERÍAS CERRADAS EN LA RED_###########")
        print("Archivo Excel  generado exitosamente.")
    
def Medidor_presion_y_caudal_tcerradas(wnx,vecq,vecp,nametubc):
    #cierro las tuberías en la red
    ntub = len(nametubc)
    for name, pipe in wn.pipes():
        for i in range(0,ntub,1):
            if pipe.name == nametubc[i]:
                pipe.initial_status = 'Closed'
    
    #simulo la red con los nuevos valores de rugosidad
    sim = wntr.sim.EpanetSimulator(wnx)
    results = sim.run_sim()
    npresion = len(vecp)
    ncaudal = len(vecq)
    flow = results.link['flowrate']*1000
    presion = results.node['pressure'] 
    #pandas to exel
    df_pres = pd.DataFrame()
    df_cau = pd.DataFrame()
    #print("PRESIONES")
    for i in range(0,npresion,1):
        df_pres[vecp[i]] = presion.loc[:,vecp[i]]
    df_pres.index  /= 3600 #TIEMPO A HORAS
    #print("caudales")
    for y in range(0,ncaudal,1):
        #nmq[y] = flow.loc[:,vecq[y]]
        df_cau[vecq[y]] = flow.loc[:,vecq[y]]
    df_cau.index  /= 3600 #TIEMPO A HORAS
    
    print("#########_ESCENARIO CON TUBERÍAS CERRADAS EN LA RED_###########")
    # Guardar los datos en un archivo Excel
    with pd.ExcelWriter("Resultados_presiones_caudales_conTcerradas.xlsx") as writer:
        df_pres.to_excel(writer, sheet_name="Presiones", index_label='Tiempo')
        df_cau.to_excel(writer, sheet_name="Caudales", index_label='Tiempo') 
    print("Archivo Excel generado exitosamente.")
    

##################################################################################
#Función para iniciar toda la simulación
def Iniciar_Simulacion(wnx):
    global nmpresion,nmcaudal,nmfugas, areafuga, patt, nhf_inicial, nhf_final    
    global fmmin, fmmax, frumin, frumax, tubc, mtubc
    #Asigno lo valores del factor de consumo para la simulacion
    horas = 24*dias
    fc = [0]*horas
    patt = wnx.pattern_name_list    
    patt_c = wnx.get_pattern(patt[0])
    value_patt = patt_c.multipliers
    resul_value = value_patt
    #Creo un vector que une todas las listas 
    for i in range(1,dias,1):
        resul_value = list(itertools.chain(resul_value, value_patt))
                
    #Ahora creo valores para los demas días
    for i in range(0,horas,1):
        if i <= 23:
            fc[i] = resul_value[i]
        else:
            x = rd.uniform(0.95,1.1)
            fc[i] = x*resul_value[i]
            
    #Asigno los nuevos la valores a la curva del factor de consumo en n días                
    patt_c.multipliers = fc
    wnx.options.hydraulic.demand_model = 'PDD'
    wnx.options.time.duration = horas*3600         
    print("horas",horas)
    print("INFORMACIÓN DE LA RED")
    print("DIAS:",dias,"MEDPRE:",medP,"MEDCAUD:",medQ)
    print("ESCENARIOS PARA SIMULAR")
    print("FUGAS:",medF,"DEMANDA:",medd,"RUGOSIDADES:",meru, "TUBERÍAS CERRADAS:",mtubc)
    
    #####################ESCENARIO NORMAL DE LA RED########################################################################
    if medP == 'SI' and medQ == 'NO' :
        print("solo medidor de presiones")
        Medidor_presion_o_caudal(wnx, nmpresion, 'presion')
        # llamo la funcion de caudal
    if medQ == 'SI' and medP == 'NO':
        print("solo medidor de caudales")
        Medidor_presion_o_caudal(wnx, nmcaudal, 'caudal')
    if medP == 'SI' and medQ == 'SI':
        print("medidor de caudales/presion")
        Medidor_presion_y_caudal(wnx, nmcaudal, nmpresion)

        # Llamo la funciones cuando se presentan fugas, para varios dias de simulación
    #####################ESCENARIO DE FUGAS########################################################################
    if medF == 'SI':
            if medP == 'SI' and medQ == 'NO':
                print("solo medidor de presiones y fugas")
                Medidor_fugas_presion_o_caudal(wnx, nmpresion,'presion',nmfugas,areafuga, nhf_inicial, nhf_final )
            # llamo la funcion de caudal
            if medQ == 'SI' and medP == 'NO':
                print("solo medidor de caudales  y fugas")
                Medidor_fugas_presion_o_caudal(wnx, nmcaudal,'caudal',nmfugas,areafuga, nhf_inicial, nhf_final)

            if medP == 'SI'  and medQ == 'SI':
                print("Medidor de caudales/presion con fugas")
                Medidor_fugas_presion_y_caudal(wnx, nmcaudal,nmpresion,nmfugas,areafuga, nhf_inicial, nhf_final)
    
    #####################ESCENARIO DE VARIACIÓN DE DEMANDA########################################################################
    if medd =='SI':        
        if medP == 'SI' and medQ == 'NO' :
            print("solo medidor de presiones")
            Medidor_presion_o_caudal_demanda(wnx, nmpresion, 'presion',fmmin, fmmax)
            # llamo la funcion de caudal
        if medQ == 'SI' and medP == 'NO':
            print("solo medidor de caudales")
            Medidor_presion_o_caudal_demanda(wnx, nmcaudal, 'caudal',fmmin, fmmax)
        if medP == 'SI' and medQ == 'SI':
            print("medidor de caudales/presion")
            Medidor_presion_y_caudal_demanda(wnx, nmcaudal, nmpresion, fmmin, fmmax)
    
    #####################ESCENARIO DE VARIACIÓN DE RUGOSIDAD########################################################################
    if meru =='SI':        
        if medP == 'SI' and medQ == 'NO' :
            print("solo medidor de presiones")
            Medidor_presion_o_caudal_rugosidad(wnx, nmpresion, 'presion',frumin, frumax)
            # llamo la funcion de caudal
        if medQ == 'SI' and medP == 'NO':
            print("solo medidor de caudales")
            Medidor_presion_o_caudal_rugosidad(wnx, nmcaudal, 'caudal',frumin, frumax)
        if medP == 'SI' and medQ == 'SI':
            print("medidor de caudales/presion")
            Medidor_presion_y_caudal_rugosidad(wnx, nmcaudal, nmpresion, frumin, frumax)   
    
    #####################ESCENARIO DE TUBERÍAS CERRADAS RED#########################################################################
    if mtubc =='SI':        
        if medP == 'SI' and medQ == 'NO' :
            print("solo medidor de presiones")
            Medidor_presion_o_caudal_tcerradas(wnx, nmpresion, 'presion', tubc)
            # llamo la funcion de caudal
        if medQ == 'SI' and medP == 'NO':
            print("solo medidor de caudales")
            Medidor_presion_o_caudal_tcerradas(wnx, nmcaudal, 'caudal',tubc)
        if medP == 'SI' and medQ == 'SI':
            print("medidor de caudales/presion")
            Medidor_presion_y_caudal_tcerradas(wnx, nmcaudal, nmpresion, tubc)




def BuscarFile():
    filepath = filedialog.askopenfilename(title="Selecciona un archivo", filetypes=[("inp files", "*.inp")])
    if filepath:
        return filepath

################################DEFINIR LISTAS##################################
#declaracion de listas evitamos errores
nmpresion =[]
nmcaudal =[]
nmfugas=[]
areafuga =[]
dias=1  # evita error sin dias
Validar_inp= False

################################ABRIR INP##################################
directorio_actual = os.getcwd()
archivos_en_directorio = os.listdir(directorio_actual)
archivos_txt = [archivo for archivo in archivos_en_directorio if archivo.endswith(".txt")]
archivos_inp = [archivo for archivo in archivos_en_directorio if archivo.endswith(".inp")]

# Verificar si se encontró algún archivo .txt
if archivos_txt:
    # Si hay varios archivos .inp, puedes elegir uno específico o procesarlos todos en un bucle
    nombre_archivo_txt = archivos_txt[0]
    data = pd.read_csv(nombre_archivo_txt, sep= ";", skiprows=8, index_col=0)
    print(f"Se encontró el archivo {nombre_archivo_txt}.")
    Validar_txt = True
else:
    # si no se encuentra lo buscamos
    print("No se encontró ningún archivo .txt en la carpeta actual.")
    print("Seleccione el Archivo txt")
    root = Tk()
    ruta_txt = BuscarFile()
    root.withdraw()  # Ocultar la ventana principa
    if ruta_txt is not None:
        data = pd.read_csv(ruta_txt, sep= ";", skiprows=8, index_col=0)
        Validar_txt = True
        
    else:
        print("LA RUTA está vacío o no ha sido inicializada.")

# Verificar si se encontró algún archivo .inp
if archivos_inp:
    # Si hay varios archivos .inp, puedes elegir uno específico o procesarlos todos en un bucle
    nombre_archivo_inp = archivos_inp[0]
    print(f"Se encontró el archivo {nombre_archivo_inp}.")
    #Asigno la red a wntr
    wn = wntr.network.WaterNetworkModel(nombre_archivo_inp)
    #Determino el nombre de los nodos y tuberias
    Validar_inp = True
else:
    # si no se encuentra lo buscamos
    print("No se encontró ningún archivo .inp en la carpeta actual.")
    print("Seleccione el Archivo inp")
    root = Tk()
    ruta = BuscarFile()
    root.withdraw()  # Ocultar la ventana principa
    if ruta is not None:
        #longitud = len(ruta)
        #print(f"Longitud del ruta: {longitud}")
        wn = wntr.network.WaterNetworkModel(ruta)
        Validar_inp = True
        
    else:
        print("LA RUTA está vacío o no ha sido inicializada.")


#extraigo los valores del archivo de texto encontrado
if Validar_txt:
                
    #Extraigo si la simulación va hacer por varios días
    dias = int(data["Interfaz"]["Rta1"])
            
    #Medidores de presión
    medP = str(data["Interfaz"]["Rta2"])
    if medP == 'SI' or medP == "si":
        nmpresion = str(data["Interfaz"]["Rta2.1"])
        nmpresion =nmpresion.split(",")
            
    #Medidores de Caudal     
    medQ = str(data["Interfaz"]["Rta3"])
    if medQ == 'SI' or medQ == 'si':
        nmcaudal = str(data["Interfaz"]["Rta3.1"])
        nmcaudal = nmcaudal.split(",")
        
    #Fugas en el sistema
    medF = str(data["Interfaz"]["Rta4"])
    if medF == 'SI' or medF == 'si':
        nmfugas = str(data["Interfaz"]["Rta4.1"])
        nmfugas = nmfugas.split(",")
        areafuga = (data["Interfaz"]["Rta4.2"])
        areafuga = areafuga.split(",")
        areafuga = list(map(float,areafuga))
        nhf_inicial = (data["Interfaz"]["Rta4.3"])
        nhf_inicial = nhf_inicial.split(",")
        nhf_inicial = list(map(float,nhf_inicial))
        nhf_final = (data["Interfaz"]["Rta4.4"])
        nhf_final = nhf_final.split(",")
        nhf_final = list(map(float,nhf_final))
    
    #Variación de la demanda en la red
    medd = str(data["Interfaz"]["Rta5"])
    if medd == 'SI' or medd == 'si':
        fmmin = float(data["Interfaz"]["Rta5.1"])
        fmmax = float(data["Interfaz"]["Rta5.2"])
    
    #Variación de la rugosidad en la red
    meru = str(data["Interfaz"]["Rta6"])
    if meru == 'SI' or meru == 'si':
        frumin = float(data["Interfaz"]["Rta6.1"])
        frumax = float(data["Interfaz"]["Rta6.2"])
    
    #tuberías en la red cerradas
    mtubc = str(data["Interfaz"]["Rta7"])
    if mtubc == 'SI' or mtubc == 'si':
        tubc = str(data["Interfaz"]["Rta7.1"])
        tubc = tubc.split(",")
        
    print("\n")
    print("#######################################################")
    print("##Iniciando simulacion")
    Iniciar_Simulacion(wn)
    print("## Finalizo simulacion")

else:
    print("error de ejecucion")


