
# scripts/backup_db.py
import asyncio
import os
import subprocess
import time
from datetime import datetime
from typing import Optional

import typer
from sqlalchemy import text

from app.core.config import settings, DatabaseType

app = typer.Typer()


@app.command()
def backup(
    output_dir: str = typer.Option("./backups", help="Directory to store backups"),
    compress: bool = typer.Option(True, help="Compress the backup file"),
):
    """Backup the database."""
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    
    if settings.DATABASE_TYPE == DatabaseType.POSTGRES:
        backup_file = f"{output_dir}/postgres_backup_{now}.sql"
        
        # Build pg_dump command
        cmd = [
            "pg_dump",
            f"--host={settings.POSTGRES_SERVER}",
            f"--port={settings.POSTGRES_PORT}",
            f"--username={settings.POSTGRES_USER}",
            f"--dbname={settings.POSTGRES_DB}",
            "--format=plain",
            f"--file={backup_file}",
        ]
        
        # Set password environment variable
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
        
        try:
            # Execute pg_dump
            subprocess.run(cmd, env=env, check=True)
            print(f"Backup created: {backup_file}")
            
            # Compress the backup if requested
            if compress:
                compressed_file = f"{backup_file}.gz"
                subprocess.run(["gzip", backup_file], check=True)
                print(f"Backup compressed: {compressed_file}")
        except subprocess.CalledProcessError as e:
            print(f"Backup failed: {e}")
    elif settings.DATABASE_TYPE == DatabaseType.ORACLE:
        backup_file = f"{output_dir}/oracle_backup_{now}.dmp"
        
        # Build expdp command
        cmd = [
            "expdp",
            f"{settings.ORACLE_USER}/{settings.ORACLE_PASSWORD}@{settings.ORACLE_SERVER}:{settings.ORACLE_PORT}/{settings.ORACLE_DB}",
            f"DIRECTORY=DATA_PUMP_DIR",
            f"DUMPFILE=backup_{now}.dmp",
            "SCHEMAS=app",
        ]
        
        try:
            # Execute expdp
            subprocess.run(cmd, check=True)
            
            # Copy the backup from the DATA_PUMP_DIR to the output directory
            cmd_copy = [
                "cp",
                f"/path/to/oracle/admin/{settings.ORACLE_DB}/dpdump/backup_{now}.dmp",
                backup_file,
            ]
            subprocess.run(cmd_copy, check=True)
            print(f"Backup created: {backup_file}")
            
            # Compress the backup if requested
            if compress:
                compressed_file = f"{backup_file}.gz"
                subprocess.run(["gzip", backup_file], check=True)
                print(f"Backup compressed: {compressed_file}")
        except subprocess.CalledProcessError as e:
            print(f"Backup failed: {e}")
    else:
        print(f"Unsupported database type: {settings.DATABASE_TYPE}")


@app.command()
def restore(
    backup_file: str = typer.Argument(..., help="Backup file to restore"),
    drop_existing: bool = typer.Option(False, help="Drop existing database before restore"),
):
    """Restore the database from a backup."""
    # Uncompress the backup file if it's compressed
    if backup_file.endswith(".gz"):
        uncompressed_file = backup_file[:-3]
        subprocess.run(["gunzip", "-c", backup_file, ">", uncompressed_file], shell=True, check=True)
        backup_file = uncompressed_file
    
    if settings.DATABASE_TYPE == DatabaseType.POSTGRES:
        # Build psql command
        cmd = [
            "psql",
            f"--host={settings.POSTGRES_SERVER}",
            f"--port={settings.POSTGRES_PORT}",
            f"--username={settings.POSTGRES_USER}",
            f"--dbname={settings.POSTGRES_DB}",
        ]
        
        # Set password environment variable
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
        
        try:
            # Drop existing database if requested
            if drop_existing:
                subprocess.run(
                    cmd + ["-c", f"DROP DATABASE IF EXISTS {settings.POSTGRES_DB}"],
                    env=env,
                    check=True,
                )
                subprocess.run(
                    cmd + ["-c", f"CREATE DATABASE {settings.POSTGRES_DB}"],
                    env=env,
                    check=True,
                )
                print(f"Database {settings.POSTGRES_DB} recreated")
            
            # Execute psql to restore
            subprocess.run(
                cmd + ["-f", backup_file],
                env=env,
                check=True,
            )
            print(f"Backup restored from: {backup_file}")
        except subprocess.CalledProcessError as e:
            print(f"Restore failed: {e}")
    elif settings.DATABASE_TYPE == DatabaseType.ORACLE:
        # Build impdp command
        cmd = [
            "impdp",
            f"{settings.ORACLE_USER}/{settings.ORACLE_PASSWORD}@{settings.ORACLE_SERVER}:{settings.ORACLE_PORT}/{settings.ORACLE_DB}",
            f"DIRECTORY=DATA_PUMP_DIR",
            f"DUMPFILE={os.path.basename(backup_file)}",
            "SCHEMAS=app",
        ]
        
        try:
            # Copy the backup to the DATA_PUMP_DIR
            cmd_copy = [
                "cp",
                backup_file,
                f"/path/to/oracle/admin/{settings.ORACLE_DB}/dpdump/{os.path.basename(backup_file)}",
            ]
            subprocess.run(cmd_copy, check=True)
            
            # Execute impdp
            subprocess.run(cmd, check=True)
            print(f"Backup restored from: {backup_file}")
        except subprocess.CalledProcessError as e:
            print(f"Restore failed: {e}")
    else:
        print(f"Unsupported database type: {settings.DATABASE_TYPE}")


@app.command()
def clear_db():
    """Clear all data in the database."""
    asyncio.run(_clear_db())


async def _clear_db():
    """Async implementation of clear_db."""
    from app.core.db import engine
    
    print("Clearing all data in the database...")
    
    async with engine.begin() as conn:
        if settings.DATABASE_TYPE == DatabaseType.POSTGRES:
            # Disable foreign key checks
            await conn.execute(text("SET session_replication_role = 'replica';"))
            
            # Truncate all tables
            await conn.execute(text("TRUNCATE TABLE item, \"user\" RESTART IDENTITY CASCADE;"))
            
            # Re-enable foreign key checks
            await conn.execute(text("SET session_replication_role = 'origin';"))
        elif settings.DATABASE_TYPE == DatabaseType.ORACLE:
            # Truncate all tables
            await conn.execute(text("TRUNCATE TABLE item"))
            await conn.execute(text("TRUNCATE TABLE \"user\""))
    
    print("Database cleared!")


if __name__ == "__main__":
    app()