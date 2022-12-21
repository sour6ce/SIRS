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

+ Interpretación de la query (decir que es igual a la del vectorial)
+ Cálculo de relevancia

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