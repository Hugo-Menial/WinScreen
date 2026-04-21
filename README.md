import os

# Contenu HTML de la présentation WinScreen
html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WinScreen - Documentation Officielle</title>
    <style>
        :root {
            --primary: #00ff41; /* Vert Matrix/Cyber */
            --bg: #0a0a0a;
            --card-bg: #161616;
            --text: #e0e0e0;
            --accent: #008f11;
        }

        body {
            background-color: var(--bg);
            color: var(--text);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }

        header {
            background: linear-gradient(180deg, #111 0%, var(--bg) 100%);
            padding: 60px 20px;
            text-align: center;
            border-bottom: 2px solid var(--primary);
        }

        .logo {
            font-size: 3rem;
            font-weight: bold;
            color: var(--primary);
            text-transform: uppercase;
            letter-spacing: 5px;
            text-shadow: 0 0 15px var(--primary);
        }

        .container {
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
        }

        .badge {
            background: var(--card-bg);
            border: 1px solid var(--primary);
            color: var(--primary);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin-bottom: 20px;
            display: inline-block;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }

        .card {
            background: var(--card-bg);
            padding: 25px;
            border-radius: 10px;
            border-left: 4px solid var(--accent);
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            border-left-color: var(--primary);
        }

        h2 { color: var(--primary); border-bottom: 1px solid #333; padding-bottom: 10px; }
        
        pre {
            background: #000;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border: 1px solid #333;
            color: #00ff41;
        }

        code { font-family: 'Consolas', monospace; }

        .footer {
            text-align: center;
            padding: 40px;
            font-size: 0.8rem;
            color: #666;
        }

        .highlight { color: var(--primary); font-weight: bold; }
    </style>
</head>
<body>

<header>
    <div class="logo">WinScreen</div>
    <p>L'alternative ultime à l'outil de capture Windows</p>
    <div class="badge">Version 1.0.0 - Python Powered</div>
</header>

<div class="container">
    <section>
        <h2>À propos de WinScreen</h2>
        <p>
            <span class="highlight">WinScreen</span> a été conçu pour briser les limitations imposées par Microsoft. 
            Que vous utilisiez une version de Windows non activée ou que vous cherchiez simplement un outil plus rapide, 
            WinScreen offre une suite complète de capture d'écran et d'enregistrement vidéo sans aucune restriction.
        </p>
    </section>

    <div class="grid">
        <div class="card">
            <h3>Capture Immédiate</h3>
            <p>Utilise la technologie <code>mss</code> pour des snapshots en quelques millisecondes, même en multi-écrans.</p>
        </div>
        <div class="card">
            <h3>Enregistrement Vidéo</h3>
            <p>Capturez votre flux de travail en haute qualité pour vos rapports d'audit ou tutoriels.</p>
        </div>
        <div class="card">
            <h3>Interface Custom</h3>
            <p>Une UI moderne basée sur <code>CustomTkinter</code> pour une expérience utilisateur fluide et sombre.</p>
        </div>
    </div>

    <section style="margin-top: 50px;">
        <h2>Installation</h2>
        <p>Installez les dépendances via le terminal :</p>
        <pre><code>pip install customtkinter Pillow mss pywin32</code></pre>
    </section>

    <section>
        <h2>Spécifications Techniques</h2>
        <ul>
            <li><strong>Backend :</strong> Python 3.9+</li>
            <li><strong>Capture :</strong> MSS (Multiple Screen Shot)</li>
            <li><strong>Traitement Image :</strong> Pillow (PIL)</li>
            <li><strong>OS :</strong> Windows 10 / 11 (Optimisé pour Win32)</li>
        </ul>
    </section>
</div>

<div class="footer">
    WinScreen &copy; 2024 - Développé pour la liberté logicielle.
</div>

</body>
</html>
"""

# Sauvegarde du fichier
with open("WinScreen_Presentation.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Fichier 'WinScreen_Presentation.html' généré avec succès.")
