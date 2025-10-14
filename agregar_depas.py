"""
Generador de Propiedades para Base de Datos PostgreSQL
Genera departamentos realistas para edificios específicos
"""
import asyncio
import asyncpg
from uuid import uuid4
import random
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN - EDITABLE
# ============================================================================

DATABASE_URL = "postgresql://postgres:Dodod.123@34.59.223.136:5432/microservicio_edificio"

EDIFICIOS = [
    {
        "id": "c44298fc-b0b4-483a-8451-c96857d43fc6",
        "nombre": "Edificio Los Pinos",
        "distrito": "San Borja",
        "num_departamentos": 10,
        "num_pisos": 10,
        "año": 2005,
        "area_range": (70, 120),
        "precio_range": (300000, 600000),
    },
    {
        "id": "0628199a-84aa-4324-9999-450f12545cd6",
        "nombre": "Residencial Sol Naciente",
        "distrito": "Miraflores",
        "num_departamentos": 8,
        "num_pisos": 8,
        "año": 2010,
        "area_range": (90, 150),
        "precio_range": (500000, 1000000),
    },
    {
        "id": "11cbe6eb-6c7b-4e9c-af81-42f5b708fb3e",
        "nombre": "Edificio Pacífico",
        "distrito": "Miraflores",
        "num_departamentos": 24,
        "num_pisos": 12,
        "año": 2010,
        "area_range": (60, 120),
        "precio_range": (400000, 1500000),
    },
    {
        "id": "f6f51619-9ee8-4659-a328-4b78c146f530",
        "nombre": "Edificio Solaris",
        "distrito": "San Miguel",
        "num_departamentos": 20,
        "num_pisos": 10,
        "año": 2012,
        "area_range": (50, 110),
        "precio_range": (300000, 1000000),
    },
    {
        "id": "877c0882-c87e-49d1-9dc8-53dc7d5af524",
        "nombre": "Edificio Los Robles",
        "distrito": "Surco",
        "num_departamentos": 30,
        "num_pisos": 15,
        "año": 2015,
        "area_range": (70, 130),
        "precio_range": (450000, 1500000),
    },
    {
        "id": "69939007-1dac-4a94-b95a-98a0d74f06b7",
        "nombre": "Edificio Horizonte",
        "distrito": "Magdalena",
        "num_departamentos": 28,
        "num_pisos": 14,
        "año": 2011,
        "area_range": (100, 180),
        "precio_range": (600000, 1500000),
    },
    {
        "id": "b16139e3-90c4-4b8e-bbd7-8db3d6080c28",
        "nombre": "Edificio Libertad",
        "distrito": "San Borja",
        "num_departamentos": 16,
        "num_pisos": 8,
        "año": 2008,
        "area_range": (50, 100),
        "precio_range": (400000, 900000),
    },
    {
        "id": "10cce8ed-687c-4cd6-aceb-3534eadb9c6e",
        "nombre": "Edificio Altamira",
        "distrito": "Jesús María",
        "num_departamentos": 18,
        "num_pisos": 9,
        "año": 2009,
        "area_range": (60, 120),
        "precio_range": (450000, 900000),
    },
]

# Configuración de generación
SEED = 42  # Para resultados reproducibles
DRY_RUN = False  # True = solo muestra qué haría, no inserta

# ============================================================================
# LÓGICA DE GENERACIÓN
# ============================================================================

def generar_numero_depto(piso: int, index: int) -> str:
    """Genera número de departamento (ej: 301, 302, 501A, 501B)"""
    if index == 0:
        return f"{piso}01"
    elif index == 1:
        return f"{piso}02"
    else:
        # Para múltiples deptos por piso, usar letras
        letra = chr(65 + index)  # A, B, C...
        return f"{piso}01{letra}"


def generar_departamento(edificio: dict, piso: int, index_piso: int) -> dict:
    """Genera un departamento con valores realistas"""
    
    # Calcular factor de piso (pisos altos más caros/grandes)
    factor_piso = piso / edificio["num_pisos"]
    
    # Área (pisos altos +10-20% más grandes)
    area_base = random.uniform(*edificio["area_range"])
    area = round(area_base * (1 + factor_piso * 0.15), 2)
    
    # Dormitorios (basado en área)
    if area < 70:
        dormitorios = random.choice([1, 2])
    elif area < 100:
        dormitorios = random.choice([2, 2, 3])
    elif area < 140:
        dormitorios = random.choice([2, 3, 3])
    else:
        dormitorios = random.choice([3, 3, 4, 4])
    
    # Baños (relacionado con dormitorios)
    if dormitorios == 1:
        banios = 1
    elif dormitorios == 2:
        banios = random.choice([1, 2])
    elif dormitorios == 3:
        banios = random.choice([2, 2, 3])
    else:
        banios = random.choice([2, 3, 3])
    
    # Precio (basado en área y piso)
    precio_base = random.uniform(*edificio["precio_range"])
    precio = round(precio_base * (area / 100) * (1 + factor_piso * 0.2), 2)
    
    # Mantenimiento (0.5% - 1% del valor comercial / 12)
    mantenimiento = round(precio * random.uniform(0.005, 0.01) / 12, 2)
    
    # Features booleanos
    balcon = random.choice([True, False]) if piso > 1 else False
    terraza = True if piso >= edificio["num_pisos"] - 1 else False
    amoblado = random.choice([True, False, False, False])  # 25% amoblado
    permite_mascotas = random.choice([True, True, True, False])  # 75% pet-friendly
    
    # Estado (70% terminado, 20% construcción, 10% planos)
    estado = random.choices(
        ['TERMINADO', 'CONSTRUCCION', 'PLANOS'],
        weights=[70, 20, 10]
    )[0]
    
    return {
        "id": str(uuid4()),
        "edificio_id": edificio["id"],
        "numero": generar_numero_depto(piso, index_piso),
        "piso": piso,
        "tipo": "DEPARTAMENTO",
        "area": area,
        "dormitorios": dormitorios,
        "banios": banios,
        "balcon": balcon,
        "terraza": terraza,
        "amoblado": amoblado,
        "permite_mascotas": permite_mascotas,
        "valor_comercial": precio,
        "mantenimiento_mensual": mantenimiento,
        "estado": estado,
        "activa": True,
    }


