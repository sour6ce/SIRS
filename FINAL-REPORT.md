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
      - [¿Cómo se define el *dataset* usado por sistema?](#cómo-se-define-el-dataset-usado-por-sistema)
      - [¿Cómo incorporar un nuevo modelo al sistema?](#cómo-incorporar-un-nuevo-modelo-al-sistema)
  - [Evaluación y Análisis](#evaluación-y-análisis)
  - [Proyección de desarrollo](#proyección-de-desarrollo)
  - [Conclusiones](#conclusiones)

---

## Introducción

En este trabajo se desea implementar un sistema que agrupe distintos subsistemas de recuperación de información. Todos bajo un mismo servicio central y cada uno de ellos con su propio modelo y peculiaridades.

## Modelos Implementados

Basado en lo estudiado durante el curso, en el contenido de la bibliografía fundamental para la asignatura$^{[1]}$ y en los requerimientos dados en la orientación se decidieron implementar los siguientes modelos:
+ Modelo Vectorial.
+ Modelo Booleano.
+ Modelo de Semántica Latente.

El modelo vectorial es un modelo clásico que se conoce que da por lo general muy buenos resultados a pesar de su simplicidad, por eso era una elección obvia su implementación.

El modelo booleano presenta ciertas características que permiten a un usuario más preparado ajustar las consultas al sistema para recuperar información de manera más exacta. En *datasets* como Cranfield puede ser de gran utilidad este modelo.

Derivado del modelo vectorial, el modelo de semántica latente (**LSI**) al reducir la dimension del espacio de los vectores de los documentos del modelo vectorial permite encontrar conceptos que pueden estar "latentes" y relacionar sinónimos o palabras que se usan en el mismo contexto como por ejemplo "*wing*" con "*aeronautic*".

## Arquitectura General

Como se decía anteriormente este sistema está conformado de una serie de subsistema destinados a implementaciones de modelos distintos. Cada uno de estos subsistemas se considera un SRI independiente aunque en la práctica no es así ya que funcionan sobre el mismo *dataset* y sobre un mismo caché con información de la frecuencia de los términos en los documentos. Esto último es posible ya que los tres modelos implementados se basan en esta información para calcular la relevancia de los documentos respecto a una consulta.

Cada subsistema es una clase que hereda de `engine.core.IRS` y contiene 4 componentes principales:
+ `querifier` (Tipo: `engine.core.IRQuerifier`): es un objeto que se encarga de recibir una consulta en texto plano y transformarla en un objeto que el sistema pueda procesar para calcular su relevancia. Se espera que cada modelo implemente el suyo propio según las características de este.
+ `collection` (Tipo: `engine.core.IRCollection`): es el objeto central de un SRI encargado de llevar la información de los modelos indexados y de, dado un objeto consulta válido, obtener la relevancia de cada uno de estos con respecto a esa consulta.
+ `indexer` (Tipo: `engine.core.IRIndexer`): su función es dado un documento de tipo `engine.core.RawDocumentData` extraer la secuencia de tokens a indexar. Su tipo base incorpora ya una implementación básica de este proceso en el cual se extraen palabras en el orden en que aparecen y se eliminan las *stopwords* ([ver más adelante](#eliminación-de-stopwords)).
+ `data_getter` (Tipo: `engine.core.RawDataGetter`): a diferencia de los anteriores el comportamiento de este objeto no depende del modelo que implementa el subsistema sino del *dataset* que se esté usando ya que implementa funciones para extraer documentos de este. Es por esto que mientras los componentes anteriores están pensados para definirse y ser instanciados junto al SRI este lo establece la aplicación según el *dataset* en uso. 

### Modelo Vectorial

El `querifier` del modelo vectorial recibe la consulta, la envía al `indexer` para obtener la lista de palabras y luego transforma esta en un diccionario donde la llave es el término y el valor la frecuencia.

En este modelo se utiliza una tabla dispersa para saber la frecuencia de los términos en los documentos, un diccionario de diccionarios donde las combinaciones de llaves que no existen es porque los términos no se encuentran en el documento.

El cálculo de la relevancia en el objeto `collection` se basa en la fórmula $tf \times idf$ y se sustituye la frecuencia de los términos por el peso obtenido por este cálculo, de igual manera la consulta se utiliza la misma fórmula con un factor de suavizado $a$ de $0.5$. Algunos de los valores de la fórmula están previamente calculados para acelerar el proceso.

Teniendo los pesos en lugar de las frecuencias se pasa entonces a calcular el ángulo entre vectores. Esto se hace dividiendo la sumatoria de los pesos de los términos en común entre la query y la consulta multiplicados, sobre la multiplicación de la norma de ambos. La norma se calcula sumando los cuadrados de todos los términos en la query o el documento para calcular la norma de la query o el documento respectivamente y luego se halla la raíz cuadrada de estos.

### Modelo Booleano

El `querifier` del modelo booleano intenta leer una expresión booleana, es decir una serie de operaciones AND (operador &), OR (operador |) o NEG (operador ~). Cada término que aparece en la expresión es un predicado que es verdadero si el término está en el documento. Además en la expresión se permiten paréntesis para agrupar y se consideran los términos uno a continuación del otro como si estuvieran bajo una operación AND.

El formato de esta consulta te permite alcanzar un nivel de precisión en la consulta muy alto según el conocimiento del usuario. Por ejemplo un usuario con experiencia podría saber que al buscar por un término *"a"* se recuperan muchos términos con documento *"b"* que no son los que se desean, entonces una consulta *"a & ~b"* daría muy buenos resultados.

Para que el sistema entienda estas expresiones booleanas se *parsean* con un parser LL(1) y se utilizan los nodos de expresiones booleanas de la librería sympy. Una vez se tiene la expresión esta se reduce a una forma normal disyuntiva, es decir una serie de consultas de solo operaciones AND y NEG simples unidas por operaciones OR.

Una vez se tiene esta información la relevancia en el objeto `collection` se define de la siguiente forma:

    Un documento es relevante o tiene relevancia 1 si al menos una de las consultas de solo AND se satisface para ese documento.
  
De esta forma, se comprueba con cada consulta de solo AND si los términos que deben aparecer están y los que no no aparecen. Si el documento se satisface con alguna su relevancia será uno, sino cero.

### Modelo de Semántica Latente

El `querifier` es exactamente el mismo del modelo vectorial.

Este modelo tiene como base una matriz $\Alpha$ de términos $W_{i,j}$ donde $W_{i,j}$ es la cantidad de veces que aparece el termino $i$ en el documento $j$ y  se basa en la reducción de la dimension del espacio vectorial que contiene a los vectores de consultas y documentos.

La matriz $\Alpha$ se descompone de la forma $\Alpha = U \cdot S \cdot V^{T}$ usando el algoritmo SVD y se truncan las matrices $U$ y $V$ dejando solo k columnas (k es un numero arbitrario que según nuestras investigaciones suele situarse alrededor de 100). Luego se procede a recalcular los vectores de documentos y la consulta ajustándolos a la nueva dimension del espacio (k).

Luego de realizar este proceso el modelo se comporta nuevamente como un modelo vectorial esta vez calculando la similitud según la fórmula original a partir de los vectores.

$$sim(q_{k},d_{ki})=\frac{ q_{k} \cdot d_{ki} }{ |q_{k}| |d_{ki}| }$$

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

La especificación de esta API REST en el formato standard de OpenAPI se encuentra en el archivo `openapi.json`.

### Interfaz Web

La interfaz web propuesta para el uso de esta aplicación como usuario final dispone de una pantalla principal en la que se escoge el subsistema/modelo sobre el que realizar la búsqueda junto a instrucciones de como se usa.

Cada uno de estos subsistemas tiene una página distinta con una barra donde se escribe la consulta con un botón para iniciar esta a la derecha. Una vez el sistema tiene listo el ranking de documentos se muestran los 10 primeros resultados con posibilidad de mostrar más si es necesario.

Además de un link a la página inicio, en la barra de navegación del sitio hay un link hacia el código fuente de la aplicación.

### Arquitectura dirigida a la extensibilidad

Esta aplicación está pensada para implementar varios modelos sobre un único `dataset`. De esta forma se asegura un sistema semi-portable en el que se pueden incluir múltiples modelos y adaptarlo en pocas líneas a cualquier *dataset* sobre el que se quiera utilizar.

#### ¿Cómo se define el *dataset* usado por sistema?

En el archivo `main.py` junto a otras configuraciones se encuentra la configuración del *dataset* en el que se encuentra actualmente lo siguiente:
```py
DATASET = {
  'name': 'Cranfield',
  'slug': 'cranfield',
  'getter': CranfieldGetter,
  'qrels': CranfieldQrelsGetter
}
```
Para utilizar otra base de datos es necesario cambiar estos datos. 

`getter` almacena el tipo derivado de `engine.core.RawDataGetter` que se debe utilizar para obtener los documentos de ese *dataset*.

+ Los tipos derivados deben implementar dos métodos:
  + `getdata(self, doc: DOCID) -> RawDocumentData`: a partir del string utilizado como id de documento devuelve la información de id, título y texto de este.
  + `getall(self) -> List[DOCID]`: devuelve una lista de todos los ids de todos los documentos del *dataset*.

`qrels` almacena el tipo derivado de `engine.metrics.qrel.QrelGetter` que se debe utilizar para obtener las consultas de prueba de ese *datasets*. Esta clase solo implementa el método `getqrels(self) -> List[Qrel]` que debe devolver una lista de objetos correspondientes a consultas de prueba de ese *dataset*. Estos objetos son derivados del tipo `engine.metrics.qrel.Qrel` cada uno con la siguiente definición:

```py
class Qrel(NamedTuple):
    query_id: str
    query: str
    # Relevancia de un documento con respecto a la consulta
    relevants: Dict[DOCID, float] 

```

Como puede notarse lo que la aplicación considera "*dataset*" es básicamente una abstracción que da acceso a documentos, por tanto si se desean usar varios *datasets* estos pueden adaptarse para que el sistema los reconozca como uno.

#### ¿Cómo incorporar un nuevo modelo al sistema?

Para modificar los modelos del sistema es necesario ir al archivo `main.py` y cambiar la lista de modelos presente en este, en la cual debe encontrarse lo siguiente:

```py
MODELS=[
  Model(
    name='Boolean Model',
    slug='boolean_model',
    type=BooleanIRS,
    dec="...",
    instructions=["Enter a query in the search bar",...]
  ),
  ...
]
```

Al modificar se debe añadir la entrada del nuevo modelo especificando cada campo. `type` guarda una clase derivada de `engine.core.IRS`. Basta en el archivo de configuración importar la definición de este nuevo SRI específico del modelo para poder usarlo. Como se decía anteriormente ([ver arriba](#arquitectura-general)) este objeto debe tener 3 componentes que se esperan definir al crear un nuevo modelo: `querifier`, `collection` y `indexer`, aunque también se pueden utilizar o heredar de los ya definidos para otros modelos.
+ De `querifier` se deben definir los métodos:
  + `querify(self, query: str) -> Any`: método que transforma una consulta en texto plano al formato entendido por el sistema.
  + `get_hash(self) -> str`: devuelve un identificador único de la última consulta sobre la que se llamó a `querify`, esto es utilizado para optimizar la velocidad de respuesta en consultas repetidas.
+ De `collection` se deben definir los métodos:
  +  `add_document(self, document: DOCID) -> None` y `add_documents(self, documents: Iterable[DOCID]) -> None` permiten añadir documentos a la colección a partir del id de estos, la colección es la responsable de revisar el estado de estos y llamar al indexer del irs en el que se encuentra si es necesario. Estos métodos están separados para permitir una optimización al añadir varios documentos a la vez.
  +  `get_relevance(self, query: Any, doc: DOCID) -> float` y `get_relevances(self, query: Any) -> List[Tuple[DOCID, float]]` separados por las mismas razones de la pareja anterior ambos métodos tienen como función calcular la relevancia de los documentos a una consulta.
+ De `indexer` solo es necesario implementar el método `index(self, doc: RawDocumentData) -> INDEX` el cual extrae una lista de palabras en el orden de aparición de un objeto `engine.core.RawDocumentData`.
## Evaluación y Análisis

El *dataset* principal usado para evaluar la aplicación fue *Cranfield* y las consultas de prueba de este. Estas consultas son en lenguaje natural, lo que implica que, por ejemplo, no pueden tomar ventaja de consultas en formato de expresión booleana para el modelo del mismo nombre.

Con cada una de las 225 consultas de prueba se calculó la Precisión, el Recobrado y la Fórmula F1 como medidas de evaluación objetivas y se calculó el tiempo de ejecución y el valor máximo de relevancia de un documento como medidas subjetivas. Esta última de utilidad para calibrar los modelos.

A estos resultados se le hizo un análisis estadístico básico calculando medidas de tendencia central y graficando un histograma de frecuencia. Todo este proceso está recogido en las notebooks adjuntas a este archivo(una para cada modelo)

Para calibrar los resultados de las consultas se utilizó un parámetro en los objetos `engine.core.IRS` llamado `RELEVANCE_FILTER`, una constante que define, una vez calculada la relevancia/similitud de los documentos respecto a una query, los documentos que se deben quedar fuera del ranking, que no son más que aquellos con una similitud igual o menor a este valor.

Aun después de calibrar este parámetro buscando optimizar el valor promedio de la Fórmula F1 o su Cuartil 3, los resultados no son lo suficientemente buenos, por tanto y debido a la cantidad de evaluaciones con valores de Precisión o Recobrado cero se cree que para mejorar la calidad sea necesario utilizar conocimiento *out-of-domain* para fortalecer el sistema.

## Proyección de desarrollo

El proyecto presenta varias vías de desarrollo posible:
+ Solucionar defectos actuales del proyecto.
    + La aplicación actual presenta escalabilidad en memoria pero no en tiempo de ejecución en *datasets* grandes. Una solución propuesta es diseñar la aplicación como un sistema distribuido dividiendo el trabajo en distintas unidades de procesamiento paralelas.
    + No se han aplicado más algoritmos de procesamiento como el stemming. Actualmente esto hace que los modelos vean las palabras *"fluid"* y *"fluids"* como términos distintos, aun cuando representan el mismo contenido.
    + Actualizar la documentación del código, pues esta es escasa y parte de la que existe está obsoleta.
+ Posible implementación de algoritmo de agrupamiento como el k-means dado en clase.
+ Posible implementación de algún método de retroalimentación. Aunque creemos que este es un trabajo que se debe hacer una vez la aplicación se enfoque en un único *dataset* en lugar de buscar una estrategia que funcione en cualquier *dataset* que se utilice.
+ Pulir la aplicación en dirección a experiencia de usuario o a servicio web. Esto se traduce a mejorar el funcionamiento del sitio web básico de la aplicación o el funcionamiento de los endpoints de la API web.
+ Dirigir el producto en función de *datasets* específicos con características específicas, esto permitirá implementar mejoras específicas para los documentos de esos *datasets* y por tanto mejorar los resultados del sistema.

## Conclusiones

Aunque los resultados de las evaluaciones no sean excelentes el presente es un sistema de recuperación de información completamente funcional y útil en la práctica.

Con este proyecto se han aprendido técnicas de la recuperación de información que se esperan que sean de utilidad en la creación de sistemas más complejos.