<div align="center">

<h1 align="center">🖥️ WinScreen</h1>
<p align="center"><b>L'alternative moderne et libre pour la capture Windows</b></p>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3.9+-00ff41?style=for-the-badge&logo=python" alt="Python Version">
    <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License MIT">
    <img src="https://img.shields.io/badge/UI-CustomTkinter-orange?style=for-the-badge" alt="UI CustomTkinter">
</p>

<hr>

<p align="center">
  <i>Développé pour pallier les limitations de l'outil système, notamment sur les versions de Windows non activées.<br>Votre matériel, vos règles.</i>
</p>

</div>

<h2>✨ Caractéristiques</h2>

<table width="100%">
  <tr>
    <td width="25%" align="center"><b>📸 Capture Rapide</b></td>
    <td width="25%" align="center"><b>🎥 Vidéo</b></td>
    <td width="25%" align="center"><b>🎨 Interface Cyber</b></td>
    <td width="25%" align="center"><b>🆓 Zéro Restriction</b></td>
  </tr>
  <tr>
    <td align="center">Screenshots instantanés sans latence via <i>mss</i>.</td>
    <td align="center">Enregistrez votre activité en haute fluidité.</td>
    <td align="center">Design moderne sombre via <i>CustomTkinter</i>.</td>
    <td align="center">Fonctionne sans Windows activé.</td>
  </tr>
</table>

<h2>🛠️ Installation & Prérequis</h2>

<h3>1. Prérequis Système</h3>
<ul>
    <li><b>OS</b> : Windows 10 / 11</li>
    <li><b>Python</b> : 3.9 ou supérieur</li>
</ul>

<h3>2. Dépendances requises</h3>
<table width="100%">
    <thead>
        <tr>
            <th align="left">Librairie</th>
            <th align="left">Utilité</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>customtkinter</code></td>
            <td>Interface utilisateur moderne et réactive.</td>
        </tr>
        <tr>
            <td><code>Pillow</code></td>
            <td>Traitement et sauvegarde des images.</td>
        </tr>
        <tr>
            <td><code>mss</code></td>
            <td>Capture d'écran haute performance (multi-écrans).</td>
        </tr>
        <tr>
            <td><code>pywin32</code></td>
            <td>Interaction avec les API natives de Windows.</td>
        </tr>
    </tbody>
</table>

<h3>3. Installation Rapide</h3>
<p>Copiez et collez ces commandes dans votre terminal :</p>

<pre><code># Cloner le projet
git clone https://github.com/votre-utilisateur/winscreen.git

# Entrer dans le dossier
cd winscreen

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py</code></pre>

<hr>

<h2>🚀 Utilisation</h2>
<ol>
    <li><b>Lancement</b> : Exécutez <code>main.py</code>.</li>
    <li><b>Sélection</b> : Choisissez entre le mode <b>Image</b> ou <b>Vidéo</b>.</li>
    <li><b>Capture</b> : Définissez votre zone de capture à la souris.</li>
    <li><b>Stockage</b> : Retrouvez vos fichiers dans le dossier <code>data/captures/</code>.</li>
</ol>

<br>

<div align="center">
    <hr>
    <p><i>WinScreen &copy; 2026 - Développé avec passion pour la liberté logicielle.</i></p>
</div>
