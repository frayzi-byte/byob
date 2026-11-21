#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import logging
import subprocess

def main():
    """
    Run the BYOB setup script (Optimized for Render and Local Use)
    """
    
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)

    # 1. Определение пути к requirements.txt
    # Ищем файл в текущей директории или в подпапке 'byob'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    req_path = None
    
    # Путь 1: В корне проекта (рядом с setup.py)
    potential_req_1 = os.path.join(current_dir, 'requirements.txt')
    if os.path.exists(potential_req_1):
        req_path = potential_req_1
        logger.info(f"Found requirements.txt at: {potential_req_1}")
    
    # Путь 2: В подпапке byob (если файл перенесен туда)
    if not req_path:
        byob_dir = os.path.join(current_dir, 'byob')
        potential_req_2 = os.path.join(byob_dir, 'requirements.txt')
        if os.path.exists(potential_req_2):
            req_path = potential_req_2
            logger.info(f"Found requirements.txt in subfolder: {potential_req_2}")

    if not req_path:
        logger.error("Could not find requirements.txt in current dir or byob subfolder")
        sys.exit(1)

    # 2. Проверка и установка системных зависимостей (для Linux/Mac)
    if os.name != "nt":
        logger.info("Checking system dependencies for OpenCV...")
        try:
            import apt
            aptcache = apt.Cache()
            if not aptcache['python3-opencv'].is_installed:
                # Пытаемся установить автоматически (работает на Render, где root)
                subprocess.run(['sudo', 'apt-get', 'update'], check=True, capture_output=True)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'python3-opencv'], check=True, capture_output=True)
                logger.info("Installed python3-opencv via apt.")
        except ImportError:
            try:
                import yum
                yumapp = yum.YumBase()
                rpmdb = yumapp.doPackageLists(patterns="python3-opencv")
                if not rpmdb.installed:
                    subprocess.run(['sudo', 'yum', 'install', '-y', 'python3-opencv'], check=True, capture_output=True)
            except ImportError:
                logger.info("System package manager (apt/yum) not found or OpenCV already installed. Continuing...")

    # 3. Поиск и установка pip (если нужно)
    try:
        import pip
        logger.debug("pip module is available.")
    except ImportError:
        logger.info("Installing pip...")
        if os.name != "nt":
            # На Linux часто нужен sudo, но на Render обычно root
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
            except Exception as e:
                logger.warning(f"Failed to upgrade pip automatically: {e}. Continuing...")

    # 4. Установка зависимостей из requirements.txt
    try:
        print("\n" + "="*50)
        print("Installing Python dependencies from: {}".format(req_path))
        print("="*50 + "\n")
        
        cmd = "{} -m pip install --upgrade -r {}".format(sys.executable, req_path)
        
        # Запуск установки с выводом в консоль
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        
        if result.returncode == 0:
            logger.info("Dependencies installed successfully!")
        else:
            logger.error(f"Error installing dependencies:\n{result.stderr}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error during installation: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
