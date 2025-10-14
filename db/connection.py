"""
Gestor de conexiones a PostgreSQL usando asyncpg
"""
import asyncpg
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from models.settings import settings


class DatabaseManager:
    """Gestor de conexiones a PostgreSQL."""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.schema = settings.database_schema
    
    async def connect(self):
        """Crea el pool de conexiones a la base de datos."""
        if self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(
                    dsn=settings.database_url,
                    min_size=settings.db_pool_min_size,
                    max_size=settings.db_pool_max_size,
                    command_timeout=settings.db_command_timeout
                )
                print(f"✅ Pool de conexiones creado exitosamente")
                print(f"📊 Schema: {self.schema}")
            except Exception as e:
                print(f"❌ Error al conectar con la base de datos: {e}")
                raise
    
    async def disconnect(self):
        """Cierra el pool de conexiones."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            print("🔌 Pool de conexiones cerrado")
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager para obtener una conexión del pool."""
        if self.pool is None:
            await self.connect()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute_query(self, query: str, *args) -> str:
        """Ejecuta una query que no retorna resultados (INSERT, UPDATE, DELETE)."""
        async with self.get_connection() as conn:
            result = await conn.execute(query, *args)
            return result
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """Ejecuta una query y retorna todos los resultados como lista de dicts."""
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, *args)
            # Convertir asyncpg.Record a dict
            return [dict(row) for row in rows]
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Ejecuta una query y retorna un solo resultado como dict."""
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetch_val(self, query: str, *args) -> Any:
        """Ejecuta una query y retorna un solo valor."""
        async with self.get_connection() as conn:
            value = await conn.fetchval(query, *args)
            return value
    
    async def get_schema_info(self) -> str:
        """Obtiene información del schema de property_infrastructure."""
        query = f"""
        SELECT 
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = '{self.schema}'
        AND table_name IN ('propiedad', 'edificio')
        ORDER BY table_name, ordinal_position;
        """
        
        try:
            rows = await self.fetch_all(query)
            
            # Formatear como texto legible
            schema_info = f"Database Schema: {self.schema}\n\n"
            
            current_table = None
            for row in rows:
                if row['table_name'] != current_table:
                    current_table = row['table_name']
                    schema_info += f"\nTable: {current_table}\n"
                    schema_info += "-" * 50 + "\n"
                
                nullable = "NULL" if row['is_nullable'] == 'YES' else "NOT NULL"
                schema_info += f"  {row['column_name']}: {row['data_type']} ({nullable})\n"
            
            return schema_info
            
        except Exception as e:
            return f"Error getting schema: {e}"
    
    async def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos."""
        try:
            version = await self.fetch_val("SELECT version()")
            print(f"✅ Conexión exitosa a PostgreSQL")
            print(f"📊 Versión: {version[:50]}...")
            return True
        except Exception as e:
            print(f"❌ Error en prueba de conexión: {e}")
            return False


# Instancia global del gestor de base de datos
db = DatabaseManager()