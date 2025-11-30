# Microservicio de Compras
Microservicio responsable de la gestión y confirmación de pedidos dentro de una arquitectura distribuida basada en microservicios. Su función principal es coordinar la interacción con los servicios de contenido y pagos, garantizando consistencia en las operaciones y controlando el ciclo de vida de los pedidos.

## Tecnologías y dependencias

* Flask como Framework de desarrollo.
* MariaDB como sistema gestor de bases de datos.
* Keycloak para autenticación y autorización basada en roles.
* Patrón Client–Service para comunicación entre microservicios.
* Circuit Breaker Pattern para tolerancia a fallos en llamadas externas.
* AWS Lambda, integrada mediante un servicio mediador.
* OpenAPI para la documentación formal del API.

## Arquitectura del Microservicio
El microservicio está implementado mediante una arquitectura en capas, proporcionando separación de responsabilidades, mantenibilidad y control estructurado del flujo interno.

### Capa de Datos

Interactúa directamente con MariaDB.
Gestiona lectura, escritura y conexión a la base de datos.

### Capa de Persistencia (DAO / ORM)

Encapsula las operaciones CRUD y abstrae la tecnología de almacenamiento.
Permite un acceso a datos desacoplado y consistente.

### Capa de Servicio

Contiene la lógica de negocio principal.
Gestiona validaciones, coordinación entre capas y comunicación con microservicios externos.

### Capa de Controlador

Define los endpoints expuestos.
Incluye validación de token y rol mediante anotaciones asociadas al cliente Keycloak.
Evita la ejecución de la lógica interna si la petición no cumple los requisitos de acceso.

## Comunicación entre Microservicios
La interacción sigue el patrón Client–Service, donde este microservicio actúa tanto como servidor (prestando sus propios endpoints) como cliente de otros microservicios críticos:

* Microservicio de contenido
* Microservicio de pagos

Las llamadas externas están protegidas mediante Circuit Breaker, evitando fallos en cascada y controlando la disponibilidad de servicios externos.

## Integración con AWS Lambda
Uno de los endpoints expuestos en la capa de controlador requiere invocar una función AWS Lambda.
Por motivos de seguridad y arquitectura, la comunicación no se realiza de manera directa:
se utiliza un servicio mediador, encargado de recibir los datos del microservicio, trasladarlos a la función Lambda y retornar la respuesta generada.

## Endpoint destacado: ``/confirm``
El endpoint confirm gestiona el proceso de confirmación de pedidos y concentra la lógica más compleja del microservicio.
El flujo previsto es:

1. Recepción de la solicitud de confirmación.

2. Consulta al microservicio de contenido para verificar disponibilidad de stock.

3. Actualización lógica del stock (decremento temporal).

4. Notificación al microservicio de pagos para iniciar la transacción.

5. Gestión del resultado (confirmación definitiva o restauración del stock en caso de fallo).

Debido al nivel de dependencia con otros microservicios, solo se ha implementado completamente la primera parte de la lógica (pasos 1, 2 y 3), quedando pendiente la integración operativa con el proceso de pago.

# Estado del Proyecto
Este repositorio refleja la implementación funcional del microservicio de compras, incluyendo la capa de seguridad, la arquitectura base y los servicios internos asociados.
El flujo completo del endpoint `confirm` se encuentra parcialmente implementado, documentado y preparado para su finalización en futuras iteraciones.
