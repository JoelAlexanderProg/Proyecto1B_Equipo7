# Catálogo de casos de prueba

Cada caso `CT-XX.Y` verifica el criterio de aceptación `CA-XX.Y` de las [historias de usuario](../01-requisitos/historias-usuario.md). Un caso puede ejecutarse con varias pruebas automatizadas de distinto nivel; los casos `CT-M` son manuales y su procedimiento está en [ejecución](ejecucion.md#casos-manuales).

## HU-01 · Consultar el menú

| Caso | Técnica | Nivel | Prueba | Resultado |
|---|---|---|---|---|
| CT-01.1 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_menu_publico_muestra_precios_y_disponibilidad` | ✅ Aprobado |
| CT-01.1 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_semilla_carga_el_menu_una_sola_vez` | ✅ Aprobado |
| CT-01.2 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_registro_inicia_sesion_y_muestra_codigo_de_cliente` | ✅ Aprobado |
| CT-01.2 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_menu_solo_disponibles_excluye_no_disponibles` | ✅ Aprobado |
| CT-01.3 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_api_de_productos_y_healthcheck` | ✅ Aprobado |
| CT-01.3 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_api_inexistente_responde_json` | ✅ Aprobado |

## HU-02 · Armar el pedido

| Caso | Técnica | Nivel | Prueba | Resultado |
|---|---|---|---|---|
| CT-02.1 | Escenario del criterio | Unitaria | `unit/test_pedido.py::test_pedido_sin_productos_no_se_confirma` | ✅ Aprobado |
| CT-02.1 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_revisar_sin_productos_no_continua` | ✅ Aprobado |
| CT-02.2 | Partición de equivalencia y valores límite | Unitaria | `unit/test_pedido.py::test_cantidad_no_entera_positiva_se_rechaza` (6 variantes) | ✅ Aprobado |
| CT-02.2 | Partición de equivalencia y valores límite | Unitaria | `unit/test_pedido.py::test_cantidades_limite_validas_se_aceptan` (2 variantes) | ✅ Aprobado |
| CT-02.2 | Partición de equivalencia y valores límite | Unitaria | `unit/test_pedido.py::test_cantidad_mayor_al_maximo_se_rechaza` | ✅ Aprobado |
| CT-02.2 | Partición de equivalencia y valores límite | Sistema | `sistema/test_web_cliente.py::test_revisar_rechaza_cantidades_no_validas` | ✅ Aprobado |
| CT-02.3 | Escenario del criterio | Unitaria | `unit/test_pedido.py::test_producto_no_disponible_no_se_puede_pedir` | ✅ Aprobado |
| CT-02.3 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_producto_no_disponible_no_se_confirma` | ✅ Aprobado |
| CT-02.3 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_producto_inexistente_no_se_confirma` | ✅ Aprobado |
| CT-02.3 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_revisar_rechaza_producto_no_disponible` | ✅ Aprobado |
| CT-02.4 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_revisar_sin_sesion_redirige_al_ingreso` | ✅ Aprobado |
| CT-02.4 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_rutas_del_cliente_exigen_sesion` | ✅ Aprobado |

## HU-03 · Conocer el total antes de confirmar

| Caso | Técnica | Nivel | Prueba | Resultado |
|---|---|---|---|---|
| CT-03.1 | Escenario del criterio | Unitaria | `unit/test_pedido.py::test_total_es_la_suma_de_precio_por_cantidad` | ✅ Aprobado |
| CT-03.1 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_revisar_calcula_total_sin_guardar` | ✅ Aprobado |
| CT-03.1 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_recorrido_completo_hasta_el_codigo_de_retiro` | ✅ Aprobado |
| CT-03.2 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_cambio_de_precio_antes_de_confirmar_muestra_el_nuevo_total` | ✅ Aprobado |
| CT-03.2 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_total_revisado_alterado_no_confirma` | ✅ Aprobado |
| CT-03.3 | Revisión manual | Manual | [CT-M01](ejecucion.md#ct-m01) | Ver ejecución |

## HU-04 · Confirmar el pedido y recibir el código de retiro

| Caso | Técnica | Nivel | Prueba | Resultado |
|---|---|---|---|---|
| CT-04.1 | Escenario del criterio | Unitaria | `unit/test_pedido.py::test_pedido_confirmado_inicia_pendiente` | ✅ Aprobado |
| CT-04.1 | Escenario del criterio | Unitaria | `unit/test_codigo_y_validaciones.py::test_codigo_generado_tiene_formato_y_alfabeto_sin_ambiguos` | ✅ Aprobado |
| CT-04.1 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_confirmar_pedido_persiste_pendiente_con_codigo` | ✅ Aprobado |
| CT-04.2 | Escenario del criterio | Unitaria | `unit/test_codigo_y_validaciones.py::test_codigos_generados_no_se_repiten_en_una_muestra` | ✅ Aprobado |
| CT-04.2 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_codigo_duplicado_se_regenera` | ✅ Aprobado |
| CT-04.3 | Escenario del criterio | Unitaria | `unit/test_pedido.py::test_precio_del_detalle_no_cambia_al_modificar_el_menu` | ✅ Aprobado |
| CT-04.3 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_precio_del_pedido_guardado_no_cambia_con_el_menu` | ✅ Aprobado |
| CT-04.4 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_producto_agotado_antes_de_confirmar_no_se_confirma` | ✅ Aprobado |

## HU-05 · Consultar el estado de mis pedidos

| Caso | Técnica | Nivel | Prueba | Resultado |
|---|---|---|---|---|
| CT-05.1 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_recorrido_completo_hasta_el_codigo_de_retiro` | ✅ Aprobado |
| CT-05.1 | Escenario del criterio | Sistema | `sistema/test_web_personal.py::test_flujo_de_preparacion_y_entrega` | ✅ Aprobado |
| CT-05.2 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_recorrido_completo_hasta_el_codigo_de_retiro` | ✅ Aprobado |
| CT-05.3 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_un_cliente_no_ve_el_pedido_de_otro` | ✅ Aprobado |
| CT-05.3 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_pedido_inexistente_responde_404` | ✅ Aprobado |
| CT-05.3 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_pagina_inexistente_muestra_error_amigable` | ✅ Aprobado |

## HU-06 · Registrarme e ingresar

| Caso | Técnica | Nivel | Prueba | Resultado |
|---|---|---|---|---|
| CT-06.1 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_registro_asigna_codigo_de_cliente` | ✅ Aprobado |
| CT-06.1 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_registro_inicia_sesion_y_muestra_codigo_de_cliente` | ✅ Aprobado |
| CT-06.2 | Partición de equivalencia | Unitaria | `unit/test_codigo_y_validaciones.py::test_cedula_valida` (2 variantes) | ✅ Aprobado |
| CT-06.2 | Partición de equivalencia | Unitaria | `unit/test_codigo_y_validaciones.py::test_cedula_invalida` (5 variantes) | ✅ Aprobado |
| CT-06.2 | Partición de equivalencia | Unitaria | `unit/test_codigo_y_validaciones.py::test_celular_valido_se_normaliza` | ✅ Aprobado |
| CT-06.2 | Partición de equivalencia | Unitaria | `unit/test_codigo_y_validaciones.py::test_celular_invalido` (3 variantes) | ✅ Aprobado |
| CT-06.2 | Partición de equivalencia | Unitaria | `unit/test_codigo_y_validaciones.py::test_correo_institucional_valido` | ✅ Aprobado |
| CT-06.2 | Partición de equivalencia | Unitaria | `unit/test_codigo_y_validaciones.py::test_correo_no_institucional_se_rechaza` (4 variantes) | ✅ Aprobado |
| CT-06.2 | Partición de equivalencia | Unitaria | `unit/test_codigo_y_validaciones.py::test_nombre_invalido` (4 variantes) | ✅ Aprobado |
| CT-06.2 | Partición de equivalencia | Sistema | `sistema/test_web_cliente.py::test_registro_con_cedula_invalida_muestra_el_motivo` | ✅ Aprobado |
| CT-06.3 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_cliente_duplicado_se_rechaza` (2 variantes) | ✅ Aprobado |
| CT-06.3 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_registro_duplicado_muestra_el_motivo` | ✅ Aprobado |
| CT-06.4 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_identificar_cliente` | ✅ Aprobado |
| CT-06.4 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_ingreso_con_correo_y_cedula` | ✅ Aprobado |
| CT-06.4 | Escenario del criterio | Sistema | `sistema/test_web_cliente.py::test_salir_cierra_la_sesion` | ✅ Aprobado |

## HU-07 · Mantener el menú

| Caso | Técnica | Nivel | Prueba | Resultado |
|---|---|---|---|---|
| CT-07.1 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_codigos_de_producto_por_categoria` | ✅ Aprobado |
| CT-07.1 | Escenario del criterio | Sistema | `sistema/test_web_personal.py::test_agregar_producto_valida_y_asigna_codigo` | ✅ Aprobado |
| CT-07.2 | Partición de equivalencia y valores límite | Unitaria | `unit/test_pedido.py::test_precio_valido_se_normaliza` (3 variantes) | ✅ Aprobado |
| CT-07.2 | Partición de equivalencia y valores límite | Unitaria | `unit/test_pedido.py::test_precio_invalido_se_rechaza` (6 variantes) | ✅ Aprobado |
| CT-07.2 | Partición de equivalencia y valores límite | Sistema | `sistema/test_web_personal.py::test_agregar_producto_valida_y_asigna_codigo` | ✅ Aprobado |
| CT-07.2 | Partición de equivalencia y valores límite | Sistema | `sistema/test_web_personal.py::test_editar_con_datos_invalidos_no_guarda` | ✅ Aprobado |
| CT-07.3 | Escenario del criterio | Sistema | `sistema/test_web_personal.py::test_formulario_de_edicion_muestra_los_datos` | ✅ Aprobado |
| CT-07.3 | Escenario del criterio | Sistema | `sistema/test_web_personal.py::test_editar_precio_no_cambia_pedidos_confirmados` | ✅ Aprobado |
| CT-07.4 | Escenario del criterio | Sistema | `sistema/test_web_personal.py::test_cambiar_disponibilidad_se_refleja_en_el_menu` | ✅ Aprobado |
| CT-07.4 | Escenario del criterio | Sistema | `sistema/test_web_personal.py::test_editar_producto_inexistente_responde_404` | ✅ Aprobado |

## HU-08 · Ver los pedidos por estado

| Caso | Técnica | Nivel | Prueba | Resultado |
|---|---|---|---|---|
| CT-08.1 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_flujo_de_preparacion_y_entrega` | ✅ Aprobado |
| CT-08.1 | Escenario del criterio | Sistema | `sistema/test_web_personal.py::test_flujo_de_preparacion_y_entrega` | ✅ Aprobado |
| CT-08.2 | Escenario del criterio | Sistema | `sistema/test_web_personal.py::test_tablero_ordena_del_mas_antiguo_al_mas_reciente` | ✅ Aprobado |
| CT-08.3 | Revisión manual | Manual | [CT-M05](ejecucion.md#ct-m05) | Ver ejecución |

## HU-09 · Registrar el avance de un pedido

| Caso | Técnica | Nivel | Prueba | Resultado |
|---|---|---|---|---|
| CT-09.1 | Transición de estados | Unitaria | `unit/test_pedido.py::test_pedido_avanza_en_orden` | ✅ Aprobado |
| CT-09.1 | Transición de estados | Sistema | `sistema/test_web_personal.py::test_flujo_de_preparacion_y_entrega` | ✅ Aprobado |
| CT-09.2 | Transición de estados | Unitaria | `unit/test_pedido.py::test_listo_no_avanza_sin_codigo` | ✅ Aprobado |
| CT-09.2 | Transición de estados | Unitaria | `unit/test_pedido.py::test_entregado_no_puede_cambiar` | ✅ Aprobado |
| CT-09.2 | Transición de estados | Sistema | `sistema/test_web_personal.py::test_listo_no_avanza_sin_codigo` | ✅ Aprobado |
| CT-09.2 | Transición de estados | Sistema | `sistema/test_web_personal.py::test_pedido_inexistente_en_el_tablero` | ✅ Aprobado |
| CT-09.3 | Concurrencia (escenario) | Integración | `integracion/test_servicios.py::test_cambio_simultaneo_de_estado_se_detecta` | ✅ Aprobado |

## HU-10 · Entregar el pedido verificando el código

| Caso | Técnica | Nivel | Prueba | Resultado |
|---|---|---|---|---|
| CT-10.1 | Tabla de decisión (estado × código) | Unitaria | `unit/test_pedido.py::test_se_entrega_con_codigo_correcto` (3 variantes) | ✅ Aprobado |
| CT-10.1 | Tabla de decisión (estado × código) | Unitaria | `unit/test_codigo_y_validaciones.py::test_normalizar_codigo` (3 variantes) | ✅ Aprobado |
| CT-10.1 | Tabla de decisión (estado × código) | Integración | `integracion/test_servicios.py::test_flujo_de_preparacion_y_entrega` | ✅ Aprobado |
| CT-10.1 | Tabla de decisión (estado × código) | Sistema | `sistema/test_web_personal.py::test_flujo_de_preparacion_y_entrega` | ✅ Aprobado |
| CT-10.2 | Tabla de decisión (estado × código) | Unitaria | `unit/test_pedido.py::test_no_se_entrega_con_codigo_incorrecto` | ✅ Aprobado |
| CT-10.2 | Tabla de decisión (estado × código) | Sistema | `sistema/test_web_personal.py::test_flujo_de_preparacion_y_entrega` | ✅ Aprobado |
| CT-10.3 | Tabla de decisión (estado × código) | Unitaria | `unit/test_pedido.py::test_no_se_entrega_si_no_esta_listo` (2 variantes) | ✅ Aprobado |
| CT-10.3 | Tabla de decisión (estado × código) | Sistema | `sistema/test_web_personal.py::test_pendiente_no_se_puede_entregar` | ✅ Aprobado |

## HU-11 · Ingresar como personal

| Caso | Técnica | Nivel | Prueba | Resultado |
|---|---|---|---|---|
| CT-11.1 | Escenario del criterio | Integración | `integracion/test_servicios.py::test_acceso_del_personal` | ✅ Aprobado |
| CT-11.1 | Escenario del criterio | Sistema | `sistema/test_web_personal.py::test_ingreso_con_clave_incorrecta` | ✅ Aprobado |
| CT-11.2 | Escenario del criterio | Sistema | `sistema/test_web_personal.py::test_tablero_exige_ingreso_del_personal` | ✅ Aprobado |
| CT-11.2 | Escenario del criterio | Sistema | `sistema/test_web_personal.py::test_acciones_del_personal_exigen_sesion` | ✅ Aprobado |
| CT-11.2 | Escenario del criterio | Sistema | `sistema/test_web_personal.py::test_salir_del_personal` | ✅ Aprobado |
| CT-11.3 | Escenario del criterio | Unitaria | `unit/test_config.py::test_clave_del_personal_es_obligatoria` | ✅ Aprobado |
| CT-11.3 | Escenario del criterio | Unitaria | `unit/test_config.py::test_valores_por_defecto_y_personalizados` | ✅ Aprobado |
| CT-11.3 | Escenario del criterio | Unitaria | `unit/test_config.py::test_cargar_archivo_env_no_sobrescribe` | ✅ Aprobado |

## Requisitos no funcionales

| Requisito | Verificación |
|---|---|
| RNF-01 · Persistencia | `integracion/test_servicios.py::test_los_datos_persisten_entre_ejecuciones`; [CT-M04](ejecucion.md#ct-m04) |
| RNF-02 · Uso desde el celular | [CT-M01](ejecucion.md#ct-m01) |
| RNF-03 · Instalación con un comando | [CT-M03](ejecucion.md#ct-m03) |
| RNF-04 · Calidad del código | [CT-M06](ejecucion.md#ct-m06) |
| RNF-05 · Credenciales fuera del código | `unit/test_config.py::test_clave_del_personal_es_obligatoria` |
| RNF-06 · Estados reconocibles | [CT-M01](ejecucion.md#ct-m01); [CT-M02](ejecucion.md#ct-m02) |
| RNF-07 · Disponibilidad observable | `sistema/test_web_cliente.py::test_api_de_productos_y_healthcheck`; `sistema/test_web_cliente.py::test_fuentes_se_sirven_con_su_tipo`; [CT-M03](ejecucion.md#ct-m03) |

## Casos manuales

| Caso | Nombre | Verifica |
|---|---|---|
| [CT-M01](ejecucion.md#ct-m01) | Revisión visual del cliente a 390 px | CA-03.3, RNF-02, RNF-06 |
| [CT-M02](ejecucion.md#ct-m02) | Revisión visual del tablero a 1280 px | CA-08.1, CA-10.2, RNF-06 |
| [CT-M03](ejecucion.md#ct-m03) | Instalación y salud del contenedor | RNF-03, RNF-07 |
| [CT-M04](ejecucion.md#ct-m04) | Persistencia en el volumen de Docker | RNF-01 |
| [CT-M05](ejecucion.md#ct-m05) | Recarga del tablero sin perder lo escrito | CA-08.3 |
| [CT-M06](ejecucion.md#ct-m06) | Análisis estático y cobertura | RNF-04 |
