# Sistema Vectorial de Recuperación de Información SIRS

Integrantes:

* Deborah Famadas Rodríguez ([@dbyta](https://t.me/dbyta))  C-312
* Erick A. Fonseca Pérez ([@TheCrusader](https://t.me/TheCrusader))     C-312
* Gabriel Hernández Rodríguez ([@sour_ce](https://t.me/sour_ce))  C-311

## Tabla de contenidos

- [Sistema Vectorial de Recuperación de Información SIRS](#sistema-vectorial-de-recuperación-de-información-sirs)
  - [Tabla de contenidos](#tabla-de-contenidos)
  - [Introducción](#introducción)
  - [SIRS](#sirs)
    - [**Obtención de documentos**](#obtención-de-documentos)
    - [**Procesamiento de documentos**](#procesamiento-de-documentos)
    - [**Representación de los documentos**](#representación-de-los-documentos)
    - [**Procesamiento y Representación de la consulta**](#procesamiento-y-representación-de-la-consulta)
    - [**Funcionamiento del motor de búsqueda y obtención de resultados**](#funcionamiento-del-motor-de-búsqueda-y-obtención-de-resultados)
  - [Conclusiones](#conclusiones)
  - [Referencias](#referencias)

---

## Introducción

Con la aparición de las redes sociales y el crecimiento de los medios de obtención de información se hizo necesaria la creación de una herramienta de filtrado y recuperación de la misma para su fácil acceso y lectura. El modelo vectorial es uno de los modelos más usados para este propósito y aunque existen muchos modelos derivados de este, su versión clásica es muy eficiente$^{[1]}$ aunque presente claras limitaciones$^{[2]}$. Debido a esto fue implementado en el presente proyecto.

## SIRS

Este sistema de recuperación de información posee una arquitectura base abstracta pensada para implementar sobre ella cualquier modelo. Esa arquitectura se basa en la utilización de una colección que gestiona la información que se tiene sobre los documentos del sistema así como el cálculo de la similitud/relevancia respecto a una consulta. Junto a la colección el sistema tiene dos componentes: el *indexer*, encargado de definir cómo se indexarán los documentos para incorporarlos al sistema; y el *querifier*, encargado de transformar el texto de una consulta en un objeto consulta que pueda aplicarse en el modelo.

Estos componentes acceden a los documentos sobre los que se aplica el modelo a través de una capa intermedia que generaliza el acceso a estos documentos independiente a su *dataset* origen.

Para representar al sistema se utiliza una clase `engine.core.IRS` que engloba las funciones de añadir documentos y realizar queries utilizando los componentes definidos por separado e incluidos dentro de este.

Actualmente se implementa sobre esta arquitectura únicamente un modelo vectorial con cálculo del peso de los términos con la fórmula $tf \times idf$ y obtención de documentos del dataset **Cranfield**.

### **Obtención de documentos**

Dentro del sistema una vez que los documentos se encuentran indexados su información completa (título y texto original) no es cargada excepto para mostrar los resultados de una consulta realizada. Esto se debe a que internamente se utilizan los *IDs* de los documentos para acceder y guardar información sobre estos.

Para poder leer su información completa se define una clase abstracta llamada `engine.core.RawDataGetter`, el cual dado el ID del documento debe retornar un objeto de tipo `engine.core.RawDocumentData` almacenando el id de este, el título y el texto a indexar. Esta última clase generaliza la representación de un documento sin importar su origen separando así la aplicación de un modelo determinado del formato o fuente de los documentos sobre los que se aplica. Se espera que para cada fuente de documentos se haga un implementación específica y se inyecte dentro de un objeto de tipo `IRS` que representa al sistema y sus componentes

En la implementación actual se utiliza el dataset **Cranfield** para la obtención de documentos, esto está facilitado gracias a el módulo de *Python* `ir_datasets` que posee una interfaz para cargar y leer información de este y otros datasets utilizados para evaluar sistemas de recuperación de información. La implementación específica de `RawDataGetter` llamada `engine.cranfield.CranfieldGetter` se sirve de utilidades de este módulo para acceder fácilmente a la información de un documento.

### **Procesamiento de documentos**

Dentro de `IRS` cuando se llama a los métodos `add_document` o `add_documents` se comienzan a procesar estos para la incorporación al sistema, el núcleo de este procesamiento se encuentra en la implementación específica de las interfaces `engine.core.IRIndexer` y `engine.core.IRCollection` que contiene el sistema. Las clases que heredan de `IRCollection` se espera que contengan las funcionalidades relacionadas al modelo específico a utilizar mientras que `IRIndexer` define la forma de extraer información de los documentos para que el modelo la utilice. Existe una funcionalidad estándar implementada en `IRIndexer` cuyo algoritmo se basa en extraer cada palabra del texto a indexar de un documento, filtrar eliminando las que se consideren *stopwords* y devolver una lista de estas (en el orden en que aparecen en el documento)

En la implementación específica del modelo vectorial, la clase `engine.vector.VectorIRCollection` hereda de `IRCollection` y esta mantiene un cache de la información extraída de los documentos para evitar sobrecarga al inicializar el sistema. Si el documento no está en la caché esta busca el indexer y *data getter* (implementación de `RawDataGetter`) del sistema que la contiene y lo incorpora a la caché luego de indexarlo y procesar la información. En el modelo vectorial solo se utiliza la frecuencia de los términos en los documentos así que una vez indexado y obtenida la lista de términos del documento se pasa a calcular la frecuencia de cada uno para incorporarlo a la tabla general, la cual se explica a continuación.

### **Representación de los documentos**

En el modelo vectorial los documentos se representan como un vector de dimensión $n$ (cantidad de términos total del sistema) de la forma:

$$\vec{d_j}=(w_{1,j},w_{2,j},...,w_{n,j})$$

Donde $dj$ representa al $j$-ésimo documento y $w_{i,j}$ el peso de el término $i$ en el documento $j$$^{[3]}$. Si se utilizan todos los términos indexados por sistema ($n$) podemos representar los vectoresde $m$ documentos incorporados como una matriz $n \times m$.

Este peso es dependiente de la frecuencia de los términos en los documentos en la implementación actual, la cual usa el cálculo para el peso $tf\times idf$; por tanto esto es lo que guardará `VectorIRCollection`. Para esto se utiliza como tabla de frecuencias un objeto de tipo `DataFrame` de la librería `pandas` almacenando para cada documento en la columna $j$-ésima la cantidad de veces que el término de la fila $i$-ésima se encuentra en este.

Como se decía anteriormente esta tabla de frecuencias es almacenada en un archivo *csv* a modo de caché para disminuir la carga de inicio del sistema.

### **Procesamiento y Representación de la consulta**

Para el procesamiento de la consulta se utiliza un método análogo al indexado de documentos, se obtiene la lista de términos de la consulta y se determina la frecuencia de estos. Esto se realiza a través de la clase `engine.vector.VectorIRQuerifier` que hereda de `engine.core.IRQuerifier`, a través de una interfaz para definir el procesamiento de una cadena de texto (la consulta) a un objeto query entendible por el modelo y la colección del sistema.

La consulta en el modelo vectorial se representa como si fuera un documento extra, de la forma:

$$q=(w_{1,q},w_{2,q},...,w_{n,q})$$

El peso está dado por la fórmula $tf \times idf$ con un factor de suavizado $a=0.5$.

### **Funcionamiento del motor de búsqueda y obtención de resultados**

Cuando se envía una query al sistema es procesada por el objeto `IRQuerifier` de este y luego se utilizan los métodos `get_relevance` o `get_relevances` del objeto `IRCollection` del sistema para obtener la similitud de un documento o de todos los documentos de la colección respectivamente.

El método `get_relevances` de `VectorIRCollection` es el utilizado para realizar una búsqueda general en el sistema y devuelve una lista de IDs de documentos junto a su similitud con la consulta ordenados de mayor a menor por su relevancia, esta lista es filtrada eliminando los que tienen relevancia negativa y el resto es el ranking devuelto como resultado de la búsqueda.

El motor de búsqueda está pensado para utilizarse como un servicio web con una interfaz independiente a este que fácilmente pueda ser utilizado desde cualquier plataforma. Al implementar este a través de una API RESTful se asegura esta capacidad. La API cuenta con un único *endpoint* de ruta `/search` con parámetros posibles: `q` (texto de la query), `page` (número de la página de los resultados) y `pagesize` (el tamaño de esta página)

## Conclusiones

El presente proyecto es aunque básico completamente funcional y puede fácilmente adaptarse a cualquier dataset (e incluso modelo gracias a la arquitectura definida). Como meta más próxima está la implementación de sistemas de evaluación que permitan ir perfeccionando el funcionamiento de este.

## Referencias
1. Singh V, Singh V. Vector space model: an information retrieval system. 2022 Jul. 

2. Raghavan VV, Wong SKM. A critical analysis of vector space model for information retrieval. Journal of the American Society for Information Science. 1986;37(5):279–87. 
 
3. Vector space model. Wikipedia [Internet]. 2022 [citado 2022 Nov 15]. URL: https://en.wikipedia.org/w/index.php?title=Vector_space_model&oldid=1117228225
