from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import pandas as pd
import random
from datetime import date, timedelta, datetime

# Lista de personas disponibles
personas = ['Ana Luisa', 'Obed', 'Paulette', 'Atenea', 'Fernanda', 'Analy', 'Pedro', 'Alan', 'Daniela', 'Nacho', 'Daniel']

# Colores por día de servicio
colores_dias = {
    'Martes': colors.HexColor("#FFDDC1"),
    'Viernes': colors.HexColor("#C1FFD7"),
    'Domingo 9:00 AM': colors.HexColor("#C1D9FF"),
    'Domingo 11:00 AM': colors.HexColor("#D9C1FF"),
    'Domingo 1:00 PM': colors.HexColor("#FFC1D9")
}

# Días y horarios de servicio
dias_servicio = {
    'Martes': ['7:00 PM'],
    'Viernes': ['7:00 PM'],
    'Domingo': ['9:00 AM', '11:00 AM', '1:00 PM']
}

def generar_fechas(mes, año):
    fechas = []
    fecha_actual = date(año, mes, 1)
    while fecha_actual.month == mes:
        if fecha_actual.strftime('%A') in ['Tuesday', 'Friday', 'Sunday']:
            fechas.append(fecha_actual)
        fecha_actual += timedelta(days=1)
    return fechas

