#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import logging
import subprocess

def main():
    """
    Run the BYOB setup script (Optimized for Render + Windows Clients)
    """
    
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)

    # 1. Поиск requirements.txt
    current_dir = os.path.dirname(os.path.abspath(__file__))
    req_path = None
    
    if os.path.exists(os.path.join(current_dir, 'requirements.txt')):
        req_path = os.path.join(current_dir, 'requirements.txt')
    elif os.path.exists(os.path.join(current_dir, 'byob', 'requirements.txt')):
        req_path = os.path.join(current_dir, 'byob', 'requirements.txt')

    if not req_path:
        logger.error("Could not find requirements.txt")
        sys.exit(1)

    # 2. Системные зависимости для Linux (Render) - OpenCV и т.д.
    if os.name != "nt":
        try:
            import apt
            aptcache = apt.Cache()
            if not aptcache['python3-opencv'].is_installed:
                subprocess.run(['sudo', 'apt-get', 'update'], check=True, capture_output=True)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'libgl1-mesa-glx', 'libglib2.0-0', 'libsm6', 'libxext6', 'libxrender-dev', 'libxcursor-dev', 'libxi-dev', 'libxtst-dev'], check=True, capture_output=True)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'python3-opencv'], check=True, capture_output=True)
        except ImportError:
            try:
                import yum
                # ... аналогично для RHEL (опционально)
            except ImportError:
                logger.info("System packages for OpenCV not found or already installed. Continuing...")

    # 3. Установка pip (если нужно)
    try:
        import pip
    except ImportError:
        if os.name != "nt":
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)

    # 4. Установка зависимостей из requirements.txt
    try:
        print("\n" + "="*50)
        print("Installing Python dependencies from: {}".format(req_path))
        print("="*50 + "\n")
        
        cmd = "{} -m pip install --upgrade -r {}".format(sys.executable, req_path)
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
