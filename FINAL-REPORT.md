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
  - [Arquitectura General](#arquitectura-general)
    - [Modelo Vectorial](#modelo-vectorial)
    - [Modelo Booleano](#modelo-booleano)
    - [Modelo de Semántica Latente](#modelo-de-semántica-latente)
  - [Características (*Features*) del proyecto](#características-features-del-proyecto)
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

Mediante este trabajo se desea implementar un sistema que agrupe distintos subsistemas de recuperación de información. Todos bajo un mismo servicio central y cada uno de ellos con su propio modelo y peculiaridades

## Modelos Implementados

Basado en lo estudiado durante el curso, en el contenido de la bibliografía fundamental para el proyecto$^{[1]}$ y en los requerimientos dados en la orientación se decidieron implementar los siguientes modelos:
+ Modelo Vectorial
+ Modelo Booleano
+ Modelo de Semántica Latente

El modelo vectorial es un modelo clásico que se conoce que da por lo general muy buenos resultados a pesar de su simplicidad, por eso era una elección obvia su implementación.

El modelo booleano presenta ciertas características que permiten a un usuario más preparado ajustar las consultas al sistema para recuperar información de manera más exacta. En *datasets* como Cranfield puede ser de gran utilidad este modelo.

Derivado del modelo vectorial, el modelo de semántica latente (**LSI**) al reducir la dimension del espacio de los vectores de los documentos del modelo vectorial permite encontrar conceptos que pueden estar "latentes" y relacionar sinónimos o palabras que se usan en el mismo contexto como por ejemplo "*wing*" con "*aeronautic*".

## Arquitectura General

Como se decía anteriormente este sistema está conformado de una serie de subsistema destinados a implementaciones de modelos distintos. Cada uno de estos subsistemas se considera un SRI independiente aunque en la práctica no es así ya que funcionan sobre el mismo *dataset* y sobre un mismo caché con información de la frecuencia de los términos en los documentos. Esto último es posible ya que los tres modelos implementados se basan en esta información para calcular la relevancia de los documentos respecto a una consulta.

Cada subsistema es una clase que hereda de `engine.core.IRS` y contiene 4 componentes principales:
+ `querifier` (Tipo: `engine.core.IRQuerifier`): es un objeto que se encarga de recibir una consulta en texto plano y transformarla en un objeto que el sistema pueda procesar para calcular su relevancia. Se espera que cada modelo implemente el suyo propio según las características de este.
+ `collection` (Tipo: `engine.core.IRCollection`): es el objeto central de un SRI encargado de llevar la información de los modelos indexados y de, dado un objeto consulta válido, obtener la relevancia de cada uno de estos con respecto a esa consulta.
+ `indexer` (Tipo: `engine.core.IRIndexer`): su función es dado un documento de tipo `engine.core.RawDocumentData` extraer la secuencia de tokens a indexar. Su tipo base incorpora ya una implementación básica de este proceso en el cual se extraen palabras en el orden en que aparecen y se eliminan las *stopwords* ([ver más adelante](#eliminación-de-stopwords))
+ `data_getter` (Tipo: `engine.core.RawDataGetter`): a diferencia de los anteriores el comportamiento de este objeto no depende del modelo que implementa el subsistema sino del *dataset* que se esté usando ya que implementa funciones para extraer documentos de este. Es por esto que mientras los componentes anteriores están pensados para definirse y ser instanciados junto al SRI este lo establece la aplicación según el *dataset* en uso. 

### Modelo Vectorial

+ Interpretación de la consulta
+ Cálculo de relevancia

### Modelo Booleano

+ Interpretación de la consulta
    + Formato especial permitido en las consulta booleanas (uso de ~, & y |)
    + Ejemplo de queries y utilidad de este sistema
+ Cálculo de relevancia

### Modelo de Semántica Latente

+ El procesamiento de la consulta se hace de la misma forma que en el modelo vectorial
+ El modelo de semantica latente tiene como base una matriz $\Alpha$ de terminos $W_{i,j}$ donde $W_{i,j}$ es la cantidad de veces que aparece el termino $i$ en el documento $j$ y  se basa en la reduccion de la dimension del espacio vectorial que contiene a los vectores de consultas y documentos.
+ Luego se descompone la matriz $\Alpha = U \cdot S \cdot V^{T}$ usando el algoritmo SVD y se truncan las matrices $U$ y $V$ dejando solo k columnas (k es un numero arbitrario que segun nuestras investigaciones suele situarse alrededor de 100).
+ Luego se procede a recalcular los vectores de documentos y la consulta ajustandolos a la nueva dimension del espacio (k).
+ Se procede al calcular la similitud entre la consulta y los documentos modificados y se ordena en ranking de los resultados de calcular la similitud. 

  $sim(q_{k},d_{ki})=\frac{ q_{k} \cdot d_{ki} }{ |q_{k}| |d_{ki}| }$ 

**NOTA**:

El modelo de semantica latente al reducir la dimension del espacion analiza conceptos que pueden estar "latentes", relacionar sinonimos o palabras que se usan en el mismo contexto como por ejemplo "wing" con "aeronautic". 


## Características (*Features*) del proyecto

### Eliminación de Stopwords

Las *stopwords* son palabras que se considera que no aportan significado, o que no son importantes para un SRI, normalmente son palabras que son muy comunes o que cumplen una función puramente gramatical en el texto. Para obtener una lista de stopwords se utilizó la preexistente lista en la librería **nltk** y de las consideradas por otros desarrolladores en sus proyectos de procesamiento de lenguaje natural.

La eliminación de estas palabras para el indexado de documentos se realiza como se dijo anteriormente con el componente `indexer` del SRI y también, en el caso de los 3 modelos implementados, en el `querifier` eliminando estas palabras también de la consulta.

Como ejemplo, en la consulta *'The thermodynamics in fluids and solids'* se tomaría en cuenta la aparición de los términos *thermodynamics*, *fluids* y *solids* únicamente.

### Indexado intermodelo

En un sistema como este donde se implementan varios modelos de recuperación de información es vital ahorrar la mayor cantidad de memoria posible, además, si se implementara por separado los cachés de información de cada modelo la información estaría repetida innecesariamente ya que la información con la que trabajan es similar.

El modelo vectorial necesita saber con que frecuencia aparece un término en un documento y el modelo booleano solo necesita saber si un término aparece o no, por tanto, solo con la primera información es suficiente. El modelo de semántica latente utiliza los mismos datos del vectorial además de las matrices del **SVD** las cuales son particulares y no se guardan en caché.

Para lograr esto, parte de las funciones del objeto `collection` de los SRI está delegada a un objeto llamado `index` dentro de la colección que se encarga de guardar información de la aparición de los términos en los documentos del SRI y de gestionar un caché local con esta información. Este se implementó con un patrón de diseño singleton para asegurar que los modelos se alimenten de un único objeto.

### RESTful API

El proyecto está pensado para utilizarse por 3 tipos de clientes distintos:
+ Aplicaciones locales: utilizando las clases definidas en `engine` como módulo de la aplicación al estilo de una API clásica.
+ Usuarios Finales: a través del sitio básico de la aplicación que permite realizar búsquedas con los modelos y el *dataset* definidos y ver los resultados.
+ Aplicaciones clientes: son aplicaciones que se sirven de esta aplicaciones que son clientes del servicio web brindado por esta aplicación a través de una RESTful API.

Esta API REST cuenta con una serie de endpoints con parámetros

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