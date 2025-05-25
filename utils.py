import pandas as pd
import numpy as np
import os
def leer_spec(path,ot=False,MJD=False,as_pandas=False,compress=False):

    if compress==True:
        import gzip

        with gzip.open(path, 'rb') as f2:
            espectro_lineas= [linea.split() for linea in f2]
    else:
        with open(path,'rt') as f2:
            espectro_lineas= [linea.split() for linea in f2]

    componente_filas_spec=[]
    spec=[]
    fases=[]
    iniciales=[]
    finales=[]
    alphas=[]
    for i in range(len(espectro_lineas)):
        if len(espectro_lineas[i])>1:
            if 'SPEC' in espectro_lineas[i][1] and 'NSPEC' not in espectro_lineas[i][1]:
                componente_filas_spec.append(i)  #me dice en que componente esta el spectro de la posicion

            if 'time:' == espectro_lineas[i][1] :
                fase=espectro_lineas[i][2]

                spec.append(float(fase)) #le saque el round porque me daba espectros repetidos cuando, si lo quiero poner deberia quiza usar un drop duplicates en el
                                            #calculo del rms y mad
                fases=spec
                #print(fase)
            else:
                if MJD==True:
                    if len(espectro_lineas[i])==5:
                        if 'MJD' in espectro_lineas[i][4] and 'SPEC' in espectro_lineas[i]:
                            fase=espectro_lineas[i][4]
                            fase=float(fase.strip('MJD='))
                            spec.append(fase) #saque el round
                            fases=spec
            if ot==True:
                if 'ini:' in espectro_lineas[i][1]:
                    inicial=espectro_lineas[i][2]
                    iniciales.append(float('%.3f'%float(inicial)))
                if 'fin:' in espectro_lineas[i][1]:
                    final=espectro_lineas[i][2]
                    finales.append(float('%.3f'%float(final)))
                if 'alpha:' in espectro_lineas[i][1]:
                    alpha=espectro_lineas[i][2]
                    alphas.append(float('%.3f'%float(alpha)))


    ESPECTRO=[]
    for j in range(len(componente_filas_spec)):
        #nombre_spec = str(spec[j])
        #print (nombre_spec)
        espectro1=[]
        if j==len(componente_filas_spec)-1:
            final=len(espectro_lineas)
            lineas_espectro=np.arange(componente_filas_spec[j]+1,final,1)
            #print (lineas_espectro)
            for i in lineas_espectro:
                if espectro_lineas[i][1]=='WAVE':
                    continue
                if float(espectro_lineas[i][1])!=0:
                    espectro1.append(espectro_lineas[i])

        else:
            if ot==True:
                res=4 #esto es para que lea los archivos bien ya que los OT tienen info extra
            else:
                res=1
            lineas_espectro=np.arange(componente_filas_spec[j]+1,componente_filas_spec[j+1]-res,1) #me dice las lineas que tengo q guardar por filtro
            #print (lineas_espectro)
            for i in lineas_espectro:

                if len(espectro_lineas[i])==0:
                    break
                if espectro_lineas[i][1]=='WAVE':
                    continue

                if float(espectro_lineas[i][1])!=0:
                    espectro1.append(espectro_lineas[i])
        if as_pandas==True:
            #print(len(espectro1[0]))
            #print(espectro1)
            try:
                if len(espectro1[0])==2:
                    espectro1=pd.DataFrame(espectro1,dtype="float64",columns=["wave","flux"])
                elif len(espectro1[0])==3:
                    espectro1=pd.DataFrame(espectro1,dtype="float64",columns=["wave","flux",'fluxerr'])
                else:
                    return print('Imposible llevar a pandas, revisa las columnas')
            except:
                espectro1=pd.DataFrame(espectro1,dtype="float64",columns=["wave","flux"])

        ESPECTRO.append(espectro1)
    #print('Phases:',fases)

    if ot==True:
        return ESPECTRO,fases,iniciales,finales,alphas
    else:
        return ESPECTRO,fases
    

def maximo_lc(tipo,sn,ubuntu=False):
    if tipo=='II':
        if ubuntu==True:
            maximum_df=pd.read_csv("/mnt/g/Mi unidad/Work/OT_unidos_2/OT_combines_test/maximum_II.txt")

        else:
            maximum_df=pd.read_csv("G:\Mi unidad\Work\OT_unidos_2\OT_combines_test\maximum_II.txt")
        max_=float(maximum_df.loc[maximum_df['name']==sn]['fase'])
        return max_
    if tipo=='Ia':
        if ubuntu==True:
             
            df_max=pd.read_csv("/mnt/g/Mi unidad/Work/OT_unidos_2/OT_combines_test/maximum_Ia.txt")
        else:
            df_max=pd.read_csv("G:\Mi unidad\Work\OT_unidos_2\OT_combines_test\maximum_Ia.txt")
        df_max[df_max.name==sn]

    if tipo=='Ibc' or tipo=='Ib' or tipo=='Ic':
            df_max=pd.read_csv(r"G:\Mi unidad\Work\Universidad\Phd\Practica2\maximum_Ibc.dat")
            #df_max=pd.read_csv( "G:\Mi unidad\Spectral Time Series - Ramirez M\Data\maximum_perband.dat")
            df_max[df_max.name==sn]
    
    band_system=['V','R','r','g','i','I','B','U','u','z'] #We use this order to obtain the day of the maximum
    for elemento in band_system:

        maximum=df_max.loc[(df_max['name']==sn) & (df_max['filter']==elemento )]['mjd_max']
        if len(maximum)>0:
            maximum=float(maximum)
            break
    return maximum

def data_curvas(path,rename=False): #funcion para leer los archivos de texto de los filtros
    import pandas as pd
    with open(path,'rt') as f2:
        lineas= [linea.split() for linea in f2]
    cantidad_filtros=0 #contador de filtros
    filtro=[] #arreglo con los filtros
    componente_filas=[] #me dice las componentes de las lineas en que estan los datos por filtro (ejemplo: filtro B de la 7
    for i in range(len(lineas)):
        if len(lineas[i])>=2:
            if lineas[i][1]=='FILTER':
                #print (lineas[i][2])
                cantidad_filtros=cantidad_filtros+1
                filtro.append(lineas[i][2])
                componente_filas.append(i)


    #print ('HAY UN TOTAL DE ',cantidad_filtros,' FILTROS')
    #print (filtro)
    #print (componente_filas)

    FILTRO=[]
    for j in range(len(componente_filas)):
        nombre = "filtro_" + str(filtro[j])
        #print (nombre)
        filtro1=[]
        if j==len(componente_filas)-1:
            final=len(lineas)
            lineas_filtro=np.arange(componente_filas[j]+2,final,1)
            #print (lineas_filtro)
            for i in lineas_filtro:
                filtro1.append(lineas[i])
                filtro1.append
        else:
            lineas_filtro=np.arange(componente_filas[j]+2,componente_filas[j+1]-1,1) #me dice las lineas que tengo q guardar por filtro
            #print (lineas_filtro)
            for i in lineas_filtro:
                filtro1.append(lineas[i])

        filtro1=pd.DataFrame(filtro1)
        #print(filtro1)
        filtro1[0] = filtro1[0].astype(float)
        filtro1[1] = filtro1[1].astype(float)
        filtro1[2]=filtro1[2].astype(float)

        if rename==True:
            filtro1 = filtro1.rename(columns={0: 'mjd', 1: 'flux'})

        FILTRO.append(filtro1)
        #print (filtro1)
    return FILTRO,filtro #me retorna FILTRO donde estan los datos y filtro que es una lista con los filtros