def asignar_roles(fechas, agregar_uno_domingo=True):
    rol_data = []
    
    # Organizar las fechas por semana
    fechas_por_semana = {}
    for fecha in fechas:
        semana = fecha.isocalendar()[1]
        if semana not in fechas_por_semana:
            fechas_por_semana[semana] = []
        fechas_por_semana[semana].append(fecha)
    
    for semana in fechas_por_semana:
        fechas_por_semana[semana].sort()
    
    ultima_fecha_servicio = {persona: None for persona in personas}
    # Diccionario para rastrear servicios por persona, semana y tipo de servicio
    servicios_por_persona_semana = {persona: {} for persona in personas}
    
    for semana, fechas_semana in sorted(fechas_por_semana.items()):
        personas_por_dia = {}
        
        for fecha in fechas_semana:
            fecha_str = fecha.strftime('%Y-%m-%d')
            dia_semana = fecha.strftime('%A')
            dia_clave = {'Tuesday': 'Martes', 'Friday': 'Viernes', 'Sunday': 'Domingo'}[dia_semana]
            horarios = dias_servicio[dia_clave]
            
            personas_por_dia[fecha_str] = []
            
            for hora in horarios:
                clave_servicio = f"{dia_clave} {hora}" if dia_clave == 'Domingo' else dia_clave
                
                excluidos = personas_por_dia[fecha_str].copy()
                # Excluir a Daniela los viernes
                if dia_clave == 'Viernes':
                    if 'Daniela' not in excluidos:
                        excluidos.append('Daniela')
                # Excluir por días consecutivos (3 días de separación)
                for persona, ultima_fecha in ultima_fecha_servicio.items():
                    if ultima_fecha is not None:
                        if (fecha - ultima_fecha).days <= 3:
                            if persona not in excluidos:
                                excluidos.append(persona)
                
                # Excluir a Fernanda, Obed y Pedro los domingos a la 1 PM
                if dia_clave == 'Domingo' and hora == '1:00 PM':
                    for persona in ['Fernanda', 'Obed', 'Pedro']:
                        if persona not in excluidos:
                            excluidos.append(persona)
                
                # Excluir personas que sirvieron en el mismo servicio la semana anterior
                semana_anterior = semana - 1
                for persona in personas:
                    if persona in servicios_por_persona_semana and semana_anterior in servicios_por_persona_semana[persona]:
                        if clave_servicio in servicios_por_persona_semana[persona][semana_anterior]:
                            if persona not in excluidos:
                                excluidos.append(persona)
                
                disponibles = [p for p in personas if p not in excluidos]
                
                if len(disponibles) < 3:
                    excluidos = personas_por_dia[fecha_str].copy()
                    if dia_clave == 'Domingo' and hora == '1:00 PM':
                        for persona in ['Fernanda', 'Obed', 'Pedro']:
                            if persona not in excluidos:
                                excluidos.append(persona)
                    # Re-checar exclusión por servicio de semana anterior en caso de relajación
                    for persona in personas:
                        if persona in servicios_por_persona_semana and semana_anterior in servicios_por_persona_semana[persona]:
                            if clave_servicio in servicios_por_persona_semana[persona][semana_anterior]:
                                if persona not in excluidos:
                                    excluidos.append(persona)
                    disponibles = [p for p in personas if p not in excluidos]
                
                if dia_clave == 'Domingo' and hora == '1:00 PM' and not agregar_uno_domingo:
                    if disponibles:
                        proyeccion = random.choice(disponibles)
                        disponibles.remove(proyeccion)
                        personas_por_dia[fecha_str].append(proyeccion)
                        ultima_fecha_servicio[proyeccion] = fecha
                        servicios_por_persona_semana[proyeccion].setdefault(semana, []).append(clave_servicio)
                    else:
                        proyeccion = 'Analy'
                        if 'Analy' not in personas_por_dia[fecha_str]:
                            personas_por_dia[fecha_str].append('Analy')
                            ultima_fecha_servicio['Analy'] = fecha
                            servicios_por_persona_semana['Analy'].setdefault(semana, []).append(clave_servicio)
                    transmision = 's/d'
                    camara = 's/d'
                elif dia_clave == 'Domingo' and hora == '1:00 PM':
                    if len(disponibles) >= 3:
                        random.shuffle(disponibles)
                        proyeccion, transmision, camara = disponibles[:3]
                        personas_por_dia[fecha_str].extend([proyeccion, transmision, camara])
                        ultima_fecha_servicio[proyeccion] = fecha
                        ultima_fecha_servicio[transmision] = fecha
                        ultima_fecha_servicio[camara] = fecha
                        servicios_por_persona_semana[proyeccion].setdefault(semana, []).append(clave_servicio)
                        servicios_por_persona_semana[transmision].setdefault(semana, []).append(clave_servicio)
                        servicios_por_persona_semana[camara].setdefault(semana, []).append(clave_servicio)
                    else:
                        proyeccion = 'Analy' if 'Analy' not in excluidos else random.choice(disponibles) if disponibles else 's/d'
                        if proyeccion != 's/d' and proyeccion not in personas_por_dia[fecha_str]:
                            disponibles.remove(proyeccion) if proyeccion in disponibles else None
                            personas_por_dia[fecha_str].append(proyeccion)
                            ultima_fecha_servicio[proyeccion] = fecha
                            servicios_por_persona_semana[proyeccion].setdefault(semana, []).append(clave_servicio)
                        transmision = random.choice(disponibles) if disponibles else 's/d'
                        if transmision != 's/d':
                            disponibles.remove(transmision)
                            personas_por_dia[fecha_str].append(transmision)
                            ultima_fecha_servicio[transmision] = fecha
                            servicios_por_persona_semana[transmision].setdefault(semana, []).append(clave_servicio)
                        camara = random.choice(disponibles) if disponibles else 's/d'
                        if camara != 's/d':
                            personas_por_dia[fecha_str].append(camara)
                            ultima_fecha_servicio[camara] = fecha
                            servicios_por_persona_semana[camara].setdefault(semana, []).append(clave_servicio)
                else:
                    if len(disponibles) >= 3:
                        random.shuffle(disponibles)
                        proyeccion, transmision, camara = disponibles[:3]
                        personas_por_dia[fecha_str].extend([proyeccion, transmision, camara])
                        ultima_fecha_servicio[proyeccion] = fecha
                        ultima_fecha_servicio[transmision] = fecha
                        ultima_fecha_servicio[camara] = fecha
                        servicios_por_persona_semana[proyeccion].setdefault(semana, []).append(clave_servicio)
                        servicios_por_persona_semana[transmision].setdefault(semana, []).append(clave_servicio)
                        servicios_por_persona_semana[camara].setdefault(semana, []).append(clave_servicio)
                    else:
                        proyeccion = random.choice(disponibles) if disponibles else 's/d'
                        if proyeccion != 's/d':
                            disponibles.remove(proyeccion)
                            personas_por_dia[fecha_str].append(proyeccion)
                            ultima_fecha_servicio[proyeccion] = fecha
                            servicios_por_persona_semana[proyeccion].setdefault(semana, []).append(clave_servicio)
                        transmision = random.choice(disponibles) if disponibles else 's/d'
                        if transmision != 's/d':
                            disponibles.remove(transmision)
                            personas_por_dia[fecha_str].append(transmision)
                            ultima_fecha_servicio[transmision] = fecha
                            servicios_por_persona_semana[transmision].setdefault(semana, []).append(clave_servicio)
                        camara = random.choice(disponibles) if disponibles else 's/d'
                        if camara != 's/d':
                            personas_por_dia[fecha_str].append(camara)
                            ultima_fecha_servicio[camara] = fecha
                            servicios_por_persona_semana[camara].setdefault(semana, []).append(clave_servicio)
                
                rol_data.append({
                    'Fecha': fecha.strftime('%d-%m-%Y'),
                    'Día': clave_servicio,
                    'Hora': hora,
                    'Proyección': proyeccion,
                    'Transmisión': transmision,
                    'Cámara': camara
                })
    
    return rol_data

