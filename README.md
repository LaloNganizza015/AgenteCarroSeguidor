# AgenteCarroSeguidor
Repositorio donde guardamos los codigos base de "Britney" nuestro proyecto de Apps de Control por IA

## Caracteristicas
Este proyecto consiste en un vehiculo pequeño con las siguientes especificaciones:
### Hardware
- 4 **motoreductores amarillos con llanta** para la movilidad en un terreno semiplano.
- Un sistema de dirección con una **transmisión de cremallera y piñon** impresos en 3D, como actuador un servomotor **SG90**.
- Una **Raspberry Pi 4B** para controlar el vehiculo.
- Un modelo **Pi Camera 2** para visualizar el camino y buscar señales.
- Una **powerbank INIU** para alimentar la raspberry y los demas componentes.
- Hay modulos de puente H **L298N** como intermediarios entre los motores y la raspberry.
- Para alimentar los motores tenemos dos vias alternas seleccionadas por un **interruptor de 3 vias**; la primer via es un conector para conectar un eliminador de       12V, la segunda es la salida de la powerbank de 5V, que pasa por un elevador de voltaje para llegar a los 12V.
- Un **interruptor de dos vias** para controlar el encendido de los motores.
- Consideramos la instalación de dos sensores al frente y atras para evitar colisiones, el frontal es un **sensor de movimiento PIR** para arduino, el trasero es         un ultrasónico **HC SR04**.
- Se considera la implementación de una base para el modulo de cámara, **un mecanismo de 4 barras controlado por un servomotor SG90** para ajustar el ángulo de visión.
  
### Software
- El método de control en la raspberry será una **red neuronal programada en python** que evaluará las señales en el camino para ir modificando el trayecto.
- Estamos proponiendo por el momento dos redes neuronales distintas para evaluar el desempeño de cada una.
- Para controlar la velocidad general del vehiculo en el codigo principal se considera un parámetro al inicio del codigo principal.
- Se considera un control PD para la dirección.
- En el método de entrenamiento de la red neuronal consideramos utilizar el conjunto de datos MNIST localizado en el siguiente link: https://yann.lecun.com/exdb/mnist/

## Funcionamiento
El funcionamiento consiste en lo siguiente:
+ _1.-_ Iniciar la raspberry.
+ _2.-_ Hacer entrenamiento con el procesamiento de imagenes para la toma de decisiones.
+ _3.-_ Iniciar la comunicación con la cámara para ajustar el ángulo mas optimo de visión.
+ _4.-_ Posicionar el vehiculo para que inicie la busqueda de las señales que indican el camino a seguir.
+ _5.-_ Una vez vista la primer señal el vehiculo inicia su movimiento hacia ella, corrigiendo su trayecto con la señal como punto de referencia en caso de empezar         a desviarse.
+ _6.-_ Ya que el vehiculo ha llegado hasta un punto frente a la señal que a percepción de la camara tiene un tamaño de N pixeles llama una función de la red               neuronal para que evalue la señal y emita una indicación, el codigo fuente evalua esa indicación y mueve el vehiculo como debe ser.
+ _7.-_ Cada vez que el vehiculo tome una decisión en base a una señal será tomada una fotografia y se registra la acción en un dataframe exportado a excel para            evaluar las métricas de desempeño.
