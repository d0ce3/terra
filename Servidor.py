import os
import sys
import json
import time
import subprocess
from cryptography.fernet import Fernet

# ================================================================
# CONFIGURACIÓN SEGURA (WEBHOOK + TOKEN)
# ================================================================
class SecureConfig:
    def __init__(self):
        self.key_file = "terraria.key"
        self.config_file = "terraria_config.enc"
        self._generate_key()
        
    def _generate_key(self):
        if not os.path.exists(self.key_file):
            with open(self.key_file, "wb") as f:
                f.write(Fernet.generate_key())
                
    def _get_cipher(self):
        return Fernet(open(self.key_file, "rb").read())
    
    def save_config(self, data):
        encrypted = self._get_cipher().encrypt(json.dumps(data).encode())
        with open(self.config_file, "wb") as f:
            f.write(encrypted)
    
    def load_config(self):
        try:
            return json.loads(self._get_cipher().decrypt(open(self.config_file, "rb").read()).decode())
        except:
            return {"webhook": "", "token": ""}

# ================================================================
# GESTIÓN COMPLETA DEL SERVIDOR
# ================================================================
class TerrariaManager:
    def __init__(self):
        self.config = SecureConfig().load_config()
        self.terraria_bin = "/workspaces/terra/terraria-server/1449/Linux/TerrariaServer.bin.x86_64"
        self.worlds_dir = "/workspaces/terra/terraria-server/Worlds"
        
    def mostrar_menu_principal(self):
        os.system('clear')
        print("""
[1] Iniciar Servidor
[2] Configuración
[3] Salir""")
        return input("\n➤ Selección: ")
    
    def mostrar_menu_config(self):
        os.system('clear')
        print("""
=== CONFIGURACIÓN ===
[1] Modificar Webhook
[2] Modificar Token Bot
[3] Eliminar Mundo
[4] Volver""")
        return input("\n➤ Selección: ")
    
    def iniciar_servidor(self):
        # Verificar configuración
        if not self.config["webhook"]:
            input("⚠️ Configura el webhook primero (Enter para continuar)")
            return
            
        # Iniciar servicios
        playit_proc = subprocess.Popen(["playit"], stdout=subprocess.DEVNULL)
        terraria_proc = subprocess.Popen(
            [self.terraria_bin, "-ip", "0.0.0.0", "-port", "7777"],
            stdin=sys.stdin,
            stdout=sys.stdout
        )
        
        # Mantener servicios activos
        try:
            terraria_proc.wait()
        except KeyboardInterrupt:
            pass
        finally:
            playit_proc.terminate()
    
    def eliminar_mundo(self):
        mundos = [f for f in os.listdir(self.worlds_dir) if f.endswith(".wld")]
        if not mundos:
            input("❌ No hay mundos para eliminar")
            return
            
        print("\nMundos disponibles:")
        for i, mundo in enumerate(mundos, 1):
            print(f"[{i}] {mundo}")
            
        try:
            seleccion = int(input("\n➤ Número del mundo a eliminar: ")) - 1
            os.remove(os.path.join(self.worlds_dir, mundos[seleccion]))
            input("✅ Mundo eliminado correctamente")
        except:
            input("❌ Selección inválida")

# ================================================================
# EJECUCIÓN PRINCIPAL
# ================================================================
if __name__ == "__main__":
    manager = TerrariaManager()
    config_manager = SecureConfig()
    
    while True:
        opcion = manager.mostrar_menu_principal()
        
        if opcion == "1":  # Iniciar servidor
            manager.iniciar_servidor()
            
        elif opcion == "2":  # Menú configuración
            while True:
                sub_opcion = manager.mostrar_menu_config()
                
                if sub_opcion == "1":  # Webhook
                    nuevo_webhook = input("\n🔗 Nuevo webhook: ")
                    manager.config["webhook"] = nuevo_webhook
                    config_manager.save_config(manager.config)
                    
                elif sub_opcion == "2":  # Token Bot
                    nuevo_token = input("\n🤖 Nuevo token: ")
                    manager.config["token"] = nuevo_token
                    config_manager.save_config(manager.config)
                    
                elif sub_opcion == "3":  # Eliminar mundo
                    manager.eliminar_mundo()
                    
                elif sub_opcion == "4":
                    break
                    
        elif opcion == "3":
            print("\n¡Hasta pronto! 🎮")
            sys.exit()