def generar_departamentos_edificio(edificio: dict) -> list:
    """Genera todos los departamentos para un edificio"""
    departamentos = []
    num_pisos = edificio["num_pisos"]
    total_deptos = edificio["num_departamentos"]
    
    # Calcular departamentos por piso
    deptos_por_piso = total_deptos // num_pisos
    deptos_extra = total_deptos % num_pisos
    
    depto_count = 0
    for piso in range(1, num_pisos + 1):
        # Algunos pisos tienen 1 depto extra
        deptos_este_piso = deptos_por_piso + (1 if depto_count < deptos_extra else 0)
        
        for i in range(deptos_este_piso):
            if depto_count >= total_deptos:
                break
            depto = generar_departamento(edificio, piso, i)
            departamentos.append(depto)
            depto_count += 1
    
    return departamentos


# ============================================================================
# BASE DE DATOS
# ============================================================================

async def verificar_departamentos_existentes(conn, edificio_id: str) -> int:
    """Verifica cuántos departamentos tiene un edificio"""
    query = """
    SELECT COUNT(*) 
    FROM property_infrastructure.propiedad 
    WHERE edificio_id = $1
    """
    count = await conn.fetchval(query, edificio_id)
    return count


async def insertar_departamentos(conn, departamentos: list):
    """Inserta departamentos en batch"""
    query = """
    INSERT INTO property_infrastructure.propiedad (
        id, edificio_id, numero, piso, tipo, area,
        dormitorios, banios, balcon, terraza, amoblado,
        permite_mascotas, valor_comercial, mantenimiento_mensual,
        estado, activa
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15::property_infrastructure.estado_propiedad, $16
    )
    """
    
    # Preparar datos para inserción
    data = [
        (
            d["id"], d["edificio_id"], d["numero"], d["piso"],
            d["tipo"], d["area"], d["dormitorios"], d["banios"],
            d["balcon"], d["terraza"], d["amoblado"], d["permite_mascotas"],
            d["valor_comercial"], d["mantenimiento_mensual"],
            d["estado"], d["activa"]
        )
        for d in departamentos
    ]
    
    await conn.executemany(query, data)


# ============================================================================
# MAIN
# ============================================================================

async def main():
    print("\n" + "="*60)
    print("🏗️  GENERADOR DE PROPIEDADES")
    print("="*60)
    print(f"📊 Edificios a procesar: {len(EDIFICIOS)}")
    print(f"🎲 Seed: {SEED}")
    print(f"🔍 Modo: {'DRY RUN (sin insertar)' if DRY_RUN else 'PRODUCCIÓN'}")
    print("-"*60 + "\n")
    
    # Configurar seed para reproducibilidad
    random.seed(SEED)
    
    # Conectar a la base de datos
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Conectado a la base de datos\n")
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return
    
    total_insertados = 0
    edificios_skipped = 0
    
    try:
        for edificio in EDIFICIOS:
            print(f"🏢 Procesando: {edificio['nombre']} ({edificio['distrito']})")
            
            # Verificar si ya tiene departamentos
            count_existentes = await verificar_departamentos_existentes(conn, edificio["id"])
            
            if count_existentes > 0:
                print(f"   ⚠️  SKIP: Ya tiene {count_existentes} departamento(s)")
                print()
                edificios_skipped += 1
                continue
            
            # Generar departamentos
            print(f"   ✅ Edificio sin departamentos")
            print(f"   📝 Generando {edificio['num_departamentos']} departamentos...")
            
            departamentos = generar_departamentos_edificio(edificio)
            
            # Mostrar muestra
            print(f"   📋 Muestra (primeros 3):")
            for i, d in enumerate(departamentos[:3]):
                print(f"      {i+1}. Depto {d['numero']}: {d['area']}m², "
                      f"{d['dormitorios']} dorm, S/{d['valor_comercial']:,.0f}, "
                      f"{d['estado']}")
            
            if len(departamentos) > 3:
                print(f"      ... y {len(departamentos) - 3} más")
            
            # Insertar (o simular)
            if not DRY_RUN:
                await insertar_departamentos(conn, departamentos)
                print(f"   ✅ Insertados {len(departamentos)} departamentos")
                total_insertados += len(departamentos)
            else:
                print(f"   🔍 [DRY RUN] Se insertarían {len(departamentos)} departamentos")
            
            print()
        
        # Resumen final
        print("="*60)
        print("✅ COMPLETADO")
        print("-"*60)
        if not DRY_RUN:
            print(f"   Total insertado: {total_insertados} departamentos")
        else:
            print(f"   Total a insertar: {total_insertados} departamentos (DRY RUN)")
        print(f"   Edificios skipped: {edificios_skipped}")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()
        print("🔌 Conexión cerrada\n")


if __name__ == "__main__":
    asyncio.run(main())