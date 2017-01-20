from ts3plugin import ts3plugin
import ts3, ts3defines, os.path, binascii, re, shutil
from base64 import b64encode
from os import path
from PythonQt.QtGui import QFileDialog
from PythonQt.QtCore import Qt

class Avatargrabber(ts3plugin):
    name = "Avatargrabber"
    requestAutoload = False
    version = "1.0"
    apiVersion = 21
    author = "Luemmel"
    description = "Grab an avatar and save it."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    hotkeys = []
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 0, "Grab avatar", "scripts/avatargrabber/logo.png")]
    destination = None

    def __init__(self):
        ts3.printMessageToCurrentTab("Avatargrabber by [url=https://github.com/Metvernichter]Luemmel[/url] - Check out for updates and more!")

    def stop(self):
        ts3.printMessageToCurrentTab("Avatargrabber disabled!")

    def onMenuItemEvent(self, schid, a_type, menu_item_id, selected_item_id):
        if a_type == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT:
            if menu_item_id == 0: self.grab_avatar(schid, selected_item_id)

    def get_avatarpath(self, schid, clientid): # algorithm: http://yat.qa/ressourcen/definitionen-und-algorithmen/#avatars
        # check if selected client has an avatar
        (error, avatarflag) = ts3.getClientVariableAsString(schid, clientid, ts3defines.ClientPropertiesRare.CLIENT_FLAG_AVATAR)
        if avatarflag != "":
            (error, clientuid) = ts3.getClientVariableAsString(schid, clientid, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            clientuid = clientuid.split('=')[0]
            binary = ""
            # A - Z ===>> dez 0 - 25
            # a - z ===>> dez 26 - 51
            # 0 - 9 ===>> dez 52 - 61
            # +,/   ===>> dez 62, 63
            for i in range(0, len(clientuid)):
                character = ord(clientuid[i])
                if 97 <= character <= 122: character -= 71  # a-z
                elif 65 <= character <= 90: character -= 65 # A-Z
                elif 48 <= character <= 57: character += 4  # 0-9
                elif character == 43: character += 19       # +
                elif character == 47: character += 16       # /
                binary += '{0:06b}'.format(character)

            # convert to 6bit array
            binary = re.findall('....?', binary)
            filename = "avatar_"
            for bits in binary: filename += chr(int(bits, 2) + 97)  # convert 6bit to a-p

            # convert uid to base64 uid
            (error, suid) = ts3.getServerVariableAsString(schid, ts3defines.VirtualServerProperties.VIRTUALSERVER_UNIQUE_IDENTIFIER)
            suid = suid.encode('ascii')
            suid = b64encode(suid).decode("ascii")

            return path.join(ts3.getConfigPath(), "cache", suid, "clients", filename)   # return cache path
        return None # return None if client has no avatar

    def grab_avatar(self, schid, clientuid):
        directory = self.get_avatarpath(schid, clientuid)
        if directory:
            (error, nickname) = ts3.getClientVariableAsString(schid, clientuid, ts3defines.ClientProperties.CLIENT_NICKNAME)
            SaveFileDialog(self, nickname)
            if self.destination != "": shutil.copy2(directory, self.destination)

class SaveFileDialog(QFileDialog):
    def __init__(self, main, nickname, parent=None):
        main.destination = QFileDialog.getSaveFileName(self, 'Save avatar', os.path.expanduser("~")+"\\"+nickname+".gif", "Images (*.png *.jpg *.gif);;All files (*.*)", Qt.WA_DeleteOnClose)