def crear_rol(mes, año, agregar_uno_domingo=True):
    fechas = generar_fechas(mes, año)
    rol = asignar_roles(fechas, agregar_uno_domingo)
    df = pd.DataFrame(rol)
    return df

def generar_pdf(df, mes, año):
    doc = SimpleDocTemplate(f"Rol_Servicio_{mes}_{año}.pdf", pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    nombre_mes = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    elements.append(Paragraph(f"Rol de Servicio - {nombre_mes.get(mes, mes)} {año}", styles['Title']))
    elements.append(Spacer(1, 12))
    
    data = [['Fecha', 'Día', 'Hora', 'Proyección', 'Transmisión', 'Cámara']]
    for _, row in df.iterrows():
        fila = [row['Fecha'], row['Día'], row['Hora'], row['Proyección'], row['Transmisión'], row['Cámara']]
        data.append(fila)
    
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    
    for i, row in enumerate(df.itertuples(), start=1):
        style.add('BACKGROUND', (0, i), (-1, i), colores_dias.get(row.Día, colors.white))
    
    table.setStyle(style)
    elements.append(table)
    
    doc.build(elements)
    print(f"PDF generado: Rol_Servicio_{mes}_{año}.pdf")

def verificar_restricciones(df):
    df['Fecha_obj'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y').dt.date
    
    errores_mismo_dia = 0
    for fecha in df['Fecha_obj'].unique():
        df_dia = df[df['Fecha_obj'] == fecha]
        personas_dia = []
        for _, row in df_dia.iterrows():
            for rol in ['Proyección', 'Transmisión', 'Cámara']:
                if row[rol] != 's/d' and row[rol] in personas_dia:
                    print(f"ERROR MISMO DÍA: {row[rol]} sirve más de una vez el {fecha} - {row['Día']} {row['Hora']}")
                    errores_mismo_dia += 1
                if row[rol] != 's/d':
                    personas_dia.append(row[rol])
    
    errores_dias_consecutivos = 0
    servicios_por_persona = {}
    for _, row in df.iterrows():
        for rol in ['Proyección', 'Transmisión', 'Cámara']:
            if row[rol] != 's/d':
                if row[rol] not in servicios_por_persona:
                    servicios_por_persona[row[rol]] = []
                servicios_por_persona[row[rol]].append((row['Fecha_obj'], row['Día'], row['Hora']))
    
    for persona, servicios in servicios_por_persona.items():
        servicios.sort()
        for i in range(len(servicios) - 1):
            fecha1, dia1, hora1 = servicios[i]
            fecha2, dia2, hora2 = servicios[i + 1]
            if (fecha2 - fecha1).days <= 3:
                print(f"ERROR DÍAS CONSECUTIVOS: {persona} sirve el {fecha1} ({dia1} {hora1}) y luego el {fecha2} ({dia2} {hora2})")
                errores_dias_consecutivos += 1
    
    errores_restriccion_personas = 0
    df_domingos_1pm = df[(df['Día'] == 'Domingo 1:00 PM')]
    personas_excluidas = ['Fernanda', 'Obed', 'Pedro']
    for _, row in df_domingos_1pm.iterrows():
        for rol in ['Proyección', 'Transmisión', 'Cámara']:
            if row[rol] in personas_excluidas:
                print(f"ERROR RESTRICCIÓN: {row[rol]} asignada el {row['Fecha']} domingo 1:00 PM como {rol}")
                errores_restriccion_personas += 1
    
    # Verificar que nadie sirva en el mismo servicio la semana siguiente
    errores_mismo_servicio_semana = 0
    servicios_por_semana_persona = {}
    for _, row in df.iterrows():
        semana = row['Fecha_obj'].isocalendar()[1]
        persona_rol = [(row['Proyección'], 'Proyección'), (row['Transmisión'], 'Transmisión'), (row['Cámara'], 'Cámara')]
        for persona, rol in persona_rol:
            if persona != 's/d':
                if persona not in servicios_por_semana_persona:
                    servicios_por_semana_persona[persona] = {}
                servicios_por_semana_persona[persona].setdefault(semana, []).append(row['Día'])
    
    for persona, semanas in servicios_por_semana_persona.items():
        semanas_ordenadas = sorted(semanas.keys())
        for i in range(len(semanas_ordenadas) - 1):
            semana_actual = semanas_ordenadas[i]
            semana_siguiente = semanas_ordenadas[i + 1]
            if semana_siguiente == semana_actual + 1:  # Verificar solo semanas consecutivas
                servicios_actual = semanas[semana_actual]
                servicios_siguiente = semanas[semana_siguiente]
                for servicio in servicios_actual:
                    if servicio in servicios_siguiente:
                        print(f"ERROR MISMO SERVICIO SEMANA SIGUIENTE: {persona} sirve en {servicio} en la semana {semana_actual} y semana {semana_siguiente}")
                        errores_mismo_servicio_semana += 1
    
    if errores_mismo_dia == 0:
        print("✓ VERIFICACIÓN EXITOSA: Nadie sirve dos veces el mismo día")
    else:
        print(f"✗ VERIFICACIÓN FALLIDA: {errores_mismo_dia} casos de personas sirviendo dos veces el mismo día")
    
    if errores_dias_consecutivos == 0:
        print("✓ VERIFICACIÓN EXITOSA: Nadie sirve en días consecutivos")
    else:
        print(f"✗ VERIFICACIÓN FALLIDA: {errores_dias_consecutivos} casos de personas sirviendo en días consecutivos")
    
    if errores_restriccion_personas == 0:
        print("✓ VERIFICACIÓN EXITOSA: Fernanda, Obed y Pedro no sirven los domingos a la 1 PM")
    else:
        print(f"✗ VERIFICACIÓN FALLIDA: {errores_restriccion_personas} casos donde Fernanda, Obed o Pedro sirven los domingos a la 1 PM")
    
    if errores_mismo_servicio_semana == 0:
        print("✓ VERIFICACIÓN EXITOSA: Nadie sirve en el mismo servicio la semana siguiente")
    else:
        print(f"✗ VERIFICACIÓN FALLIDA: {errores_mismo_servicio_semana} casos donde alguien sirve en el mismo servicio la semana siguiente")
    
    return (errores_mismo_dia + errores_dias_consecutivos + errores_restriccion_personas + errores_mismo_servicio_semana) == 0

# Programa principal
hoy = datetime.now()
mes, año = 5, hoy.year

respuesta = input("¿Desea agregar personas en 'Transmisión' y 'Cámara' los domingos a la 1:00 PM? (s/n): ").lower()
agregar_uno_domingo = respuesta != 'n'

mejor_rol = None
menos_errores = float('inf')

for intento in range(1, 8):
    print(f"\nIntento {intento} de crear rol...")
    rol_mensual = crear_rol(mes, año, agregar_uno_domingo)
    
    rol_mensual.to_csv(f"temp_rol_intento_{intento}.csv", index=False)
    
    df_verificacion = rol_mensual.copy()
    errores = 0
    
    df_verificacion['Fecha_obj'] = pd.to_datetime(df_verificacion['Fecha'], format='%d-%m-%Y').dt.date
    for fecha in df_verificacion['Fecha_obj'].unique():
        df_dia = df_verificacion[df_verificacion['Fecha_obj'] == fecha]
        personas_dia = []
        for _, row in df_dia.iterrows():
            for rol in ['Proyección', 'Transmisión', 'Cámara']:
                if row[rol] != 's/d' and row[rol] in personas_dia:
                    errores += 1
                if row[rol] != 's/d':
                    personas_dia.append(row[rol])
    
    servicios_por_persona = {}
    for _, row in df_verificacion.iterrows():
        for rol in ['Proyección', 'Transmisión', 'Cámara']:
            if row[rol] != 's/d':
                if row[rol] not in servicios_por_persona:
                    servicios_por_persona[row[rol]] = []
                servicios_por_persona[row[rol]].append((row['Fecha_obj'], row['Día'], row['Hora']))
    
    for persona, servicios in servicios_por_persona.items():
        servicios.sort()
        for i in range(len(servicios) - 1):
            fecha1, _, _ = servicios[i]
            fecha2, _, _ = servicios[i + 1]
            if (fecha2 - fecha1).days <= 3:
                errores += 1
    
    df_domingos_1pm = df_verificacion[df_verificacion['Día'] == 'Domingo 1:00 PM']
    for _, row in df_domingos_1pm.iterrows():
        for rol in ['Proyección', 'Transmisión', 'Cámara']:
            if row[rol] in ['Fernanda', 'Obed', 'Pedro']:
                errores += 1
    
    servicios_por_semana_persona = {}
    for _, row in df_verificacion.iterrows():
        semana = row['Fecha_obj'].isocalendar()[1]
        persona_rol = [(row['Proyección'], 'Proyección'), (row['Transmisión'], 'Transmisión'), (row['Cámara'], 'Cámara')]
        for persona, rol in persona_rol:
            if persona != 's/d':
                if persona not in servicios_por_semana_persona:
                    servicios_por_semana_persona[persona] = {}
                servicios_por_semana_persona[persona].setdefault(semana, []).append(row['Día'])
    
    for persona, semanas in servicios_por_semana_persona.items():
        semanas_ordenadas = sorted(semanas.keys())
        for i in range(len(semanas_ordenadas) - 1):
            semana_actual = semanas_ordenadas[i]
            semana_siguiente = semanas_ordenadas[i + 1]
            if semana_siguiente == semana_actual + 1:
                servicios_actual = semanas[semana_actual]
                servicios_siguiente = semanas[semana_siguiente]
                for servicio in servicios_actual:
                    if servicio in servicios_siguiente:
                        errores += 1
    
    print(f"Intento {intento}: {errores} errores encontrados")
    
    if errores < menos_errores:
        menos_errores = errores
        mejor_rol = rol_mensual.copy()
    
    if errores == 0:
        print("¡Encontrado un rol sin errores!")
        break

rol_mensual = mejor_rol

print("\n=== VERIFICACIÓN FINAL ===")
verificar_restricciones(rol_mensual)

generar_pdf(rol_mensual, mes, año)
print("\nROL DE SERVICIO FINAL:")
print(rol_mensual[['Fecha', 'Día', 'Hora', 'Proyección', 'Transmisión', 'Cámara']])