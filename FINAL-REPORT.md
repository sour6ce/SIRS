# Simple Information Recovery System (SIRS)

Integrantes:

* Deborah Famadas Rodríguez ([@dbyta](https://t.me/dbyta))  C-312
* Erick A. Fonseca Pérez ([@TheCrusader](https://t.me/TheCrusader))     C-312
* Gabriel Hernández Rodríguez ([@sour_ce](https://t.me/sour_ce))  C-311

## Tabla de Contenidos

- [Simple Information Recovery System (SIRS)](#simple-information-recovery-system-sirs)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Introducción](#introducción)
  - [Modelos Implementados](#modelos-implementados)
    - [Modelo Vectorial](#modelo-vectorial)
    - [Modelo Booleano](#modelo-booleano)
    - [Modelo de Semántica Latente](#modelo-de-semántica-latente)
  - [Características Adicionales](#características-adicionales)
    - [Eliminación de Stopwords](#eliminación-de-stopwords)
    - [Indexado intermodelo](#indexado-intermodelo)
    - [RESTful API](#restful-api)
    - [Interfaz Web](#interfaz-web)
    - [Arquitectura dirigida a la extensibilidad](#arquitectura-dirigida-a-la-extensibilidad)
  - [Evaluación y Análisis](#evaluación-y-análisis)
  - [Proyección de desarrollo](#proyección-de-desarrollo)
  - [Conclusiones](#conclusiones)

---

## Introducción

+ Problema planteado
+ Objetivo del trabajo

## Modelos Implementados

+ Criterios de selección
+ Explicación de la arquitectura general de un SRI en el proyecto
  + Querifier
  + Collection
  + Index en que se basan las tres colecciones del proyecto
  + Resultados

### Modelo Vectorial

+ Interpretación de la query
+ Cálculo de relevancia

### Modelo Booleano

+ Interpretación de la query
    + Formato especial permitido en las query booleanas (uso de ~, & y |)
    + Ejemplo de queries y utilidad de este sistema
+ Cálculo de relevancia

### Modelo de Semántica Latente

+ El procesamiento de la query se hace de la misma forma que en el modelo vectorial
+ El modelo de semantica latente tiene como base una matriz $\Alpha$ de terminos $W_{i,j}$ donde $W_{i,j}$ es la cantidad de veces que aparece el termino $i$ en el documento $j$ y  se basa en la reduccion de la dimension del espacio vectorial que contiene a los vectores de consultas y documentos.
+ Luego se descompone la matriz $\Alpha = U \cdot S \cdot V^{T}$ usando el algoritmo SVD y se truncan las matrices $U$ y $V$ dejando solo k columnas (k es un numero arbitrario que segun nuestras investigaciones suele situarse alrededor de 100).
+ Luego se procede a recalcular los vectores de documentos y la query ajustandolos a la nueva dimension del espacio (k).
+ Se procede al calcular la similitud entre la query y los documentos modificados y se ordena en ranking de los resultados de calcular la similitud. 

  $sim(q_{k},d_{ki})=\frac{ q_{k} \cdot d_{ki} }{ |q_{k}| |d_{ki}| }$ 

**NOTA**:

El modelo de semantica latente al reducir la dimension del espacion analiza conceptos que pueden estar "latentes", relacionar sinonimos o palabras que se usan en el mismo contexto como por ejemplo "wing" con "aeronautic". 


## Características Adicionales

### Eliminación de Stopwords

+ Fuente de stopwords
+ Momento en que se eliminan estas
+ Ejemplo con una query

### Indexado intermodelo

+ Problema inicial
+ Por qué los tres modelos pueden usar el mismo indexado
+ Solución a través del singleton

### RESTful API

+ Uso de FastAPI
+ Endpoints e instrucciones para el uso

### Interfaz Web

+ Instrucciones para su uso
+ Diferentes secciones

### Arquitectura dirigida a la extensibilidad

+ Objetivo de que el proyecto sea extensible
+ Cómo incorporar un dataset
+ Cómo incorporar un nuevo modelo

## Evaluación y Análisis

+ Características de las consultas de prueba
+ Cálculo de Precisión, Recobrado y Fórmula F1 de cada modelo con cada dataset
+ Cálculo de la velocidad en la recuperación
+ Medidas de tendencia central de estos valores
+ Explicación de por qué estos resultados son malos
+ Defender el modelo booleano como opción recomendada (al menos en Cranfield)

## Proyección de desarrollo

+ Solucionar defectos actuales del proyecto
    + Escalabilidad en memoria pero no en tiempo en bases de datos grandes. Posible solución utilizando sistema distribuido
    + Falta de Stemming. Explicación de cómo afecta esto
+ Posible implementación de algoritmo de agrupamiento
+ Retroalimentación
+ Pulir en dirección a experiencia de usuario o a servicio web
+ Dirigir el producto en función de datasets específicos con características específicas

## Conclusiones

+ Defensa del producto final
+ Conocimiento adquirido